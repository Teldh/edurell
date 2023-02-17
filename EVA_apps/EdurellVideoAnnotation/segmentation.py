from dataclasses import dataclass
from bisect import insort_left
from words import is_partially_in

@dataclass
class TimedAndFramedText:
    text: str
    start_end_frames: 'list[tuple[(int,int)]]'
    xywh: 'tuple[(int,int,int,int)]'
    
    def merge_adjacent_frames(self,tol:int=15) -> None:
        '''
        Merges adjacent (within a tolerance of frames) frame times a TimedAndFramedText structure
        '''
        start_end_frames = self.start_end_frames
        merged_start_end_frames = []
        curr_end = None
        curr_start = None
        for new_start,new_end in start_end_frames:
            if curr_end is None:
                curr_start = new_start
                curr_end = new_end
            elif new_start <= curr_end+tol:
                curr_end = new_end
            else:
                merged_start_end_frames.append((curr_start,curr_end))
                curr_end = new_end
                curr_start = new_start
        merged_start_end_frames.append((curr_start,curr_end))
        self.start_end_frames = merged_start_end_frames
    
    def extend_frames(self, other_start_end_list:'list[tuple[(int,int)]]'):
        for other_start_end_elem in other_start_end_list:
            insort_left(self.start_end_frames,other_start_end_elem)
    
    def is_partial_text_of(self, other:'TimedAndFramedText'):
        return  other is not None and   \
                ((len(self.text) > 4 and self.text.strip()[2:-2] in other.text) or   \
                    (self.text in other.text) or is_partially_in(self.text,other.text))

    def __lt__(self, other:'TimedAndFramedText'):
        return self.start_end_frames[-1][1] < other.start_end_frames[0][0]
    
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
from numpy import clip, all, array, empty, average,var,zeros
from image import ImageClassifier, ColorScheme, draw_bounding_boxes_on_image
from segmentation import TimedAndFramedText
from words import TextSimilarityClassifier
from pprint import pprint
from xgboost_model import XGBoostModelAdapter
from collections import deque
from video import VideoSpeedManager
from matplotlib import pyplot as plt
import time
from itertools_extension import pairwise_linked


class Segmentator:

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

    def _extract_analysis_frames_and_estimate_cos_sim_threshold(self, vsm:VideoSpeedManager, color_scheme_for_analysis:ColorScheme,num_segments:int=70):
        '''
        Split the video into num_segments windows frames, for every segment it's taken the first and the second frame\n
        The first is analyzed by XGBoost model to recognize the scene\n
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
        seconds_per_frame = floor(vsm.get_video().get_count_frames() / vsm.get_video().get_fps() / num_segments)
        speed = floor(vsm.get_video().get_fps()*seconds_per_frame)
        num_frames_analyzed = ceil(vsm.get_video().get_count_frames() / speed)
        vsm.lock_speed(speed)
        iterations_counter:int = 0
        cos_sim_values = empty((num_frames_analyzed,vsm.get_video().get_dim_frame()[2]))

        # Optimization can be performed by doing a first coarse-grained analysis with the XGBoost model predictor
        # then set those windows inside the VideoSpeedManager
        scene_model = XGBoostModelAdapter(os.path.dirname(os.path.realpath(__file__))+"/xgboost/model/xgboost500.sav")

        start_frame_num = None
        frames_to_analyze = []
        answ_queue = deque([False,False])
        curr_frame = ImageClassifier([None,color_scheme_for_analysis])
        prev_frame = curr_frame.copy()
        while not vsm.is_video_ended():
            prev_frame.set_img(vsm.get_frame())
            curr_frame.set_img(vsm.get_following_frame())
            answ_queue.appendleft(scene_model.is_enough_slidish_like(prev_frame)); answ_queue.pop()

            # if there's more than 1 True discontinuity -> cut the video
            if any(answ_queue) and start_frame_num is None:
                start_frame_num = iterations_counter*speed
            elif not any(answ_queue) and start_frame_num is not None:
                frames_to_analyze.append((start_frame_num,iterations_counter*speed))
                start_frame_num = None

            cos_sim_values[iterations_counter,:] = prev_frame.get_cosine_similarity(curr_frame)
            iterations_counter+=1
            #print(answ_queue[0]);plt.imshow(curr_frame.get_img(),cmap='gray');plt.show()
            print(f" Estimating cosine_similarity_threshold: {ceil((iterations_counter)/num_frames_analyzed * 100)}%",end='\r')

        else:
            
            if start_frame_num is not None:
                frames_to_analyze.append((start_frame_num,vsm.get_video().get_count_frames()-1))
            vsm.reset()
            cos_sim_img_threshold = clip(average(cos_sim_values,axis=0) + var(cos_sim_values,axis=0),0.9,0.99999)
            print(f"Estimating cosine_similarity_threshold: Done -> {cos_sim_img_threshold}")
            print(f"Frames to analyze: {frames_to_analyze} of {vsm.get_video().get_count_frames()} total frames")
            frames_to_analyze.sort(reverse=True)
            return cos_sim_img_threshold, frames_to_analyze

    def _shrink_englobe_partial_words(self,TFT_list: 'list[TimedAndFramedText]',_reverse_list:bool=False):
        '''
        Merge near TimedAndFramedText elements of the list where words are contained in the neighbour element.\n
        Goes in both directions with a recursive call

        ----------
        Parameters
        ----------
        TFT_list : list of texts
        _reverse_list : is a trigger for internal purposes
        
        Returns
        -------
        Same length or shorter list with frames merged 
        '''
        out_list:'list[TimedAndFramedText]' = []
        elem1:TimedAndFramedText
        elem2:TimedAndFramedText
        for elem1, elem2 in pairwise_linked(TFT_list,reversed=_reverse_list):
            if elem1.is_partial_text_of(elem2): elem2.extend_frames(elem1.start_end_frames)
            else: out_list.append(elem1)
        if _reverse_list:
            # end of recursion -> reversing the list to return in the correct order
            out_list.reverse()
            return out_list
        else:
            # recursive call
            return self._shrink_englobe_partial_words(out_list,_reverse_list=True)

    def extract_text_from_video(self,color_scheme_for_analysis:ColorScheme=ColorScheme.BGR,debug:bool=False):
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
        cos_sim_img_threshold, frames_to_analyze = self._extract_analysis_frames_and_estimate_cos_sim_threshold(vsm, color_scheme_for_analysis)
        if frames_to_analyze is None:
            return []
        
        curr_frame = ImageClassifier(image_and_scheme=[None,color_scheme_for_analysis])
        prev_frame = curr_frame.copy()

        output_TFT_list:'list[TimedAndFramedText]' = []
        printed_progress:int = -1
        iterations_counter:int = 0
        #max_speed:int = 0
        collisions_TFT_stack:'list[TimedAndFramedText]' = []
        txt_classif = TextSimilarityClassifier()
        vsm.lock_speed()
        if not (len(frames_to_analyze) == 1 and frames_to_analyze[0][0] == 0 and frames_to_analyze[0][1] == vsm.get_video().get_count_frames()-1):
            vsm.set_analysis_frames(frames_to_analyze)

        while not vsm.is_video_ended():
        
            curr_frame.set_img(vsm.get_frame())

            #   if collision stack is empty search for text in the current frame and then put it in the stack
            #   collide() function sets the speed cap of the video to the minimum and returns the num frame of the first frame with text within this the last iteration
            if len(collisions_TFT_stack) == 0:
                if curr_frame.detect_text():
                    num_start_frame = vsm.collide_and_get_fixed_num_frame()
                    curr_frame.set_img(vsm.get_frame_from_num(num_start_frame))
                    texts_with_cnt = curr_frame.detect_text(return_text=True,with_contours=True)
                    for text,xywh in texts_with_cnt:
                        collisions_TFT_stack.append(
                            TimedAndFramedText( text=text,
                                                start_end_frames=[(num_start_frame,-1)],
                                                xywh=xywh))

            # if there are collisions in the queue
            else: # we are in a collision window
                # if there's statistical difference from the last frame or video is ended -> scene changed
                if not all(curr_frame.get_cosine_similarity(prev_frame,on_histograms=True) >= cos_sim_img_threshold) \
                    or vsm.is_video_ended():

                    #   detect the different text in the new frame with respect to the already present in the collision stack
                    #   save diffs in a mask
                    texts_with_cnt = curr_frame.detect_text(return_text=True,with_contours=True)
                    mask = zeros(len(collisions_TFT_stack),dtype=bool)
                    if not vsm.is_video_ended():
                        for text_in_image,_ in texts_with_cnt:
                            for indx_in_stack, timedText_coll in enumerate(collisions_TFT_stack):
                                if text_in_image == timedText_coll.text:
                                    mask[indx_in_stack] = True

                    #   get number of the last same frame to save it in the output structure
                    num_last_same_frame = vsm.get_prev_num_frame()
                    #   for every changed text of the collision stack (False in the mask), find if already in the list
                    for indx_in_stack,found_this_text_in_new_frame in sorted(enumerate(mask),reverse=True): # converted to stack to pop elements from it
                        if not found_this_text_in_new_frame:
                            coll_TFT_elem = collisions_TFT_stack.pop(indx_in_stack)
                            coll_TFT_elem_text = coll_TFT_elem.text
                            coll_TFT_elem_start_frame = coll_TFT_elem.start_end_frames[0][0]
                            inserted = False
                            for output_TFT_elem in sorted(output_TFT_list,reverse=True): #  sorted reversed because coul be modified
                                #   if already in the list append the starting and ending frames to the field in the struct 
                                if txt_classif.cosine_sim_SKL(output_TFT_elem.text, coll_TFT_elem_text) > 0.8:
                                    output_TFT_elem.start_end_frames.append((coll_TFT_elem_start_frame,num_last_same_frame))
                                    inserted = True
                                    break
                            #   else append the whole structure to the list
                            if not inserted:
                                coll_TFT_elem.start_end_frames[0] = (coll_TFT_elem_start_frame,num_last_same_frame)
                                output_TFT_list.append(coll_TFT_elem)

                    if len(collisions_TFT_stack)==0:
                        vsm.end_collision()

            prev_frame.set_img(curr_frame.get_img())

            #   print percentage and measure max speed
            curr_percentage = vsm.get_percentage_progression()
            #max_speed = max(max_speed, vsm._debug_get_speed())
            print("  video analysis "+str(curr_percentage)+'%'+" progress"+"."*(iterations_counter%12)+" "*12,end="\r")
            if curr_percentage > printed_progress:
                printed_progress = curr_percentage
            iterations_counter += 1

        
        output_TFT_list = self._shrink_englobe_partial_words(output_TFT_list)
        [TFT_elem.merge_adjacent_frames(tol=vsm.get_video().get_fps()*2) for TFT_elem in output_TFT_list]

        # TODO before merge remove all the useless words found

        print()
        print(f"total time = {round(time.time()-start_time,ndigits=3)}"+" "*20)

        if debug:
            video = vsm.get_video()
            for output_TFT_elem in output_TFT_list:
                #print(output_TFT_elem)
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

        return output_TFT_list

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
    #segmentator = Segmentator('yN7ypxC7838')
    segmentator = Segmentator('PPLop4L2eGk')
    
    subtitles, autogenerated = segmentator.get_transcript()
    # segment the video with semantic similarity
    print("Entering segmentation")
    #start_times, end_times, images_path, text = segmentator.transcript_segmentation(subtitles)
    out_list = segmentator.extract_text_from_video()
    pprint(out_list)
    #lemmatized_concepts = extract_keywords(text, minFrequency=2)
    #print(lemmatized_concepts)
    #segmentation("https://www.youtube.com/watch?v=TpcbfxtdoI8", 0.19, 20, 1, 375)
    #segmentation("https://www.youtube.com/watch?v=KkgkZwQ9HgQ", 0.22, 40, 1, 375)