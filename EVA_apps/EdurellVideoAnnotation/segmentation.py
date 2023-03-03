from dataclasses import dataclass
from bisect import insort_left
from words import TextSimilarityClassifier, ComparisonMethod
from typing_extensions import Literal
from typing import List,Tuple

@dataclass
class TimedAndFramedText:
    text: str
    start_end_frames: List[Tuple[(int,int)]]
    xywh: Tuple[(int,int,int,int)]

    def clean_copy(self,txt_cleaner: TextSimilarityClassifier) -> 'TimedAndFramedText':
        return TimedAndFramedText(txt_cleaner.clean_text(self.text),self.start_end_frames,self.xywh)
    
    def merge_adjacent_startend_frames(self,max_dist:int=15) -> 'TimedAndFramedText':
        '''
        Merges adjacent (within a tolerance of frames) frame times a TimedAndFramedText structure
        '''
        start_end_frames = self.start_end_frames
        merged_start_end_frames = []
        curr_start,curr_end = start_end_frames[0]
        for new_start,new_end in start_end_frames:
            if new_start-curr_end <= max_dist:
                curr_end = max(curr_end,new_end)
            else:
                merged_start_end_frames.append((curr_start,curr_end))
                curr_start = new_start
                curr_end = new_end
        merged_start_end_frames.append((curr_start,curr_end))
        self.start_end_frames = merged_start_end_frames
        return self
    
    def extend_frames(self, other_start_end_list:List[Tuple[(int,int)]]) -> None:
        for other_start_end_elem in other_start_end_list:
            insort_left(self.start_end_frames,other_start_end_elem)
    
    def extend_text_and_bounding_boxes(self, other_text:str,other_xywh:Tuple[int,int,int,int]) -> None:
        this_is_prev = self.xywh[1] < other_xywh[1]
        this_text = self.text
        this_xywh = self.xywh
        if this_is_prev:    self.text = this_text + '\n' + other_text
        else:               self.text = other_text + '\n' + this_text
        self.xywh = (   min(this_xywh[0],other_xywh[0]), 
                        min(this_xywh[1],other_xywh[1]), 
                        max(this_xywh[2],other_xywh[2]),
                        max(this_xywh[3],other_xywh[3]) )


    def is_partial_text_of(self, other:'TimedAndFramedText',text_classifier:TextSimilarityClassifier):
        if other is not None:
            this_startend_frames = self.start_end_frames
            other_startend_frames = other.start_end_frames
            return text_classifier.is_partially_in( self.text,
                                                    other.text,
                                                    (this_startend_frames[0][0],this_startend_frames[-1][1]),
                                                    (other_startend_frames[0][0],other_startend_frames[-1][1]),
                                                    self.xywh,
                                                    other.xywh)
        return False

    def __lt__(self, other:'TimedAndFramedText'):
        return self.start_end_frames[0][0] < other.start_end_frames[0][0]
    
    def __repr__(self) -> str:
        return 'TimedAndFramedText(txt={0}, start_end_arr={1}, xywh={2})'.format(
            repr(self.text),repr(self.start_end_frames),repr(self.xywh))


from nltk import tokenize
import db_mongo

#################################################################################
# Issue with online server (incompatibility with gunicorn)
# Edited import to fix issue: (https://github.com/chrisspen/punctuator2/issues/3)
import sys
incompatible_path = '/home/anaconda3/envs/myenv/bin'
if incompatible_path in sys.path:
    sys.path.remove(incompatible_path)
from punctuator import Punctuator
#################################################################################

from sentence_transformers import SentenceTransformer
from Cluster import create_cluster_list, aggregate_short_clusters
from audio_transcription import get_timed_sentences
import os, sys
from conll import get_text

# from lexrank import LexRank
# from lexrank.mappings.stopwords import STOPWORDS

# riassunto con bert
# from summary import LectureEnsembler

'''
variables to consider:
    * punctuator net,
    * bert model,
    * cosine similarity threshold - c_threshold,
    * summary model - bert vs sumy,
    * min time to merge short clusters,
    * add_sentence vs deprecated,
    * color_histogram threshold and frame range,
'''

#video_quello_corto = "https://www.youtube.com/watch?v=qgCvnogeN2s"
#video_quello_medio = "https://www.youtube.com/watch?v=0K2qhSTrXtE&ab_channel=DocSpotDocSpo"
#video_quello_lungo = "https://www.youtube.com/watch?v=DHXwC0xt1hk&t"
#video_quello_indexato = "https://www.youtube.com/watch?v=URtsnESYcPk&ab_channel=DerekBanas"

#mooc_intro = "https://www.youtube.com/watch?v=KuMRk-arGAk&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV"
#mooc_1 = "https://www.youtube.com/watch?v=sXLhYStO0m8&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=2"
#mooc_2 = "https://www.youtube.com/watch?v=g8w-IKUFoSU&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=3"
#mooc_3 = "https://www.youtube.com/watch?v=D4PGqxGWCT0&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=4"
#mooc_4 = "https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5"
#mooc_5 = "https://www.youtube.com/watch?v=wbqpzILKENI&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=6"

#mooc = mooc_1

from inspect import getfile
import cv2

from youtube_transcript_api import YouTubeTranscriptApi as YTTranscriptApi
from math import floor, ceil
from numpy import clip, all, array, empty, average, var, zeros, where
from image import ImageClassifier, ColorScheme, draw_bounding_boxes_on_image
from pprint import pprint
from xgboost_model import XGBoostModelAdapter
from collections import deque
from video import VideoSpeedManager, LocalVideo
from matplotlib import pyplot as plt
import time
from itertools_extension import double_iterator, pairwise_linked_iterator
from collections_extension import LiFoStack


class VideoAnalyzer:

    _text_in_video: List[TimedAndFramedText] or None = None
    _video_slidishness = None

    def __init__(self,video_id:str,from_youtube:bool=True) -> None:
        if from_youtube:
            self._video_id = video_id
        else:
            raise Exception("not implemented!")
    
    def create_keyframes(self,start_times,end_times,S,seconds_range, image_scale:float=0.5):
        """
        Take a list of clusters and compute the color histogram on end and start of the cluster
        
        Parameters
        ----------
        cluster_list :
        S : scala per color histogram
        seconds_range : aggiustare inizio e fine dei segmenti in base a differenza nel color histogram
        """
        assert len(start_times) == len(end_times)
        vsm = VideoSpeedManager(self._video_id,output_colors=ColorScheme.RGB)
        vid_ref = vsm.vid_ref
        vidcap = vid_ref._vidcap
        start_end_frames = [(vid_ref.get_num_frame_from_time(s_time),vid_ref.get_num_frame_from_time(e_time)) 
                                for s_time,e_time in zip(start_times,end_times)]

        curr_num_frame = 0
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, curr_num_frame)
        has_frame,curr_frame = vidcap.read()
        next_frame_offset = 10*vid_ref.get_fps()
        summation = 0
        prev_hist = []
        all_diffs = []
        while has_frame:
            curr_frame = cv2.resize(curr_frame,(240,180))
            image = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY)
            hist = cv2.calcHist([image], [0], None, [32], [0, 128])
            hist = cv2.normalize(hist, hist)
            
            if curr_num_frame > 0 :
                diff = 0
                for i, bin in enumerate(hist):
                    diff += abs(bin[0] - prev_hist[i][0])
                all_diffs.append(diff)
                summation += diff
            
            curr_num_frame += next_frame_offset
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, curr_num_frame)
            has_frame,curr_frame = vidcap.read()
            prev_hist = hist

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        threshold = S * (summation / curr_num_frame)

        '''
        Controllo se c'è un cambio scena in un intorno di "seconds_range" frames dalla fine ed inizio di ciascun cluster.
        '''

        #start_changes = []
        #end_changes = []
        fps = vid_ref.get_fps()

        for j,(start_f,end_f) in enumerate(start_end_frames):
            changes_found = [False,False]
            for i in range(seconds_range):
                diffs = [int(start_f / next_frame_offset),int(end_f / next_frame_offset)]
                if not changes_found[0] and diffs[0] + i < len(all_diffs) and all_diffs[diffs[0] + i] > threshold:
                    sec = (start_f + i) / fps
                    start_times[j] = round(sec,2)
                    changes_found[0] = True
                
                if not changes_found[1] and diffs[1] + i < len(all_diffs) and all_diffs[diffs[1] + i] > threshold:
                    sec = (end_f + i) / fps
                    end_times[j] = round(sec,2)
                    changes_found[1] = True

                if all(changes_found): break

        # salvo immagini da mostrare nella timeline
        
        images_path = []
        for i, start_end in enumerate(start_end_frames):

            vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_end[0])
            ret, image = vidcap.read()
            assert ret
            image = cv2.resize(image,(array([image.shape[1],image.shape[0]],dtype='f')*image_scale).astype(int))
            current_path = os.path.dirname(os.path.abspath(__file__))
            image_name = str(i) #str(cluster_starts[i]).replace(".","_")

            saving_position = os.path.join(current_path, "static", "videos", self._video_id, image_name + ".jpg")
            #print(saving_position)
            #saving_position = "videos\\" + video_id + "\\" + str(start) + ".jpg"
            cv2.imwrite(saving_position, image)
            images_path.append("videos/" + self._video_id + "/" + image_name + ".jpg")

        vsm.close()
        #print(images_path)
        ''' Ritorno le path delle immagini della timeline'''
        return images_path, start_times, end_times

    def get_transcript(self,lang:str='en'):
        transcripts = YTTranscriptApi.list_transcripts(self._video_id)
        autogenerated = False
        try:
            transcript = transcripts.find_manually_created_transcript([lang])
        except:
            transcript = transcripts.find_generated_transcript([lang])
            autogenerated = True

        subs_dict = []
        for sub in transcript.fetch():

            subs_dict.append(
                {"text": sub["text"],
                 "start": sub["start"],
                 "end": sub["start"] + sub["duration"]}
            )

        return subs_dict, autogenerated

    def is_slide_video(self,threshold:float=0.5):
        if self._video_slidishness is None:
            self._extract_analysis_frames_and_estimate_threshold(   vsm=VideoSpeedManager(self._video_id,ColorScheme.RGB),
                                                                    num_segments=50,
                                                                    _debug=False    )
        self._video_slidishness:float
        return self._video_slidishness > threshold

    def _set_video_slidishness(self,slidish_frames: List[Tuple[int,int]],num_frames:int):
        counter:float = 0.0
        for frame_window in slidish_frames:
            counter += (frame_window[1] - frame_window[0])
        self._video_slidishness = counter/(num_frames-1)

    def _extract_analysis_frames_and_estimate_threshold(self, vsm:VideoSpeedManager,num_segments:int=150,_debug=True):
        '''
        Split the video into `num_segments` windows frames, for every segment it's taken the frame that's far enough to guarantee a minimum sensibility\n
        The current frame is analyzed by XGBoost model to recognize the scene\n
        If there are two non-slide frames consecutively the resulting frame window is cut\n
        Bounds are both upper and lower inclusive to avoid a miss as much as possible\n
        Then both are compared in terms of cosine distance of their histograms (it's faster than flattening the images)\n\n
        Lastly the per-frame-cosine-distance is selected as the average of all + the variance for a small boost, all clipped to prevent 1 or too small values

        ----------
        Example
        ----------
        A video split into 10 segments:\n\n
        slide_segments : 0,1,3,6,9,10\n
        non_slide_segments : 2,4,5,7,8\n
        results in segmentation = [(0,4),(5,7)(8,10)]\n
        with holes between segments 4-5 and 7-8
        '''
        num_frames = vsm.get_video().get_count_frames()
        speed = floor(num_frames / (num_segments))
        vsm.lock_speed(speed)
        iterations_counter:int = 0
        #cos_sim_values = empty((num_segments,vsm.get_video().get_dim_frame()[2]))
        dists = empty((num_segments,vsm.get_video().get_dim_frame()[2]))


        # Optimization is performed by doing a first coarse-grained analysis with the XGBoost model predictor
        # then set those windows inside the VideoSpeedManager
        scene_model = XGBoostModelAdapter(os.path.dirname(os.path.realpath(__file__))+"/xgboost/model/xgboost500.sav")

        start_frame_num = None
        frames_to_analyze = []
        answ_queue = deque([False,False])
        curr_frame = ImageClassifier(image_and_scheme=[None,vsm._color_scheme])
        prev_frame = curr_frame.copy()
        while iterations_counter < num_segments:
            prev_frame.set_img(vsm.get_frame())
            curr_frame.set_img(vsm.get_following_frame())
            answ_queue.appendleft(scene_model.is_enough_slidish_like(prev_frame)); answ_queue.pop()

            # if there's more than 1 True discontinuity -> cut the video
            if any(answ_queue) and start_frame_num is None:
                start_frame_num = iterations_counter*speed
            elif not any(answ_queue) and start_frame_num is not None:
                frames_to_analyze.append((start_frame_num,iterations_counter*speed))
                start_frame_num = None

            #cos_sim_values[iterations_counter,:] = prev_frame.get_cosine_similarity(curr_frame)
            dists[iterations_counter,:] = curr_frame.get_mean_distance(prev_frame)
            iterations_counter+=1
            #print(answ_queue[0]);plt.imshow(curr_frame.get_img(),cmap='gray');plt.show()
            #print(f" Estimating cosine_similarity_threshold: {ceil((iterations_counter)/num_segments * 100)}%",end='\r')
            if _debug: print(f" Coarse-grained analysis percentage: {ceil((iterations_counter)/num_segments * 100)}%",end='\r')
        
        if start_frame_num is not None:
            frames_to_analyze.append((start_frame_num,num_frames-1))
        #cos_sim_img_threshold = clip(average(cos_sim_values,axis=0),0.9,0.99999)
        #   can't estimate corretly the cosine similarity threshold with average, too dependant from the segments chosen and also too low
        #   neither can set to max because it's almost always the highest
        #cos_sim_img_threshold = clip(cos_sim_values.min(axis=0),0.9,0.99999)
        #diff_threshold = average(diffs,axis=0)+3*var(diffs,axis=0)
        dist_threshold = (dists.max(axis=0) - dists.min(axis=0)) / 2
        #print(f"Estimated cosine_similarity_threshold: {cos_sim_img_threshold}")
        if _debug:
            print(f"Estimated mean_dist_threshold: {dist_threshold}")
            print(f"Frames to analyze: {frames_to_analyze} of {num_frames} total frames")
        frames_to_analyze.sort(reverse=True)
        #return cos_sim_img_threshold, frames_to_analyze
        self._set_video_slidishness(frames_to_analyze,num_frames)
        return dist_threshold, frames_to_analyze

    def _compact_embedding_partial_words(self,TFT_list:'list[TimedAndFramedText]',text_classifier:TextSimilarityClassifier,frames_max_dist:int):
        '''
        Merge near TimedAndFramedText elements of the list\n
        Goes in both directions reversing the array and lastly iterates over all the elements with an (optimized) nested for loop\n

        ----------
        Parameters
        ----------
        TFT_list : list of texts
        text_classifier : utility class for text similarity comparison used by TimedAndFramedText for finding partial texts
        
        Returns
        -------
        Same length or shorter list with elements merged
        '''
        input_list = TFT_list
        elem1:TimedAndFramedText
        elem2:TimedAndFramedText
        for _reverse in [False, True]:
            output_list:'list[TimedAndFramedText]' = []
            for elem1, elem2 in pairwise_linked_iterator(input_list,reversed=_reverse):
                if elem1.is_partial_text_of(elem2,text_classifier): elem2.extend_frames(elem1.start_end_frames)
                else: output_list.append(elem1)
            input_list = output_list

        deleted:'list[int]' = []
        for i1,i2, elem1,elem2 in double_iterator(input_list,enumerated=True):
            if not i1 in deleted and not i2 in deleted and elem1.is_partial_text_of(elem2,text_classifier):
                elem2.extend_frames(elem1.start_end_frames)
                deleted.append(i1)
        return sorted([elem.merge_adjacent_startend_frames(max_dist=frames_max_dist) for indx, elem in enumerate(input_list) if not indx in deleted])

    def _compact_embedding_same_frames(self,TFT_list:'list[TimedAndFramedText]',text_classifier:TextSimilarityClassifier):
        deleted:'list[int]' = []
        elem1:TimedAndFramedText
        elem2:TimedAndFramedText
        for i1,i2, elem1,elem2 in double_iterator(TFT_list,enumerated=True):
            if not i1 in deleted and not i2 in deleted and elem1.is_partial_text_of(elem2,text_classifier):
                elem2.extend_text_and_bounding_boxes(elem1.text,elem1.xywh)
                deleted.append(i1)
        return sorted([elem for indx, elem in enumerate(TFT_list) if not indx in deleted])

    def extract_text_from_video(self,color_scheme_for_analysis:ColorScheme=ColorScheme.BGR,_debug:bool=False):
        '''
        Firstly the video is analized in coarse-grained way, by a ML model to recognize frames of slides
        and the threshold for the difference between two frames is concurrently estimated. \n
        The method uses an ImageClassifier to detect text in the frames of the video
        Then saves that text in a collision stack.\n
        It then looks for changes in the collision stack with respect to the text in the current frame
        flushes the differences in the output list.\n
        Finally, it calls two helper methods to clean up the output list by combining partial words and merging adjacent frames.
        '''
        start_time = time.time()   

        vsm = VideoSpeedManager(self._video_id,color_scheme_for_analysis)
        img_threshold, frames_to_analyze = self._extract_analysis_frames_and_estimate_threshold(vsm)
        vsm.reset()
        if frames_to_analyze is None:
            return []
        #frames_to_analyze = [(0,3000)]
        curr_frame = ImageClassifier(   threshold = img_threshold,
                                        comp_method = 'mean-abs-diff',
                                        image_and_scheme = [None,color_scheme_for_analysis]   )
        prev_frame = curr_frame.copy()

        output_TFT_stack:LiFoStack[TimedAndFramedText] = LiFoStack()
        iterations_counter:int = 0
        #max_speed:int = 0
        collisions_TFT_list:'list[TimedAndFramedText]' = []
        txt_classif = TextSimilarityClassifier(comp_methods=[ComparisonMethod.TXT_LEN,ComparisonMethod.TXT_SIM])
        #vsm.lock_speed()
        if not (len(frames_to_analyze) == 1 and frames_to_analyze[0][0] == 0 and frames_to_analyze[0][1] == vsm.get_video().get_count_frames()-1):
            vsm.set_analysis_frames(frames_to_analyze)

        while not vsm.is_video_ended():
        
            curr_frame.set_img(vsm.get_frame())

            #   collide() function sets the speed cap of the video to the minimum and returns the num frame of the first frame with text within this the last iteration

            #   if collision stack is empty search for text in the current frame and then put it in the stack
            if len(collisions_TFT_list) == 0 and curr_frame.detect_text():
                num_start_frame = vsm.collide_and_get_fixed_num_frame()
                curr_frame.set_img(vsm.get_frame_from_num(num_start_frame))
                texts_with_cnt = curr_frame.detect_text(return_text=True,with_contours=True)
                for text,xywh in texts_with_cnt:
                    collisions_TFT_list.append(
                        TimedAndFramedText( text=text,
                                            start_end_frames=[(num_start_frame,-1)],
                                            xywh=xywh))

            #   otherwise put the text not visible any more in the output stack
            elif len(collisions_TFT_list) > 0 and \
                    (not curr_frame.is_similar_to(prev_frame) or vsm.is_video_ended()):
                
                coll_TFT_stack_mask = zeros(len(collisions_TFT_list,),dtype=bool)
                #   create a mask for the text that's still on screen
                if not vsm.is_video_ended():
                    texts_with_cnt = curr_frame.detect_text(return_text=True,with_contours=True)
                    for text,_ in texts_with_cnt:
                        for indx_in_stack, coll_elem in enumerate(collisions_TFT_list):
                            if text == coll_elem.text:
                                coll_TFT_stack_mask[indx_in_stack] = True
                                break

                #   get number of the last same frame to save it in the output structure
                num_last_same_frame = vsm.get_prev_num_frame()
                for indx_in_stack in sorted(where(~coll_TFT_stack_mask)[0],reverse=True):
                    coll_TFT_elem = collisions_TFT_list.pop(indx_in_stack)
                    coll_TFT_elem_text = coll_TFT_elem.text
                    coll_TFT_elem_start_frame = coll_TFT_elem.start_end_frames[0][0]
                    inserted = False
                    output_TFT_elem:TimedAndFramedText  # hinting variables for the IDE 
                    #  match on every element of the list sorted reversed because highly possible that 
                    for output_TFT_elem in output_TFT_stack: 
                        #   if already in the list append the starting and ending frames to the field in the struct 
                        if txt_classif.are_cosine_similar(output_TFT_elem.text, coll_TFT_elem_text) \
                                and txt_classif.is_partially_in(coll_TFT_elem_text,output_TFT_elem.text):
                            output_TFT_elem.start_end_frames.append((coll_TFT_elem_start_frame,num_last_same_frame))
                            inserted = True
                            break
                    if not inserted:
                        #   append the whole structure to the list
                        coll_TFT_elem.start_end_frames[0] = (coll_TFT_elem_start_frame,num_last_same_frame)
                        output_TFT_stack.push(coll_TFT_elem)
                if len(collisions_TFT_list) == 0:
                    vsm.end_collision()

            prev_frame.set_img(curr_frame.get_img())

            #   print percentage and measure max speed
            #max_speed = max(max_speed,vsm._debug_get_speed())
            #print("  video analysis "+str(vsm.get_percentage_progression())+'%'+" progress"+" max_speed = "+str(max_speed)+" "+"."*(iterations_counter%12)+" "*12,end="\r")
            print("  video analysis "+str(vsm.get_percentage_progression())+'%'+" progress"+"."*(iterations_counter%12)+" "*12,end="\r")
            iterations_counter += 1

        output_TFT_list = list(output_TFT_stack)
        frames_dist_tol = vsm.get_video().get_fps()*20
        #TODO check if TXT_LEN is a reasonable comparison method (i think it is not)
        txt_classif.set_comparison_methods([ComparisonMethod.TXT_SIM,ComparisonMethod.TXT_LEN,ComparisonMethod.MEANINGFUL_WORDS_NUM])
        output_TFT_list = self._compact_embedding_partial_words(output_TFT_list,txt_classif,frames_dist_tol)
        
        txt_classif.set_comparison_methods([ComparisonMethod.TXT_SIM,ComparisonMethod.TIME_PROXIMITY])
        output_TFT_list = self._compact_embedding_partial_words(output_TFT_list,txt_classif,frames_dist_tol)
        
        txt_classif.set_comparison_methods([ComparisonMethod.TIME_PROXIMITY,ComparisonMethod.POSITION_NOT_COLLIDING])
        output_TFT_list = self._compact_embedding_same_frames(output_TFT_list,txt_classif)

        txt_classif.set_comparison_methods([ComparisonMethod.TIME_PROXIMITY])
        output_TFT_list = self._compact_embedding_partial_words(output_TFT_list,txt_classif,frames_dist_tol)
        
        print()
        print(f"total time = {round(time.time()-start_time,ndigits=3)}"+" "*20)

        if _debug:
            video = vsm.get_video()
            for output_TFT_elem in output_TFT_list:
                pprint(output_TFT_elem)
                for start_end in output_TFT_elem.start_end_frames:
                    text = ''.join(list(output_TFT_elem.text)[:80]).replace('\n',' ')
                    frames = []
                    if start_end[0] > 0:
                        frames.append(vsm.get_frame_from_num(start_end[0]-1))
                    frames.append(vsm.get_frame_from_num(start_end[0]))
                    frames.append(vsm.get_frame_from_num(start_end[0]+1))
                    frames.append(vsm.get_frame_from_num(start_end[1]-1))
                    frames.append(vsm.get_frame_from_num(start_end[1]))
                    if start_end[1] < video.get_count_frames()-1:
                        frames.append(vsm.get_frame_from_num(start_end[1]+1))
                    frames.reverse()
                    if color_scheme_for_analysis==ColorScheme.BGR:
                        frames = [cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) for frame in frames]

                    if start_end[0] > 0:
                        frame = frames.pop()
                        plt.imshow(frame,cmap='gray')
                        plt.title(f"'{text}'\n frame before the start ({start_end[0]-1})")
                        plt.show()
                    frame = frames.pop()
                    plt.imshow(draw_bounding_boxes_on_image(frame,[output_TFT_elem.xywh]),cmap='gray')
                    plt.title(f"'{text}'\n\nstart {start_end[0]}")
                    plt.show()
                    frame = frames.pop()
                    plt.imshow(frame,cmap='gray')
                    plt.title(f"'{text}'\n\nframe after the start ({start_end[0]+1})")
                    plt.show()
                    frame = frames.pop()
                    plt.imshow(frame,cmap='gray')
                    plt.title(f"'{text}'\n\nframe before the end ({start_end[1]-1})")
                    plt.show()
                    frame = frames.pop()
                    plt.imshow(draw_bounding_boxes_on_image(frame,[output_TFT_elem.xywh]),cmap='gray')
                    plt.title(f"'{text}'\n\nend {start_end[1]}")
                    plt.show()
                    if start_end[1] < video.get_count_frames()-1:
                        frame = frames.pop()
                        plt.imshow(frame,cmap='gray')
                        plt.title(f"'{text}'\n frame after the end ({start_end[1]+1})")
                        plt.show()

        self._text_in_video = output_TFT_list

    def get_extracted_text(self,format:Literal['str','list','list[timed-tuple]','list[text_id, timed-tuple]']='list[text_id, timed-tuple]'):
        txt_cleaner = TextSimilarityClassifier()
        if self._text_in_video is None:
            return None
        if format=='list':
            return [elem.clean_copy(txt_cleaner) for elem in self._text_in_video]
        elif format=='str':
            return ' '.join([tft.text for tft in self._text_in_video])
        elif format=='list[timed-tuple]':
            video = LocalVideo(self._video_id)
            return [((video.get_time_from_num_frame(startend[0]),video.get_time_from_num_frame(startend[1])), txt_cleaner.clean_text(tft.text)) 
                        for tft in self._text_in_video for startend in tft.start_end_frames]
        elif format=='list[text_id, timed-tuple]':
            video = LocalVideo(self._video_id)
            return [(id,(video.get_time_from_num_frame(startend[0]),video.get_time_from_num_frame(startend[1])), txt_cleaner.clean_text(tft.text)) 
                        for id, tft in enumerate(self._text_in_video) 
                        for startend in tft.start_end_frames]
        else:
            return None

    def transcript_segmentation(self, subtitles, c_threshold=0.22, sec_min=0.35, S=1, frame_range=15):
        """
        :param c_threshold: threshold per la similarità tra frasi
        :param sec_min: se un segmento è minore di sec_min verrà unito con il successivo
        :param S: scala per color histogram
        :param frame_range: aggiustare inizio e fine dei segmenti in base a differenza nel color histogram nel frame_range
        :return: segments
        """
        video_id = self._video_id
        #video_id = video.split('&')[0].split("=")[1]

        '''Get the transcription from the subtitles'''
        transcription = ""
        for sub in subtitles:
            transcription += " " + sub["text"]

        transcription = transcription.replace('\n', ' ')\
            .replace(">>", "").replace("Dr.","Dr").replace("dr.","dr").replace("Mr.","Mr").replace("mr.","mr")

        # get punctuated transcription from the conll in the db
        punctuated_transcription = get_text(video_id)

        if punctuated_transcription is None:
            print("Checking punctuation..")
            if transcription.count(".") > 5 and transcription.count(",") > 5:
                print("transcription present")
                punctuated_transcription = transcription
            else:
                punctuated_transcription = None


        # if conll is not in the db
        if punctuated_transcription is None:
            print("Adding punctuation..")
            punct = Punctuator(os.path.join(os.path.dirname(os.path.abspath(getfile(self.__class__))), "punctuator", "Demo-Europarl-EN.pcl"))
            punctuated_transcription = punct.punctuate(transcription)

        segments_times = db_mongo.get_segments_times(video_id)

        # if segments times are not already in the db
        if segments_times is None:
            '''Divide into sentences the punctuated transcription'''
            print("Extracting sentences..")
            sentences = tokenize.sent_tokenize(punctuated_transcription)
            print(len(sentences))


            '''For each sentence, add its start and end time obtained from the subtitles'''
            timed_sentences = get_timed_sentences(subtitles, sentences)


            '''Define the BERT model for similarity'''
            print("Creating embeddings..")
            model = SentenceTransformer('paraphrase-distilroberta-base-v1')
            #model = SentenceTransformer('stsb-roberta-large')

            '''Compute a vector of numbers (the embedding) to idenfity each sentence'''
            embeddings = model.encode(sentences, convert_to_tensor=True)


            '''Create clusters based on semantic textual similarity, using the BERT embeddings'''
            print("Creating initials segments..")
            clusters = create_cluster_list(timed_sentences, embeddings, c_threshold)


            '''Aggregate togheter clusters shorter than 40 seconds in total'''
            refined_clusters = aggregate_short_clusters(clusters, sec_min)

            start_times = []
            end_times = []
            #print("Clusters done")

            '''Print the final result'''
            for c in refined_clusters:
                start_times.append(c.start_time)
                end_times.append(c.end_time)
        else:
            start_times = segments_times[0]
            end_times = segments_times[1]



        '''Find and append to each cluster the 2 most relevant sentences'''
        #num_sentences = 2
        #sumy_summary(refined_clusters, num_sentences)


        '''Adjust end and start time of each cluster based on detected scene changes'''
        current_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_path, "static", "videos", video_id)

        if not any(File.endswith(".jpg") for File in os.listdir(path)):
            images_path, start_times, end_times = self.create_keyframes(start_times, end_times, S, frame_range)
            print("Done creating keyframes")
        else:
            print("keyframes already present")
            images = []
            for File in os.listdir(path):
                if File.endswith(".jpg"):
                    images.append(File.split(".")[0])

            images.sort(key=int)
            images_path = ["videos/" + video_id + "/" + im + ".jpg" for im in images]

        return start_times, end_times, images_path, punctuated_transcription

from words import extract_keywords

if __name__ == '__main__':
    video = VideoAnalyzer('yN7ypxC7838') #TODO try again with this video and measure cv2.resize() performances against pure analysis
    #video = VideoAnalyzer('PPLop4L2eGk')
    #video = VideoAnalyzer('rFRO8IwB8aY') # Lesson Med 33 minutes low score and very slow
    #print(video.is_slide_video())
    
    #subtitles, autogenerated = video.get_transcript()
    
    # segment the video with semantic similarity
    #print("Entering segmentation")
    #start_times, end_times, images_path, text = video.transcript_segmentation(subtitles)
    
    video.extract_text_from_video()
    pprint(video.get_extracted_text())
    
    #lemmatized_concepts = extract_keywords(text, minFrequency=2)
    #print(lemmatized_concepts)
    #segmentation("https://www.youtube.com/watch?v=TpcbfxtdoI8", 0.19, 20, 1, 375)
    #segmentation("https://www.youtube.com/watch?v=KkgkZwQ9HgQ", 0.22, 40, 1, 375)
    # https://youtu.be/gbg89EJHtk0