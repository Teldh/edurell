from dataclasses import dataclass
from bisect import insort_left
from typing_extensions import Literal
from typing import List,Tuple

class TextCleaner:

    def __init__(self) -> None:
        # selects all chars except to alphanumerics space & -
        self.pattern = re.compile('[^a-zA-Z\d &-]')
    
    def clean_text(self,text:str):
        return ' '.join(self.pattern.sub(' ',text).split()).lower()

class TimedAndFramedText:
    """
    Structure made of:
        - _framed_sentences: list of portions of a full_text composed field and their absolute location on the screen 
        - _full_text: full string built for comparison purposes
        - start_end_frames: list of tuples of num start and num end frames of this text
        
    """
    _framed_sentences: List[Tuple[Tuple[int,int],Tuple[int,int,int,int]]]
    _full_text: str
    start_end_frames: List[Tuple[(int,int)]]

    def __init__(self,framed_sentences:List[Tuple[str,Tuple[int,int,int,int]]],startend_frames:List[Tuple[(int,int)]]) -> None:
        self.start_end_frames = startend_frames
        full_text = ''
        converted_framed_sentence:List[Tuple[Tuple[int,int],Tuple[int,int,int,int]]] = []
        curr_start = 0
        for sentence,bb in framed_sentences:
            full_text += sentence
            len_sent = len(sentence)
            converted_framed_sentence.append(((curr_start,curr_start+len_sent),bb))
            curr_start += len_sent
        self._framed_sentences = converted_framed_sentence
        self._full_text = full_text
 
    def copy(self):
        tft_copy = TimedAndFramedText(framed_sentences=None,start_end_frames=self.start_end_frames)
        tft_copy._framed_sentences=self._framed_sentences
        tft_copy._full_text = self._full_text
        return tft_copy
    
    def extend_frames(self, other_start_end_list:List[Tuple[(int,int)]]) -> None:
        '''
        extend this element's start_end frames with the other list in a sorted way
        '''
        for other_start_end_elem in other_start_end_list:
            insort_left(self.start_end_frames,other_start_end_elem)

    def get_full_text(self):
        return self._full_text
    
    def get_split_text(self):
        '''
        returns the full text splitted by new lines without removing them
        '''
        return self._full_text.split("(?<=\n)")

    def get_framed_sentences(self):
        '''
        converts the full text string into split segments of text with their respective bounding boxes
        '''
        full_text = self._full_text
        return [((full_text[start_char_pos:end_char_pos]),bb) for (start_char_pos,end_char_pos),bb in self._framed_sentences]

    def merge_adjacent_startend_frames(self,max_dist:int=15) -> 'TimedAndFramedText':
        '''
        Merges this object adjacent (within a max_dist) frame times
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

    def __lt__(self, other:'TimedAndFramedText'):
        return self.start_end_frames[0][0] < other.start_end_frames[0][0]
    
    def __repr__(self) -> str:
        return 'TFT(txt={0}, on_screen_in_frames={1}, text_portions_with_bb_normzd={2})'.format(
            repr(self._full_text),repr(self.start_end_frames),repr(self._framed_sentences))
    
from sklearn.feature_extraction.text import CountVectorizer
from difflib import ndiff
import re
from nltk.corpus import words
from numpy import dot,round,empty,prod,sum,array
from numpy.linalg import norm
from transformers import pipeline
from collections import Counter

COMPARISON_METHOD_TXT_SIM_RATIO:int=0
COMPARISON_METHOD_TXT_MISS_RATIO:int=1
COMPARISON_METHOD_MEANINGFUL_WORDS_COUNT:int=2
COMPARISON_METHOD_FRAMES_TIME_PROXIMITY:int=3

class TextSimilarityClassifier:
    """
    Text diffences classifier\n
    Using various methods can check if some text is part of other text\n
    or if two texts are similar
    """

    def __init__(self,comp_methods:List[int] or None=None,
                 max_removed_chars_over_total_diff:float=0.1,
                 min_common_chars_ratio:float=0.8,
                 max_removed_chars_over_txt:float=0.3,
                 max_added_chars_over_total:float= 0.2,
                 time_frames_tol = 10  ) -> None:
        self._CV = CountVectorizer()
        self._txt_cleaner:TextCleaner = TextCleaner()
        if comp_methods is None:
            self._comp_methods = {COMPARISON_METHOD_TXT_MISS_RATIO,COMPARISON_METHOD_TXT_SIM_RATIO}
        else:
            self.set_comparison_methods(comp_methods)
        self.removed_chars_diff_ratio_thresh = max_removed_chars_over_total_diff
        self.added_chars_diff_ratio_thresh = max_added_chars_over_total
        self.common_chars_txt_ratio_thresh = min_common_chars_ratio
        self.removed_chars_txt_ratio_thresh = max_removed_chars_over_txt
        self.time_frames_tol = time_frames_tol
        self._words = set(words.words())
        self._noise_classifier = pipeline('text-classification', model='textattack/bert-base-uncased-imdb')

    def is_partially_in(self,TFT1:TimedAndFramedText,TFT2:TimedAndFramedText) -> bool:
        '''
        Finds if the framed_text1 is part of the framed_text2

        Then are compared in terms of one or more predefined methods: 
            - time proximity of their frames within a tolerance\n
            - NOT IMPLEMENTED ANYMORE { collision of their bounding boxes [improve adding a tol] }
        
        Then it is passed to is_partially_in_txt_version(), check that documentation

        Order is based on performance maximization
            
        ### No checks are performed on input

        -------

        Returns
        -------
        True if text1 is part of the text2

        '''
        comp_methods = self._comp_methods
        checks:list[bool] = [bool(TFT1) and bool(TFT2)]

        if all(checks) and COMPARISON_METHOD_FRAMES_TIME_PROXIMITY in comp_methods:
            frames_tol = self.time_frames_tol
            startends1 = TFT1.start_end_frames; startends2 = TFT2.start_end_frames
            found_all = True
            for startend1 in startends1:
                found = False
                for startend2 in startends2:
                    if startend2[0] - frames_tol <= startend1[0] and startend1[1] <= startend2[1] + frames_tol:
                        found = True
                        break
                if not found: found_all = False; break
            checks.append(found_all)
                    
        return all(checks) and self.is_partially_in_txt_version(TFT1.get_full_text(),TFT2.get_full_text())
        
    def is_partially_in_txt_version(self,text1:str,text2:str) -> bool:
        '''
        Finds if text1 is partial text of text2
        texts are cleaned of all non alphanumeric characters.

        Then are compared in terms of one or more predefined methods: 
            - diffs percentage of all the merged texts with respect to 3 thresholds:\n
                removed chars from txt1 with respect to txt2 over the total diff\n
                common chars of both texts\n
                added chars in txt1 to reach txt2 over the total diff\n
            - most rich and meaningful text\n
            - removed chars percentage over the string

        
        Order is based on performance maximization
            
        ### No checks are performed on input

        -------

        Returns
        -------
        True if text1 is part of the text2

        '''
        checks = [bool(text1) and bool(text2)]
        comp_methods = self._comp_methods

        if all(checks) and COMPARISON_METHOD_TXT_SIM_RATIO in comp_methods:
            cleaner = self._txt_cleaner
            text1_cleaned = cleaner.clean_text(text1); text2_cleaned = cleaner.clean_text(text2)
            counter = Counter([change[0] for change in ndiff(text1_cleaned,text2_cleaned)])
            removed_chars_count = 0 if not '-' in counter.keys() else counter['-']
            common_chars_count = 0 if not ' ' in counter.keys() else counter[' ']
            added_chars_count = 0 if not '+' in counter.keys() else counter['+']
            diffs_len = removed_chars_count+common_chars_count+added_chars_count
            text1_len = len(text1_cleaned)
            checks.append(  diffs_len > 0 and 
                            text1_len > 0 and 
                            removed_chars_count/diffs_len < self.removed_chars_diff_ratio_thresh and 
                            common_chars_count/text1_len > self.common_chars_txt_ratio_thresh  and
                            added_chars_count/diffs_len < self.added_chars_diff_ratio_thresh)
        
        if all(checks) and COMPARISON_METHOD_MEANINGFUL_WORDS_COUNT in comp_methods:
            all_words = self._words
            txt1_split = text1_cleaned.split(); txt2_split = text2_cleaned.split()
            len_txt1_split = len(txt1_split); len_txt2_split = len(txt2_split) 
            checks.append(( 0 < len_txt1_split <= len_txt2_split 
                                and ( len([word for word in txt1_split if word in all_words]) / len(txt1_split) 
                                        <= 
                                      len([word for word in txt2_split if word in all_words]) / len(txt2_split)) ) 
                            or len_txt1_split <= len_txt2_split )
        
        if all(checks) and COMPARISON_METHOD_TXT_MISS_RATIO in comp_methods:
            checks.append(  text1_len > 0 and 
                            removed_chars_count/len(text1_cleaned) < self.removed_chars_txt_ratio_thresh)
        
        return all(checks)

    def are_cosine_similar(self,text1:str,text2:str,confidence:float=0.9) -> bool:
        '''
        Determine if two texts are cosine similar.

        This is evaluated in terms of words mapped to a unique number\n
        ### May collapse when performed on texts with num words = 1 vs 2 or 2 vs 1

        -----------

        Parameters:
        ----------
            - text1 (str): The first text to compare.
            - text2 (str): The second text to compare.
            - confidence (float, optional): The minimum confidence level required to consider
                the texts similar. Defaults to 0.9

        Returns:
        --------
            bool: True if the texts are cosine similar with a confidence level above
                `confidence`, False otherwise.  

        '''
        cleaner = self._txt_cleaner
        text1_clean_split, text2_clean_split = cleaner.clean_text(text1).split(), cleaner.clean_text(text2).split()
        len_split1, len_split2 = len(text1_clean_split), len(text2_clean_split)
        max_len = max(len_split1,len_split2)
        words_set = set(text1_clean_split+text2_clean_split)
        values = list(range(1,len(words_set)+1))
        words_dict = dict(zip(words_set,values))
        text1_vectorized = list(map(lambda key: words_dict[key], text1_clean_split))
        text2_vectorized = list(map(lambda key: words_dict[key], text2_clean_split))
        texts_vectorized = empty((2,max_len),dtype=int)
        texts_vectorized[0,:len_split1] = text1_vectorized; texts_vectorized[0,len_split1:] = 0
        texts_vectorized[1,:len_split2] = text2_vectorized; texts_vectorized[1,len_split2:] = 0
        return sum(prod(texts_vectorized,axis=0))/prod(norm(texts_vectorized,axis=1)) > confidence

    def set_comparison_methods(self,methods:List[int]):
        assert not COMPARISON_METHOD_TXT_MISS_RATIO in methods or COMPARISON_METHOD_TXT_SIM_RATIO in methods, \
                "Too low granularity in setting txt_missing and not txt_similarity"
        self._comp_methods = set(methods)

TxSmCl = TextSimilarityClassifier

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
import os, sys

from conll import get_text
from Cluster import create_cluster_list, aggregate_short_clusters
from audio_transcription import get_timed_sentences

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
from numpy import clip, all, array, empty, average, var, zeros, where, ones, dtype, quantile
from pprint import pprint
from collections import deque
from matplotlib import pyplot as plt
import time
from operator import itemgetter

from image import ImageClassifier,draw_bounding_boxes_on_image,COLOR_RGB,COLOR_BGR,DIST_MEAS_METHOD_COSINE_SIM
from video import VideoSpeedManager, LocalVideo
from xgboost_model import XGBoostModelAdapter
from itertools_extension import double_iterator, pairwise_linked_iterator
from collections_extension import LiFoStack

class VideoAnalyzer:

    _text_in_video: List[TimedAndFramedText] or None = None
    _video_slidishness = None
    _cos_sim_img_threshold = None
    _frames_to_analyze = None

    def __init__(self,video_id:str,from_youtube:bool=True) -> None:
        if from_youtube:
            self._video_id = video_id
        else:
            raise Exception("not implemented!")
    
    def _create_keyframes(self,start_times,end_times,S,seconds_range, image_scale:float=0.5):
        """
        Take a list of clusters and compute the color histogram on end and start of the cluster
        
        Parameters
        ----------
        cluster_list :
        S : scala per color histogram
        seconds_range : aggiustare inizio e fine dei segmenti in base a differenza nel color histogram
        """
        assert len(start_times) == len(end_times)
        vsm = VideoSpeedManager(self._video_id,output_colors=COLOR_RGB)
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
            images_path, start_times, end_times = self._create_keyframes(start_times, end_times, S, frame_range)
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


    def _remove_classification_errors(self,lst: List[TimedAndFramedText],vsm: VideoSpeedManager,img_classif:ImageClassifier,txt_classif: TextSimilarityClassifier):
        '''
        for every element of the input list of TimedAndFramedText checks if at every start frame the text recognized is approximatly the same\n
        otherwise it pops that startend frames or removes the whole element if it's too distant from the real one found 
        '''
        for i, elem in reversed(list(enumerate(lst))):
            text_in_lst = elem.get_full_text()
            start_end_frames = elem.start_end_frames
            for j, startend in reversed(list(enumerate(start_end_frames))):
                img_classif.set_img(vsm.get_frame_from_num(startend[0]))
                text_in_frame = img_classif.extract_text(return_text=True)
                if  len(text_in_frame) == 0 or \
                    startend[0] == startend[1] or \
                    len(text_in_lst) == 0 or \
                    (not txt_classif.is_partially_in_txt_version(text_in_frame,text_in_lst) and \
                    not txt_classif.is_partially_in_txt_version(text_in_lst,text_in_frame)): 
                        start_end_frames.pop(j)
            elem.start_end_frames = start_end_frames
            if len(elem.start_end_frames) == 0: lst.pop(i)
        return lst

    def _preprocess_video(self, vsm:VideoSpeedManager,num_segments:int=150,estimate_threshold=False,_show_info=False):
        '''
        Split the video into `num_segments` windows frames, for every segment it's taken the frame that's far enough to guarantee a minimum sensibility\n
        The current frame is analyzed by XGBoost model to recognize the scene\n
        If there are two non-slide frames consecutively the resulting frame window is cut\n
        Bounds are both upper and lower inclusive to avoid a miss as much as possible\n
        Then both are compared in terms of cosine distance of their histograms (it's faster than flattening and computing on pure pixels)\n\n
        Lastly the distance between wach frame is selected as either the average of values, either with fixed value.\n
        In this instance with videos that are mostly static, the threshold is set to 0.9999

        Returns
        ----------
        The cosine similarity threshold and the list of frames to analyze (tuples of starting and ending frames)

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
        if estimate_threshold:
            cos_sim_values = empty((num_segments,vsm.get_video().get_dim_frame()[2]))
            #dists = empty((num_segments,vsm.get_video().get_dim_frame()[2]))

        # Optimization is performed by doing a first coarse-grained analysis with the XGBoost model predictor
        # then set those windows inside the VideoSpeedManager
        scene_model = XGBoostModelAdapter(os.path.dirname(os.path.realpath(__file__))+"/xgboost/model/xgboost500.sav")

        start_frame_num = None
        frames_to_analyze:List[Tuple[int,int]] = []
        answ_queue = deque([False,False])
        curr_frame = ImageClassifier(image_and_scheme=[None,vsm._color_scheme])
        prev_frame = curr_frame.copy()
        while iterations_counter < num_segments:
            prev_frame.set_img(vsm.get_frame())
            curr_frame.set_img(vsm.get_following_frame())
            answ_queue.appendleft(scene_model.is_enough_slidish_like(prev_frame)); answ_queue.pop()

            # if there's more than 1 True discontinuity -> cut the video
            if any(answ_queue) and start_frame_num is None:
                start_frame_num = int(clip(iterations_counter-1,0,num_segments))*speed
            elif not any(answ_queue) and start_frame_num is not None:
                frames_to_analyze.append((start_frame_num,(iterations_counter-1)*speed))
                start_frame_num = None

            if estimate_threshold:
                cos_sim_values[iterations_counter,:] = prev_frame.get_cosine_similarity(curr_frame)
                #dists[iterations_counter,:] = curr_frame.get_mean_distance(prev_frame)
            iterations_counter+=1
            #print(answ_queue[0]);plt.imshow(curr_frame.get_img(),cmap='gray');plt.show()
            #print(f" Estimating cosine_similarity_threshold: {ceil((iterations_counter)/num_segments * 100)}%",end='\r')
            if _show_info: print(f" Coarse-grained analysis: {ceil((iterations_counter)/num_segments * 100)}%",end='\r')
        if start_frame_num is not None:
            frames_to_analyze.append((start_frame_num,num_frames-1))

        if estimate_threshold:
            cos_sim_img_threshold = clip(average(cos_sim_values,axis=0)+var(cos_sim_values,axis=0)/2,0.9,0.9999)
            #cos_sim_img_threshold = clip(cos_sim_values.min(axis=0),0.9,0.99999)
            #   can't estimate correctly the cosine similarity threshold with average, too dependant from the segments chosen and also too low
            #   neither can set to max because it's always more than 1 neither to min because it's too low
            #diff_threshold = average(diffs,axis=0)+3*var(diffs,axis=0)
            #dist_threshold = (dists.max(axis=0) - dists.min(axis=0)) / 2
        else:
            cos_sim_img_threshold = ones((1,vsm.get_video().get_dim_frame()[2]))*0.9999
        
        if _show_info:
            if estimate_threshold:
                print(f"Estimated cosine similarity threshold: {cos_sim_img_threshold}")
            else:
                print(f"Cosine_similarity threshold: {cos_sim_img_threshold}")
                #print(f"Estimated mean_dist_threshold: {dist_threshold}")
            print(f"Frames to analyze: {frames_to_analyze} of {num_frames} total frames")
        counter:int = 0
        for frame_window in frames_to_analyze:
            counter += (frame_window[1] - frame_window[0])
        self._video_slidishness = counter/(num_frames-1)

        self._cos_sim_img_threshold = cos_sim_img_threshold 
        self._frames_to_analyze = frames_to_analyze #dist_threshold, frames_to_analyze

    def _compact_embedding_partial_words(self,TFT_list:'list[TimedAndFramedText]',text_classifier:TextSimilarityClassifier,frames_max_dist:int):
        '''
        Merge near TimedAndFramedText elements of the list\n
        Goes in both directions reversing the array and lastly iterates over all the elements with an (optimized) nested loop\n

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
                if text_classifier.is_partially_in(elem1,elem2): elem2.extend_frames(elem1.start_end_frames)
                else: output_list.append(elem1)
            input_list = output_list

        deleted:'list[int]' = []
        for i1,i2, elem1,elem2 in double_iterator(input_list,enumerated=True):
            if not i1 in deleted and not i2 in deleted and text_classifier.is_partially_in(elem1,elem2):
                elem2.extend_frames(elem1.start_end_frames)
                deleted.append(i1)
        return sorted([elem.merge_adjacent_startend_frames(max_dist=frames_max_dist) for indx, elem in enumerate(input_list) if not indx in deleted])

    def analyze_video(self,color_scheme_for_analysis:int=COLOR_BGR,_show_info:bool=False,_plot_contours=False):
        '''
        Firstly the video is analized in coarse-grained way, by a ML model to recognize frames of slides
        and the threshold for the difference between two frames is concurrently estimated. \n
        The method uses an ImageClassifier to detect text in the frames of the video
        Then saves that text in a collision stack.\n
        It then looks for changes in the collision stack with respect to the text in the current frame
        flushes the differences in the output list.\n
        Finally, it calls two helper methods to clean up the output list by combining partial words and merging adjacent frames.

        Parameters :
        ------------
        - color_scheme_for_analysis : is a predefined value that must be either COLOR_BGR or COLOR_RGB from image.py
        - _show_info : prints in stdout progression and set thresholds
        - _plot_contours : shows images with bounding boxes once the video has been analyzed

        Returns :
        ---------
        None but sets internal text that can be retrieved with ``get_extracted_text()``
        '''
        assert color_scheme_for_analysis is not None and (color_scheme_for_analysis == COLOR_BGR or color_scheme_for_analysis == COLOR_RGB)
        start_time = time.time()
        vsm = VideoSpeedManager(self._video_id,color_scheme_for_analysis)
        if self._cos_sim_img_threshold is None:
            self._preprocess_video(vsm,_show_info=_show_info)
        img_diff_threshold, frames_to_analyze = self._cos_sim_img_threshold, self._frames_to_analyze
        vsm.reset()
        if frames_to_analyze is None:
            self._text_in_video = []
            return
        
        curr_frame = ImageClassifier(   comp_method = DIST_MEAS_METHOD_COSINE_SIM,
                                        threshold = img_diff_threshold,
                                        image_and_scheme = [None,color_scheme_for_analysis]   )
        prev_frame = curr_frame.copy()

        output_TFT_stack:LiFoStack[TimedAndFramedText] = LiFoStack()
        iterations_counter:int = 0
        collisions_TFT_list:'list[TimedAndFramedText]' = []
       #max_speed = 0
        txt_classif = TxSmCl(comp_methods=[COMPARISON_METHOD_TXT_SIM_RATIO,
                                           COMPARISON_METHOD_TXT_MISS_RATIO])
       #vsm.lock_speed()
        if not vsm.is_full_video(frames_to_analyze):
            vsm.set_analysis_frames(frames_to_analyze)

        while not vsm.is_video_ended():
        
            curr_frame.set_img(vsm.get_frame())

            #   collide() function sets the speed cap of the video to the minimum and returns the num frame of the first frame with text within this the last iteration

            #   if collision stack is empty search for text in the current frame and then put it in the stack
            if len(collisions_TFT_list) == 0 and curr_frame.extract_text():
                num_start_frame = vsm.collide_and_get_fixed_num_frame()
                curr_frame.set_img(vsm.get_frame_from_num(num_start_frame))
                collisions_TFT_list.append(TimedAndFramedText( framed_sentences= curr_frame.extract_text(return_text=True,with_contours=True),
                                                               startend_frames= [(num_start_frame,-1)]))

            #   otherwise put the text not visible any more in the output stack
            elif len(collisions_TFT_list) > 0 and \
                    (not curr_frame.is_similar_to(prev_frame) or vsm.is_video_ended()):
                
                coll_TFT_stack_mask = zeros(len(collisions_TFT_list,),dtype=bool)
                #   create a mask for the text that's still on screen
                if not vsm.is_video_ended():
                    text_on_screen:str = curr_frame.extract_text(return_text=True)
                    for indx_in_stack, coll_elem in enumerate(collisions_TFT_list):
                        if text_on_screen and text_on_screen in coll_elem.get_full_text():
                            coll_TFT_stack_mask[indx_in_stack] = True
                            break

                #   get number of the last same frame to save it in the output structure
                num_last_same_frame = vsm.get_prev_num_frame()
                for indx_in_stack in sorted(where(~coll_TFT_stack_mask)[0],reverse=True):
                    coll_TFT_elem = collisions_TFT_list.pop(indx_in_stack)
                    inserted = False
                    output_TFT_elem:TimedAndFramedText  # hinting variables for the IDE 
                    #  match on every element of the list sorted reversed because highly possible that 
                    for output_TFT_elem in output_TFT_stack: 
                        #   if already in the list append the starting and ending frames to the field in the struct 
                        if txt_classif.are_cosine_similar(output_TFT_elem.get_full_text(), coll_TFT_elem.get_full_text()):# \
                                #and txt_classif.is_partially_in(coll_TFT_elem,output_TFT_elem):
                            output_TFT_elem.start_end_frames.append((coll_TFT_elem.start_end_frames[0][0],num_last_same_frame))
                            inserted = True
                            break
                    if not inserted:
                        #   append the whole structure to the list
                        coll_TFT_elem.start_end_frames[0] = (coll_TFT_elem.start_end_frames[0][0],num_last_same_frame)
                        output_TFT_stack.push(coll_TFT_elem)
                if len(collisions_TFT_list) == 0:
                    vsm.end_collision()

            prev_frame.set_img(curr_frame.get_img())

            #   print percentage and measure max speed
           #max_speed = max(max_speed,vsm._debug_get_speed())
           #print("  video analysis "+str(vsm.get_percentage_progression())+'%'+" progress"+" max_speed = "+str(max_speed)+" "+"."*(iterations_counter%12)+" "*12,end="\r")
            if _show_info:
                print("  video analysis "+str(vsm.get_percentage_progression())+'%'+" progress"+"."*(iterations_counter%12)+" "*12,end="\r")
            iterations_counter += 1

        output_TFT_list = list(output_TFT_stack)
        frames_dist_tol = vsm.get_video().get_fps()*10

        txt_classif.set_comparison_methods([COMPARISON_METHOD_TXT_SIM_RATIO,
                                            COMPARISON_METHOD_TXT_MISS_RATIO,
                                            COMPARISON_METHOD_MEANINGFUL_WORDS_COUNT])
        output_TFT_list = self._compact_embedding_partial_words(output_TFT_list,txt_classif,frames_dist_tol)

        txt_classif.set_comparison_methods([COMPARISON_METHOD_FRAMES_TIME_PROXIMITY])
        output_TFT_list = self._compact_embedding_partial_words(output_TFT_list,txt_classif,frames_dist_tol)

        txt_classif.set_comparison_methods([COMPARISON_METHOD_TXT_SIM_RATIO,
                                            COMPARISON_METHOD_TXT_MISS_RATIO])
        output_TFT_list = self._remove_classification_errors(output_TFT_list,vsm,curr_frame,txt_classif)

        if _show_info:        
            print("video analysis completed!"+" "*30)
            print(f"total time = {round(time.time()-start_time,decimals=3)}"+" "*20)

        if _plot_contours:
            video = vsm.get_video()
            for output_TFT_elem in output_TFT_list:
                pprint(output_TFT_elem)
                for start_end in output_TFT_elem.start_end_frames:
                    text = ''.join(list(output_TFT_elem.get_full_text())[:80]).replace('\n',' ')
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
                    if color_scheme_for_analysis==COLOR_BGR:
                        frames = [cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) for frame in frames]

                    if start_end[0] > 0:
                        frame = frames.pop()
                        plt.imshow(frame,cmap='gray')
                        plt.title(f"'{text}'\n frame before the start ({start_end[0]-1})")
                        plt.show()
                    frame = frames.pop()
                    bbs = [elem[1] for elem in output_TFT_elem.get_framed_sentences()]
                    plt.imshow(draw_bounding_boxes_on_image(frame,bbs),cmap='gray')
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
                    bbs = [elem[1] for elem in output_TFT_elem.get_framed_sentences()]
                    plt.imshow(draw_bounding_boxes_on_image(frame,bbs),cmap='gray')
                    plt.title(f"'{text}'\n\nend {start_end[1]}")
                    plt.show()
                    if start_end[1] < video.get_count_frames()-1:
                        frame = frames.pop()
                        plt.imshow(frame,cmap='gray')
                        plt.title(f"'{text}'\n frame after the end ({start_end[1]+1})")
                        plt.show()

        self._text_in_video = output_TFT_list

    def get_extracted_text(self,format:Literal['str','list','list[text,box]','list[time,text,box]','list[time,list[text,box]]','list[id,text,box]']='list',from_ids:'tuple[int]' or None=None):
        """
        Returns the text extracted from the video.\n
        Text can be cleaned from non-alphanumeric characters or not.

        Parameters :
        ------------
        - format (str): The desired format of the output. Defaults to 'list[text_id, timed-tuple]'.
            - 'str': single string with the text joined together.\n
            - 'list': list of TimedAndFramedTexts\n
            - 'list[time,list[text,box]]': a list of (times, list of (sentence, bounding-box))
            - 'list[text,box]': list of texts with bounding boxes
            - 'list[id,text,box]': list of tuple of id, text, and bounding boxes
            - 'list[time,text,box]': list of repeated times (in frames) for every text_bounding_boxed
            - 'list[tuple(id,timed-text)]': list of tuples made of (startend times in seconds, text as string present in those frames)
        """
        if self._text_in_video is None:
            return None
        if format=='list':
            return self._text_in_video
        elif format=='str':
            return ' '.join([tft.get_full_text() for tft in self._text_in_video])
        elif format=='list[text,box]':
            out_lst = []
            for tft in self._text_in_video:
                out_lst.extend(tft.get_framed_sentences())
            return out_lst
        elif format=='list[id,text,box]':
            timed_text_with_bb = []
            _id = 0
            for tft in self._text_in_video:
                for sentence,bb in tft.get_framed_sentences():
                    timed_text_with_bb.append((_id,sentence,bb))
                    _id +=1
            return timed_text_with_bb
        elif format=='list[time,text,box]':
            timed_text_with_bb = []
            for tft in self._text_in_video:
                for sentence,bb in tft.get_framed_sentences():
                    timed_text_with_bb.append((tft.start_end_frames,sentence,bb))
            return timed_text_with_bb
        elif format=='list[time,list[text,box]]':
            video = LocalVideo(self._video_id)
            timed_text = []
            texts = self._text_in_video
            for tft in texts:
                for startend in tft.start_end_frames:
                    insort_left(timed_text,((video.get_time_from_num_frame(startend[0]),video.get_time_from_num_frame(startend[1])), tft.get_full_text()))
            return timed_text
        elif format=='list[tuple(id,timed-text)]':
            video = LocalVideo(self._video_id)
            return [(id,(video.get_time_from_num_frame(startend[0]),video.get_time_from_num_frame(startend[1])), tft.get_full_text()) 
                            for id, tft in enumerate(self._text_in_video) 
                            for startend in tft.start_end_frames]
        return None

    def is_slide_video(self,slide_frames_percent_threshold:float=0.6):
        '''
        Returns
        -------
        True if percentage of recognized slidish frames is above the threshold
        '''
        if self._video_slidishness is None:
            self._preprocess_video(vsm=VideoSpeedManager(self._video_id,COLOR_RGB))
        self._video_slidishness:float
        return self._video_slidishness > slide_frames_percent_threshold

    def extract_titles(self,quant:float=.88,axis_for_outliers_detection:Literal['w','h','wh']='h',union=True,with_times=True):
        """
        Titles are extracted by performing statistics on the axis defined, computing a threshold based on quantiles\n
        and merging results based on union of results or intersection\n
        #TODO improvements: now the analysis is performed on the whole list of sentences, but can be performed:\n
            - per slide\n
            - then overall\n
            but i don't know if can be beneficial

        Prerequisites :
        ------------
        Must have runned analyze_video()
        
        Parameters :
        ----------
        - quant : quantile as lower bound for outlier detection
        - axis_for_outliers_detection : axis considered for analysis are 'width' or 'height' or both 
        - union : lastly it's perfomed a union of results (logical OR) or an intersection (logical AND)
        - with_times : if with_times returns a list of tuples(startend_frames, text, bounding_box)
                otherwise startend_frames are omitted
            
        Returns :
        ---------
        List of all the detected titles
        """
        assert axis_for_outliers_detection in {'w','h','wh'} and 0 < quant < 1 and self.get_extracted_text(format='list[id,text,box]') is not None
        # convert input into columns slice for analysis
        sliced_columns = {'w':slice(2,3),'h':slice(3,4),'wh':slice(2,4)}[axis_for_outliers_detection]
        texts_with_bb = self.get_extracted_text(format='list[time,text,box]')
        # select columns
        axis_array = array([text_with_bb[2][sliced_columns] for text_with_bb in texts_with_bb],dtype=dtype('float','float'))
        # compute statistical analysis on columns
        indices_above_threshold = where((axis_array > quantile(axis_array,quant,axis=0)).any(axis=1))[0] if union else \
                                  where((axis_array > quantile(axis_array,quant,axis=0)).all(axis=1))[0]
        # selects the above texts
        if with_times:
            titles = itemgetter(*indices_above_threshold)(texts_with_bb)
        else:
            titles = itemgetter(*indices_above_threshold)(list(zip(*list(zip(*texts_with_bb))[1:])))
        return titles

    def create_thumbnails(self):
        '''
        could replace previous creation of keyframes
        '''
        images_path = []
        images_already_present = False
        current_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_path, "static", "videos", self._video_id)
        if any(File.endswith(".jpg") for File in os.listdir(path)):
            thumbnails = [File for File in os.listdir(path) if File.endswith(".jpg")]
            for i in range(len(thumbnails)):
                for File in os.listdir(path):
                    if File.startswith(str(i)+"."):
                        images_path.append("videos/" + self._video_id + "/" + File)
            images_already_present = True
        assert self._text_in_video is not None
        time_text = self.get_extracted_text(format='list[time,list[text,box]]')
        start_times =[]
        end_times = []
        video = LocalVideo(self._video_id,output_colors=COLOR_RGB)

        for i,((start_seconds,end_seconds),_) in enumerate(time_text):
            if not images_already_present:
                video.set_num_frame(video.get_num_frame_from_time(start_seconds))
                image = video.extract_next_frame()
                assert image is not None
                file_name = str(i) + ".jpg"
                image_file_dir = os.path.join(path, file_name)
                cv2.imwrite(image_file_dir, image)
                images_path.append("videos/" + self._video_id + "/" + file_name)
            start_times.append(start_seconds)
            end_times.append(end_seconds)
        return start_times, end_times, images_path
        

from words import extract_keywords

def main_in_segmentation():
    import db_mongo
    # WEAK_POINT not performing fast with long videos or text that composes character by character each frame 
    #video = VideoAnalyzer('yN7ypxC7838') #TODO try again with this video and measure cv2.resize() performances against pure analysis
    #video = VideoAnalyzer('g8w-IKUFoSU') #infants and juveniles forensic
    video = VideoAnalyzer('PPLop4L2eGk') #introduction to ML
    #video = VideoAnalyzer('UuzKYffpxug') #estimating stature forensic
    #video = VideoAnalyzer('ujutUfgebdo')
    #video = VideoAnalyzer('rFRO8IwB8aY') # Lesson Med 33 minutes low score and very slow

    video.analyze_video(_show_info=True)
    #print(video.extract_titles())
    #video.create_thumbnails()
    results = video.extract_titles()
    results_dict = [{'start_end_frames':start_end_frames,'title':title,'xywh_normalized':bb} for (start_end_frames,title,bb) in results]
    pprint(results_dict)
    
    image = ImageClassifier(image_and_scheme=[None, COLOR_BGR])
    video_ref = LocalVideo('PPLop4L2eGk')
    from matplotlib import pyplot as plt
    fig, ax = plt.subplots(nrows=1,ncols=5, figsize=(16,9))
    j=0
    for (start_end_frames,title,bb) in results:
        for start_end in start_end_frames:
            axis = ax[j]
            video_ref.set_num_frame(start_end[0])
            title = title.rstrip('\n')
            axis.set_title(f"'Title: {title}'\n\nstart frame: {start_end[0]}\ntime: {video_ref.get_time_from_num_frame(start_end[0])}")
            image.set_img(draw_bounding_boxes_on_image(video_ref.extract_next_frame(),[bb]))
            image._debug_show_image(axis)
            j+=1

    plt.show()
    # TODO make plots
    
    #subtitles, autogenerated = video.get_transcript()
    #start_times, end_times, images_path, text = video.transcript_segmentation(subtitles)
    #print(db_mongo.get_extracted_keywords(video._video_id))
    
    #print(video.is_slide_video())
    #lemm_concepts_transcript = extract_keywords(text,minFrequency=3)

    #subtitles, autogenerated = video.get_transcript()
    
    # segment the video with semantic similarity
    #print("Entering segmentation")
    #start_times, end_times, images_path, text = video.transcript_segmentation(subtitles)
    
    #lemm_concepts_video_text = []
    #titles = []
    #curr_id = 0
    #for (text_id,timing,text) in text_on_screen:
    #    if curr_id < text_id:
    #        lemm_concepts_video_text.append(extract_keywords(text,maxWords=2))
    #        titles.append(extract_title(text))
    #        curr_id = text_id
    #print(f"titles: {titles}")
    #print(f"lemm_concepts_video_text: {lemm_concepts_video_text}")
    
    #lemmatized_concepts = extract_keywords(text, minFrequency=2)
    #print(lemmatized_concepts)
    #segmentation("https://www.youtube.com/watch?v=TpcbfxtdoI8", 0.19, 20, 1, 375)
    #segmentation("https://www.youtube.com/watch?v=KkgkZwQ9HgQ", 0.22, 40, 1, 375)
    # https://youtu.be/gbg89EJHtk0


if __name__ == '__main__':
    main_in_segmentation()