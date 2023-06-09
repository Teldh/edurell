from bisect import insort_left
from typing_extensions import Literal
from typing import List,Tuple
from multiprocessing import Process
from sklearn.feature_extraction.text import CountVectorizer
from difflib import ndiff
import re
from nltk import tokenize
from nltk.corpus import words
from numpy import round,empty,prod,sum,array,clip,all,average,var,zeros,where,ones,dtype,quantile
from numpy.linalg import norm
from transformers import pipeline
from collections import Counter
from sentence_transformers import SentenceTransformer
import os, sys
from inspect import getfile
import cv2
from youtube_transcript_api import YouTubeTranscriptApi as YTTranscriptApi
from math import floor, ceil
from pprint import pprint
from collections import deque
from matplotlib import pyplot as plt
import time
from operator import itemgetter
from itertools import groupby
from conllu import parse

from image import *
from video import VideoSpeedManager, LocalVideo
from xgboost_model import XGBoostModelAdapter
from itertools_extension import double_iterator, pairwise_linked_iterator
from collections_extension import LiFoStack
from conll import get_text
from words import get_keywords_from_title
from Cluster import create_cluster_list, aggregate_short_clusters
from audio_transcription import get_timed_sentences
import db_mongo


class TextCleaner:

    def __init__(self) -> None:
        # selects all chars except to alphanumerics space & -
        self.pattern = re.compile('[^a-zA-Z\d &-]')
    
    def clean_text(self,text:str):
        return ' '.join(self.pattern.sub(' ',text).split()).lower()

class TimedAndFramedText:
    """
    Structure made of:
        - _full_text: full string built for comparison purposes
        - _framed_sentences: list of portions of a full_text composed field and their absolute location on the screen 
        - start_end_frames: list of tuples of num start and num end frames of this text
        
    """
    _full_text: str
    _framed_sentences: List[Tuple[Tuple[int,int],Tuple[int,int,int,int]]]
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
        removed_chars_count = None

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
            if removed_chars_count is None:
                cleaner = self._txt_cleaner
                text1_cleaned = cleaner.clean_text(text1); text2_cleaned = cleaner.clean_text(text2)
                counter = Counter([change[0] for change in ndiff(text1_cleaned,text2_cleaned)])
                removed_chars_count = 0 if not '-' in counter.keys() else counter['-']
                text1_len = len(text1_cleaned)
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


    def is_exactly_in_txt_version(self,text1:str,text2:str,chars_tol_percentage:float=0.9):
        '''
        Checks whether there's the same string text1 in text2, within a reasonable margin of error\n
        Based on perfect match from left to right so if text1 has char in second position different\n
        from what is in text2, the match is insignificant\n\n

        TODO can be improved with match in reversed string but might get expencive
        '''
        cleaner = self._txt_cleaner
        clean_text1 = cleaner.clean_text(text1)
        res = re.search(clean_text1,cleaner.clean_text(text2))
        return res is not None and len(res.group(0))/len(clean_text1) > chars_tol_percentage

    def subtract_common_text(self,text1:str,text2:str):
        '''
        Performs text1 - text2 where they are in common
        
        Can be improved by using ndiff alg but for now keep it simple
        '''
        return self._txt_cleaner.clean_text(text1.replace(text2,'').lstrip())

    def set_comparison_methods(self,methods:List[int]):
        self._comp_methods = set(methods)



#################################################################################
# Issue with online server (incompatibility with gunicorn)
# Edited import to fix issue: (https://github.com/chrisspen/punctuator2/issues/3)
import sys
incompatible_path = '/home/anaconda3/envs/myenv/bin'
if incompatible_path in sys.path:
    sys.path.remove(incompatible_path)
from punctuator import Punctuator
#################################################################################

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



class VideoAnalyzer:
    '''
    This class analyzes videos from their ids in the path "__class__"-path/static/videos \n
    _testing_path is for changing the folder path but it's used just for testing\n\n
        - It provides a method to get the transcript from the youtube link associated to the id provided\n
        - segment the transcript to obtain keyframes\n
        - Analyze the whole video stream or frames to segment slides,text and times on screen of those\n
        - Get the extracted text in different formats (tipically only one is used and the others are for debug)\n
        - Check if the video contains slides (for now this means text around the center of the screen) and the proportion with respect to the whole video len\n
        - Extract titles from the slides found\n
        - Create thumbnails based on the slides segmentation after having analyzed the text\n
        - Find definitions and in-depths of concepts expressed in the title of every slide
    checks of valid session are performed sometimes to ensure user did not want to stop analysis
    '''
    _text_in_video: List[TimedAndFramedText] or None = None
    _video_slidishness = None
    _cos_sim_img_threshold = None
    _frames_to_analyze = None
    _slide_startends = None
    _slide_titles = None

    def __init__(self,video_id:str,from_youtube:bool=True,_testing_path:str=None) -> None:
        if from_youtube:
            self._video_id = video_id
        else:
            raise Exception("not implemented!")
        self._testing_path = _testing_path
    
    def _create_keyframes(self,start_times,end_times,S,seconds_range, image_scale:float=1,create_thumbnails=True):
        """
        Take a list of clusters and compute the color histogram on end and start of the cluster
        
        Parameters
        ----------
        cluster_list :
        S : scala per color histogram
        seconds_range : Adjust the start and end of segments based on the difference in color histograms.
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
        checking if there is a scene change within a timeframe of "seconds_range" frames from the beginning and end of each cluster.
        '''
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
        if create_thumbnails:
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
            return images_path, start_times, end_times
        else:
            return start_times,end_times

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

    def transcript_segmentation(self, subtitles, c_threshold=0.22, sec_min=35, S=1, frame_range=15,create_thumbnails=True):
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

        if create_thumbnails:
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
        else:
            start_times,end_times = self._create_keyframes(start_times, end_times, S, frame_range, create_thumbnails=False)
            return start_times, end_times, punctuated_transcription
        

    def can_be_analyzed(self,video:LocalVideo=None,max_seconds=18000):
        if video is None:
            video = VideoSpeedManager(self._video_id).get_video()
        return video.get_count_frames() / video.get_fps() <= max_seconds

    def _preprocess_video(self, vsm:VideoSpeedManager,num_segments:int=150,estimate_threshold=False,_show_info=False):
        '''
        Split the video into `num_segments` windows frames, for every segment it's taken the frame that's far enough to guarantee a minimum sensibility\n
        The current frame is analyzed by XGBoost model to recognize the scene\n
        If there are two non-slide frames consecutively the resulting frame window is cut\n
        Bounds are both upper and lower inclusive to avoid a miss as much as possible\n
        Then both are compared in terms of cosine distance of their histograms (it's faster than flattening and computing on pure pixels)\n\n
        Lastly the distance between wach frame is selected as either the average of values, either with fixed value.\n
        In this instance with videos that are mostly static, the threshold is set to 0.9999
        #TODO further improvements: for more accuracy this algorithm could include frames similarity to classify a segment as slide (which is a generally very static)

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
        txt_cleaner = TextCleaner()
        if estimate_threshold:
            cos_sim_values = empty((num_segments,vsm.get_video().get_dim_frame()[2]))

        # Optimization is performed by doing a first coarse-grained analysis with the XGBoost model predictor
        # then set those windows inside the VideoSpeedManager
        scene_model = XGBoostModelAdapter(os.path.dirname(os.path.realpath(__file__))+"/xgboost/model/xgboost500.sav")

        start_frame_num = None
        frames_to_analyze:List[Tuple[int,int]] = []
        answ_queue = deque([False,False])
        curr_frame = ImageClassifier(image_and_scheme=[None,vsm._color_scheme])
        prev_frame = curr_frame.copy()
        frame_w,frame_h,num_colors = vsm.get_video().get_dim_frame()
        while iterations_counter < num_segments:
            prev_frame.set_img(vsm.get_frame())
            curr_frame.set_img(vsm.get_following_frame())
            if scene_model.is_enough_slidish_like(prev_frame):
                frame = prev_frame.get_img()
                # validate slide in frame by slicing the image in a region that removes logos (that are usually in corners)
                region = (slice(int(frame_h/4),int(frame_h*3/4)),slice(int(frame_w/4),int(frame_w*3/4)))
                prev_frame.set_img(frame[region])
                # double checks the text  
                is_slide = bool(txt_cleaner.clean_text(prev_frame.extract_text(return_text=True)).strip())
            else:
                is_slide = False
            answ_queue.appendleft(is_slide); answ_queue.pop()

            # if there's more than 1 True discontinuity -> cut the video
            if any(answ_queue) and start_frame_num is None:
                start_frame_num = int(clip(iterations_counter-1,0,num_segments))*speed
            elif not any(answ_queue) and start_frame_num is not None:
                frames_to_analyze.append((start_frame_num,(iterations_counter-1)*speed))
                start_frame_num = None

            if estimate_threshold:
                cos_sim_values[iterations_counter,:] = prev_frame.get_cosine_similarity(curr_frame)
            iterations_counter+=1
            if _show_info: print(f" Coarse-grained analysis: {ceil((iterations_counter)/num_segments * 100)}%",end='\r')
        if start_frame_num is not None:
            frames_to_analyze.append((start_frame_num,num_frames-1))

        if estimate_threshold:
            cos_sim_img_threshold = clip(average(cos_sim_values,axis=0)+var(cos_sim_values,axis=0)/2,0.9,0.9999)
        else:
            cos_sim_img_threshold = ones((1,num_colors))*0.9999
        
        if _show_info:
            if estimate_threshold:
                print(f"Estimated cosine similarity threshold: {cos_sim_img_threshold}")
            else:
                print(f"Cosine_similarity threshold: {cos_sim_img_threshold}")
            print(f"Frames to analyze: {frames_to_analyze} of {num_frames} total frames")
        self._video_slidishness = sum([frame_window[1] - frame_window[0] for frame_window in frames_to_analyze])/(num_frames-1)
        self._cos_sim_img_threshold = cos_sim_img_threshold 
        self._frames_to_analyze = frames_to_analyze

    def _merge_and_cleanup(self,TFT_list:'list[TimedAndFramedText]',vsm: VideoSpeedManager,frame:ImageClassifier,frames_dist_tol:int):
        
        txt_classif = TextSimilarityClassifier()

        def compact_embedding_partial_words(TFT_list:'list[TimedAndFramedText]',text_classifier:TextSimilarityClassifier,frames_max_dist:int):
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

        txt_classif.set_comparison_methods([COMPARISON_METHOD_TXT_SIM_RATIO,
                                            COMPARISON_METHOD_TXT_MISS_RATIO,
                                            COMPARISON_METHOD_MEANINGFUL_WORDS_COUNT])
        TFT_list = compact_embedding_partial_words(TFT_list,txt_classif,frames_dist_tol)

        txt_classif.set_comparison_methods([COMPARISON_METHOD_FRAMES_TIME_PROXIMITY])
        TFT_list = compact_embedding_partial_words(TFT_list,txt_classif,frames_dist_tol)

        txt_classif.set_comparison_methods([COMPARISON_METHOD_TXT_SIM_RATIO,
                                            COMPARISON_METHOD_TXT_MISS_RATIO])
        
        def remove_classification_errors(lst: List[TimedAndFramedText],vsm: VideoSpeedManager,img_classif:ImageClassifier,txt_classif: TextSimilarityClassifier,min_seconds_duration=2):
            '''
            for every element of the input list of TimedAndFramedText checks if at every start frame the text recognized is approximatly the same\n
            checks also that the text has a minimum len and the segment's duration is long enough\n
            otherwise it pops that startend frames or removes the whole element if it's too distant from the real one found 
            '''
            min_frames_duration = vsm.get_video().get_fps()*min_seconds_duration
            for i, elem in reversed(list(enumerate(lst))):
                text_in_lst = elem.get_full_text()
                start_end_frames = elem.start_end_frames
                for j, startend in reversed(list(enumerate(start_end_frames))):
                    img_classif.set_img(vsm.get_frame_from_num(startend[0]))
                    text_in_frame = img_classif.extract_text(return_text=True)
                    if  len(text_in_frame) < 4 or \
                        startend[0] + min_frames_duration > startend[1] or \
                        len(text_in_lst) < 4 or \
                        (not txt_classif.is_partially_in_txt_version(text_in_frame,text_in_lst) and \
                        not txt_classif.is_partially_in_txt_version(text_in_lst,text_in_frame)): 
                            start_end_frames.pop(j)
                elem.start_end_frames = start_end_frames
                if len(elem.start_end_frames) == 0: lst.pop(i)
            return lst

        return remove_classification_errors(TFT_list,vsm,frame,txt_classif)
    

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
        if self._video_slidishness is None:
            self._preprocess_video(vsm,_show_info=_show_info)
        else:
            self._cos_sim_img_threshold = ones((1,vsm.get_video().get_dim_frame()[2]))*0.9999
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
        txt_classif = TextSimilarityClassifier(comp_methods=[COMPARISON_METHOD_TXT_SIM_RATIO,
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
                    merged = False
                    output_TFT_elem:TimedAndFramedText  # hinting variables for the IDE 
                    #  match on every element of the list sorted reversed because highly possible that 
                    for output_TFT_elem in output_TFT_stack: 
                        #   if already in the list append the starting and ending frames to the field in the struct 
                        if txt_classif.are_cosine_similar(output_TFT_elem.get_full_text(), coll_TFT_elem.get_full_text()):# \
                                #and txt_classif.is_partially_in(coll_TFT_elem,output_TFT_elem):
                            output_TFT_elem.start_end_frames.append((coll_TFT_elem.start_end_frames[0][0],num_last_same_frame))
                            merged = True
                            break
                    if not merged:
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

        output_TFT_list = self._merge_and_cleanup(output_TFT_list,vsm,curr_frame,frames_dist_tol)

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

    def get_extracted_text(self,format:Literal['str','list','list[text,box]','set[times]','list[text,time,box]','list[time,list[text,box]]','list[id,text,box]']='list',from_ids:'tuple[int]' or None=None):
        """
        Returns the text extracted from the video.\n
        Text can be cleaned from non-alphanumeric characters or not.

        Parameters :
        ------------
        - format (str): The desired format of the output. Defaults to 'list[text_id, timed-tuple]'.
            - 'str': single string with the text joined together.\n
            - 'list': list of TimedAndFramedTexts\n
            - 'set[times] : list of unique texts' times (in seconds) (used for creation of thumbnails)
            - 'list[time,list[text,box]]': a list of (times, list of (sentence, bounding-box))
            - 'list[text,box]': list of texts with bounding boxes
            - 'list[id,text,box]': list of tuple of id, text, and bounding boxes
            - 'list[text,time,box]': list of repeated times (in seconds) for every text_bounding_boxed
            - 'list[tuple(id,timed-text)]': list of tuples made of (startend times in seconds, text as string present in those frames)
        """
        if self._text_in_video is None:
            return None
        if format=='list':
            return self._text_in_video
        elif format=='str':
            return ' '.join([tft.get_full_text() for tft in self._text_in_video])
        elif format=='set[times]':
            out = []
            video = LocalVideo(self._video_id)
            for tft in self._text_in_video:
                out.extend([(video.get_time_from_num_frame(st_en_frames[0]),video.get_time_from_num_frame(st_en_frames[1])) for st_en_frames in tft.start_end_frames])
            return out
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
        elif format=='list[text,time,box]':
            timed_text_with_bb = []
            video = LocalVideo(self._video_id)
            for tft in self._text_in_video:
                st_en_frames = tft.start_end_frames[0]
                for sentence,bb in tft.get_framed_sentences():
                    timed_text_with_bb.append((sentence.strip('\n'),(video.get_time_from_num_frame(st_en_frames[0]),video.get_time_from_num_frame(st_en_frames[1])),bb))
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

    def is_slide_video(self,slide_frames_percent_threshold:float=0.5,return_value=False,return_slide_frames=False,_show_info=False):
        '''
        Computes a threshold against a value that can be calculated or passed as precomputed_value
        
        Returns
        -------
        value and slide frames if return value is True\n
        else\n
        True and slide frames if percentage of recognized slidish frames is above the threshold
        '''
        if self._video_slidishness is None:
            self._preprocess_video(vsm=VideoSpeedManager(self._video_id,COLOR_RGB,_testing_path=self._testing_path),_show_info=_show_info)
        self._video_slidishness:float
        
        if return_value:
            returned_elements = self._video_slidishness
        else:
            returned_elements = self._video_slidishness > slide_frames_percent_threshold
        if return_slide_frames:
            returned_elements = (returned_elements, self._frames_to_analyze)
        return returned_elements

    def extract_titles(self,quant:float=.8,axis_for_outliers_detection:Literal['w','h','wh']='h',union=True,with_times=True) -> list:
        """
        Titles are extracted by performing statistics on the axis defined, computing a threshold based on quantiles\n
        and merging results based on union of results or intersection\n
        #TODO improvements: now the analysis is performed on the whole list of sentences, but can be performed:\n
            - per slide\n
            - then overall\n
        but i don't know if can be beneficial, depends on style of presentation. 
        For now the assumption is that there's uniform text across all the slides and titles are generally bigger than the other text

        Then titles are further more filtered by choosing that text whose size is above the threshold, only if it's
        the first sentence of the slide\n
            
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
        assert axis_for_outliers_detection in {'w','h','wh'} and 0 < quant < 1 and self.get_extracted_text(format='list[text,time,box]') is not None
        # convert input into columns slice for analysis
        sliced_columns = {'w':slice(2,3),'h':slice(3,4),'wh':slice(2,4)}[axis_for_outliers_detection]
        texts_with_bb = self.get_extracted_text(format='list[text,time,box]')
        
        # select columns
        axis_array = array([text_with_bb[2][sliced_columns] for text_with_bb in texts_with_bb],dtype=dtype('float','float'))
        
        # compute statistical analysis on columns
        indices_above_threshold = list(where((axis_array > quantile(axis_array,quant,axis=0)).any(axis=1))[0]) if union else \
                                  list(where((axis_array > quantile(axis_array,quant,axis=0)).all(axis=1))[0])

        slides_group = []
        # group by slide
        # x[0] is one element of indices_above_threshold to compare, x[1] is another
        # [1] accesses the startend seconds of that TimedAndFramedText  [text, startend, bounding_boxes]
        # [0] picks the start second of that object [start_second, end_second]
        for _,g in groupby(enumerate(indices_above_threshold),lambda x: texts_with_bb[x[0]][1][0] - texts_with_bb[x[1]][1][0]):
            slides_group.append(list(reversed(list(map(lambda x:x[1], g)))))
        slides_group = list(reversed(slides_group))

        # remove indices of text that are classified as titles but are just big text that's not at the top of every slide
        for group in slides_group:
            for indx_text in group:
                if indx_text > 0 and indx_text-1 not in group and (                        # if i'm not at the first index and the text of the previous index is not in the group
                   texts_with_bb[indx_text-1][1][0] == texts_with_bb[indx_text][1][0] and  # and the text is in the same slide
                   texts_with_bb[indx_text-1][2][1] < texts_with_bb[indx_text][2][1]):     # and has a y value lower than my current text (there's another sentence before this one)
                    indices_above_threshold.remove(indx_text)

        # selects the texts from the list of texts
        if len(indices_above_threshold) == 0:
            return None
        
        if not with_times:
            if len(indices_above_threshold) > 1:
                return itemgetter(*indices_above_threshold)(list(zip(*list(zip(*texts_with_bb))[0:3:2])))
            return [itemgetter(*indices_above_threshold)(list(zip(*list(zip(*texts_with_bb))[0:3:2])))]
        if len(indices_above_threshold) > 1:
            return itemgetter(*indices_above_threshold)(texts_with_bb)
        return [itemgetter(*indices_above_threshold)(texts_with_bb)]
        
        

    def create_thumbnails(self):
        '''
        Create thumbnails of keyframes from slide segmentation

        --------------
        Prerequisites
        --------------
        Must have runned analyze_video() or set(slide_startends)

        -------------------------------
        it's used to replace previous creation of keyframes when video is enough slidish\n
        '''

        assert self._slide_startends is not None or self._text_in_video is not None, "Must firstly either set slides startends or analyze the video"
        
        times = self._slide_startends
        print(times)
        if times is None:
            times = sorted(self.get_extracted_text(format='set[times]'))
        else:
            times = sorted(times)

        images_path = []
        images_already_present = False
        current_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_path, "static", "videos", self._video_id)
        if any(File.endswith(".jpg") for File in os.listdir(path)):
            thumbnails = [File for File in os.listdir(path) if File.endswith(".jpg")]
            if len(times) == len(thumbnails):
                for i in range(len(thumbnails)):
                    for File in os.listdir(path):
                        if File.startswith(str(i)+"."):
                            images_path.append("videos/" + self._video_id + "/" + File)
                assert len(thumbnails) == len(images_path), "Images are incorrectly labeled!"
                images_already_present = True
            else:
                for File in os.listdir(path):
                    if not File.endswith(".mp4"):
                        print("removing "+File)
                        os.remove(os.path.join(path,File))
                images_already_present = False

        

        start_times = []
        end_times = []
        video = LocalVideo(self._video_id)
        for i,(start_seconds,end_seconds) in enumerate(times):
            start_times.append(start_seconds)
            end_times.append(end_seconds)
            if not images_already_present:
                video.set_num_frame(video.get_num_frame_from_time(start_seconds+0.5))
                image = video.extract_next_frame()
                assert image is not None
                file_name = str(i) + ".jpg"
                image_file_dir = os.path.join(path, file_name)
                cv2.imwrite(image_file_dir, image)
                images_path.append("videos/" + self._video_id + "/" + file_name)
            
        return start_times, end_times, images_path

    def adjust_or_insert_definitions_and_indepth_times(self,burst_concepts:List[dict],definition_tol_seconds:float = 3,_show_output=False):
        '''
        This is an attempt to find definitions from timed sentences of the transcript and the timed titles of the slides.\n
        Heuristic is that if there's a keyword in the title of a slide (frontpage slide excluded)
        find the first occurence of that keyword in the transcript within a tolerance seconds window before and after the appearance of the slide
        set that as "definition" only if it contains the keyword of the title .\n 
        Heuristic for the in-depth is that after definition there's an in-depth of the slide, this means that the concept is explained further there, until the slide with that title won't disappear.\n
        
        On the algorithmic side sentences of the transcript used by the heuristic are mapped to the conll version of the text,
        cleaning operation is performed to remove errors (it groups the contiguous hit of every used sentence of the transcript to the conll by groups len and picks the biggest)\n
        Then the mapped sentences are aggregated by start and end sentence ids\n
        Lastly if the burst analysis has different definition times it is overwritten, if it does not contain the definition, this is appended at the end
        '''
        if self._slide_titles is None:
            raise Exception('slide titles not set')
        
        def extract_defs_and_indepths(burst_concepts: List[dict],titles:'list[dict]',timed_sentences:'list[dict]',definition_tol_seconds:float,_show_output=False):
            video_defs = {}
            video_in_depths = {}
            #txt_classif = TextSimilarityClassifier([COMPARISON_METHOD_TXT_MISS_RATIO])
            is_introductory_slide = True

            for title in titles:
                if is_introductory_slide or title['start_end_seconds'] == start_end_times_introductory_slides: # TODO is there always an introductory slide?
                    start_end_times_introductory_slides = title['start_end_seconds']
                    is_introductory_slide = False

                else:
                    start_time_title,end_time_title = title['start_end_seconds']
                    title_lowered = title["text"].lower()
                    title_keyword = [burst_concept['concept'] for burst_concept in burst_concepts if burst_concept['concept'] in title_lowered]
                    if len(title_keyword) > 0:
                        title_keyword = title_keyword[0]
                    else:
                        title_keyword = get_keywords_from_title(title['text'])[0]

                    for sent_id, timed_sentence in enumerate(timed_sentences):
                        if title_keyword not in video_defs.keys() and \
                           abs(start_time_title - timed_sentence['start']) < definition_tol_seconds and \
                           title_keyword in timed_sentence['text']:
                            if _show_output:
                                print()
                                print('********** Here comes the definition of the following keyword *******')
                                print(f'keyword from title: {title_keyword}')
                                print(f"time: {str(timed_sentence['start'])[:5]} : {str(timed_sentence['end'])[:5]}  |  sentence: {timed_sentence['text']}")
                                print()
                            #timed_sentence['id'] = ts_id
                            video_defs[title_keyword] = [(sent_id,timed_sentence)]
                            
                        # enlarge end time threshold to incorporate split slides with the same title
                        if title_keyword in video_defs.keys() and \
                           end_time_title > timed_sentence['end'] - 1 and \
                           timed_sentence['start'] > video_defs[title_keyword][0][1]['start']: # and \
                           #txt_classif.is_partially_in_txt_version(title_keywords[0],timed_sentence['text']):
                            if title_keyword not in video_in_depths.keys():
                                if _show_output:
                                    print('********** Here comes the indepth of the following keyword *******')
                                    print(f'keyword from title: {title_keyword}')
                                    print(f"time: {str(timed_sentence['start'])[:5]} : {str(timed_sentence['end'])[:5]}  |  sentence: {timed_sentence['text']}")
                                #timed_sentence['id'] = ts_id
                                video_in_depths[title_keyword] = [(sent_id,timed_sentence)]
                                
                            elif not any([True for _,tmd_sentence in video_in_depths[title_keyword] if tmd_sentence['start'] == timed_sentence['start']]):
                                #timed_sentence['id'] = ts_id
                                video_in_depths[title_keyword].append((sent_id,timed_sentence))
                                if _show_output:
                                    print(f"time: {str(timed_sentence['start'])[:5]} : {str(timed_sentence['end'])[:5]}  |  sentence: {timed_sentence['text']}")
            if _show_output:
                print()
            return video_defs,video_in_depths
        
        
        #print(burst_concepts)
        # extract definitions and in-depths in the transcript of every title based on slide show time and concept citation (especially with definition)
        timed_sentences = get_timed_sentences(self.get_transcript()[0],[sent.metadata["text"] for sent in parse(get_text(self._video_id,return_conll=True)[1])])
        video_defs, video_in_depths = extract_defs_and_indepths(burst_concepts,self._slide_titles,timed_sentences,definition_tol_seconds,_show_output=_show_output)

        def seconds_to_h_mm_ss_dddddd(time:float):
            millisec = str(time%1)[2:8]
            millisec += '0'*(6-len(millisec))
            seconds = str(int(time)%60)
            seconds = '0'*(2-len(seconds)) + seconds
            minutes = str(int(time/60))
            minutes = '0'*(2-len(minutes)) + minutes
            hours = str(int(time/3600))
            return hours+':'+minutes+':'+seconds+'.'+millisec

        # Creating or modifying burst_concept definition of the video results 
        added_concepts = []
        concepts_used = {concept:False for concept in video_defs.keys()}
        concept_description_type = "Definition"
        for burst_concept in burst_concepts:
            if burst_concept["concept"] in video_defs.keys() and burst_concept["description_type"] == concept_description_type:

                if burst_concept["start_sent_id"] != video_defs[burst_concept["concept"]][0][0] or \
                   burst_concept["end_sent_id"] != video_defs[burst_concept["concept"]][-1][0]:
                    burst_concept_name = burst_concept['concept']
                    burst_concept['start_sent_id'] = video_defs[burst_concept_name][0][0]
                    burst_concept['end_sent_id'] = video_defs[burst_concept_name][-1][0]
                    burst_concept['start'] = seconds_to_h_mm_ss_dddddd(video_defs[burst_concept_name][0][1]["start"])
                    burst_concept['end'] = seconds_to_h_mm_ss_dddddd(video_defs[burst_concept_name][-1][1]["end"])
                    burst_concept['creator'] = "Video_Analysis"
                    concepts_used[burst_concept_name] = True
        
        for concept_name in video_defs.keys():
            if not concepts_used[concept_name]:
                burst_concepts.append({ 'concept':concept_name,
                                        'start_sent_id':video_defs[concept_name][0][0],
                                        'end_sent_id':video_defs[concept_name][-1][0],
                                        'start':seconds_to_h_mm_ss_dddddd(video_defs[concept_name][0][1]['start']),
                                        'end':seconds_to_h_mm_ss_dddddd(video_defs[concept_name][-1][1]["end"]),
                                        'description_type':concept_description_type,
                                        'creator':'Video_Analysis'})
                if not concept_name in added_concepts:
                    added_concepts.append(concept_name)

        # In Depths must be managed differently since there can be more than one
        concepts_used = {concept:False for concept in video_in_depths.keys()}
        concept_description_type = "In Depth"
        for video_concept_name in video_in_depths.keys():
            most_proximal = {'found':False}
            for id_, burst_concept in reversed(list(enumerate(burst_concepts))):
                
                if burst_concept["concept"] == video_concept_name and burst_concept["description_type"] == concept_description_type:
                    if not most_proximal["found"]:
                        most_proximal['found'] = True
                        most_proximal["id"] = id_
                        most_proximal['diff_start_sent_id'] = abs(burst_concept['start_sent_id']-video_in_depths[video_concept_name][0][0])
                        most_proximal['diff_end_sent_id'] = abs(burst_concept['end_sent_id']-video_in_depths[video_concept_name][-1][0])
                    else:
                        if most_proximal['diff_start_sent_id'] > abs(burst_concept['start_sent_id']-video_in_depths[video_concept_name][0][0]):
                            most_proximal["id"] = id_
                            most_proximal['diff_start_sent_id'] = abs(burst_concept['start_sent_id']-video_in_depths[video_concept_name][0][0])
                            most_proximal['diff_end_sent_id'] = abs(burst_concept['end_sent_id']-video_in_depths[video_concept_name][-1][0])
                
                elif most_proximal['found'] and burst_concept["concept"] != video_concept_name:
                    target_concept = burst_concepts[most_proximal['id']]
                    target_concept['start'] = seconds_to_h_mm_ss_dddddd(video_in_depths[video_concept_name][0][1]["start"])
                    target_concept['end'] = seconds_to_h_mm_ss_dddddd(video_in_depths[video_concept_name][-1][1]["end"])
                    target_concept['start_sent_id'] = video_in_depths[video_concept_name][0][0]
                    target_concept['end_sent_id'] = video_in_depths[video_concept_name][-1][0]
                    target_concept['creator'] = 'Video_Analysis'
                    break
                
            if not most_proximal['found']:
                burst_concepts.append({ 'concept':video_concept_name,
                                        'start_sent_id':video_in_depths[video_concept_name][0][0],
                                        'end_sent_id':video_in_depths[video_concept_name][-1][0],
                                        'start':seconds_to_h_mm_ss_dddddd(video_in_depths[video_concept_name][0][1]['start']),
                                        'end':seconds_to_h_mm_ss_dddddd(video_in_depths[video_concept_name][-1][1]["end"]),
                                        'description_type':concept_description_type,
                                        'creator':'Video_Analysis'})
                if not concept_name in added_concepts:
                    added_concepts.append(concept_name)
                    
        return added_concepts,burst_concepts

    def reconstruct_slides_from_times_set(self):
        '''
        From the slides_startends previously set, reads the text in the first frame for each slide and converts it into TimedAndFramedText
        '''
        assert self._slide_startends is not None, "Must firstly load (set) startend frames read from database to run this function"
        slide_startends = self._slide_startends
        frame = ImageClassifier(image_and_scheme=[None,COLOR_BGR])
        loc_video = LocalVideo(self._video_id)
        TFT_list = []
        for slide_start_seconds,slide_end_seconds in slide_startends:
            slide_frames_startend = (loc_video.get_num_frame_from_time(slide_start_seconds),loc_video.get_num_frame_from_time(slide_end_seconds))
            loc_video.set_num_frame(slide_frames_startend[0])
            frame.set_img(loc_video.extract_next_frame())
            text_extracted = frame.extract_text(return_text=True,with_contours=True)
            TFT_list.append(TimedAndFramedText(text_extracted,[slide_frames_startend]))
        self._text_in_video = TFT_list
        


    def set(self,video_slidishness=None,slidish_frames_startend=None,slide_startends=None,titles=None):
        '''
        Set parameters at various steps:
            - video_slidishness : percentage of slide frames overall
            - slidish_frames_startend : list of timeframes of probably slides computed after the preprocess
            - slide_startends : list of timeframes of the exact slides
            - titles : list of TimedAndFramedTexts that represent titles of their respective slides
        '''
        if video_slidishness is not None:
            self._video_slidishness = video_slidishness
        if slidish_frames_startend is not None:
            self._frames_to_analyze = slidish_frames_startend
        if slide_startends is not None:
            self._slide_startends = slide_startends
        if titles is not None:
            self._slide_titles = titles
        return self

def _debug_write_on_file(text,mode):
    return
    import os
    # Look for your absolute directory path
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    filew = open(absolute_path+"/logging_segmentation.txt",mode)
    filew.write(text)
    filew.close()

def run_one_segmentation_job(video_id):
    _debug_write_on_file("started runjobs\n","w")
    vid_analyzer = VideoAnalyzer(video_id)
    if not vid_analyzer.can_be_analyzed(LocalVideo(video_id)):
        _debug_write_on_file("cant be analyzed\n","a")
        segmentation_data = {'video_id':video_id,'video_slidishness':0.0,'slidish_frames_startend':[]}
    else: 
        # if there's no data in the database check the video slidishness
        video_slidishness,slide_frames = vid_analyzer.is_slide_video(return_value=True,return_slide_frames = True)
        _debug_write_on_file("video slidishness "+str(video_slidishness)+"\n","a")
        # prepare data for upload
        segmentation_data = {'video_id':video_id,'video_slidishness':video_slidishness,'slidish_frames_startend':slide_frames}
        if vid_analyzer.is_slide_video():
            # if it's classified as a slides video analyze it and insert results in the structure that will be uploaded online
            _debug_write_on_file("gonna analyze video\n","a")
            vid_analyzer.analyze_video()
            _debug_write_on_file("video Analyzed!\n","a")
            results = vid_analyzer.extract_titles()
            #from pprint import pprint
            #pprint(results)
            # insert titles data in the structure that will be loaded on the db
            segmentation_data = {**segmentation_data, 
                                 **{'slide_titles':[{'start_end_seconds':start_end_seconds,'text':title,'xywh_normalized':bb} for (title,start_end_seconds,bb) in results] if results is not None else [],
                                    'slide_startends': vid_analyzer.get_extracted_text(format='set[times]')}}
    db_mongo.insert_video_text_segmentation(segmentation_data)
    _debug_write_on_file("Done\n","a")

def _run_jobs(queue):
    '''
    Periodically checks if the segmentation queue is empty, if not it starts a segmentation and runs it until the end\n
    if it's empty it goes to sleep to avoid cpu usage 
    '''
    _debug_write_on_file("started runjobs\n","w")
    #db_mongo.open_socket()
    while True:
        print(" Scheduler says: No jobs",end="\r")
        if len(queue) > 0:
            
            _debug_write_on_file("queue has a job\n","a")
            
            # Ensuring video has to be analyzed (is not already present in mongo) to prevent looping through the same video cliecked by the user
            # in a short amount of time
            video_id = queue.pop(0)
            video_has_to_be_analyzed = db_mongo.get_video_segmentation(video_id,raise_error=False) is None

            while not video_has_to_be_analyzed and len(queue) > 0:
                video_id = queue.pop(0)
                video_has_to_be_analyzed = db_mongo.get_video_segmentation(video_id,raise_error=False) is None

            if video_has_to_be_analyzed:
                _debug_write_on_file("segm job on "+video_id+"\n","a")

                print("Segmentation job on "+video_id+" starts  working...")
                vid_analyzer = VideoAnalyzer(video_id)
                if not vid_analyzer.can_be_analyzed(LocalVideo(video_id)):
                
                    _debug_write_on_file("cant be analyzed\n","a")

                    segmentation_data = {'video_id':video_id,'video_slidishness':0.0,'slidish_frames_startend':[]}
                else: 
                    # if there's no data in the database check the video slidishness
                    video_slidishness,slide_frames = vid_analyzer.is_slide_video(return_value=True,return_slide_frames = True)
                    _debug_write_on_file("video slidishness "+str(video_slidishness)+"\n","a")
                    # prepare data for upload
                    segmentation_data = {'video_id':video_id,'video_slidishness':video_slidishness,'slidish_frames_startend':slide_frames}
                    if vid_analyzer.is_slide_video():
                        # if it's classified as a slides video analyze it and insert results in the structure that will be uploaded online
                        _debug_write_on_file("gonna analyze video\n","a")
                        vid_analyzer.analyze_video()
                        _debug_write_on_file("video Analyzed!\n","a")
                        results = vid_analyzer.extract_titles()

                        #from pprint import pprint
                        #pprint(results)

                        # insert titles data in the structure that will be loaded on the db
                        segmentation_data = {**segmentation_data, 
                                             **{'slide_titles':[{'start_end_seconds':start_end_seconds,'text':title,'xywh_normalized':bb} for (title,start_end_seconds,bb) in results] if results is not None else [],
                                                'slide_startends': vid_analyzer.get_extracted_text(format='set[times]')}}
                db_mongo.insert_video_text_segmentation(segmentation_data)
                _debug_write_on_file("video pushed on db!!\n","a")
                print(f"Job on {video_id} done!"+" "*20)
        time.sleep(10)

def workers_queue_scheduler(queue):
    '''
    Creates a separated process that runs the segmentation of every video in the queue
    '''
    from threading import Thread
    Thread(target=_run_jobs,args=(queue,)).start()    


def _test_and_save_segment_video(vid_id):
    video = VideoAnalyzer(vid_id)
    try:
        segmentation_data = db_mongo.get_video_segmentation(vid_id)
        video.set(segmentation_data['video_slidishness'],segmentation_data['slidish_frames_startend'])
        if video.is_slide_video():
            video.set(slide_startends = segmentation_data['slide_startends'])
            video.reconstruct_slides_from_times_set()
            pprint(video.extract_titles())
    except Exception as e:
        print("Error: ")
        print(e)

        # Pre-process the video
        video_slidishness,slide_frames = video.is_slide_video(return_slide_frames=True,return_value=True,_show_info=True)
        segmentation_data = {'video_id':vid_id,'video_slidishness':video_slidishness,'slidish_frames_startend':slide_frames}

        # Analyze the video
        video.analyze_video(_show_info=True)
        segmentation_data = {**segmentation_data,
                             **{'slide_startends': video.get_extracted_text(format='set[times]'),
                                'slide_titles':[{'start_end_seconds':start_end_seconds,
                                                 'text':title,
                                                 'xywh_normalized':bb} 
                                                 for (title,start_end_seconds,bb) in video.extract_titles()]}}
        db_mongo.insert_video_text_segmentation(segmentation_data,update=True)


def _main_in_segmentation():
    # NOTE to test the analysis must set _debug to true otherwise it tries to check if there's a flask session running in order to validate the execution
    #vid_id = 'eVjQXLEX-78'

    # FOR TEST
    # WEAK_POINT not performing fast with long videos or text that composes character by character each frame 
    #video = VideoAnalyzer('yN7ypxC7838')
    #video = VideoAnalyzer('g8w-IKUFoSU') #infants and juveniles forensic
    video = VideoAnalyzer('PPLop4L2eGk') #introduction to ML
    #video = VideoAnalyzer('UuzKYffpxug') #estimating stature forensic
    #video = VideoAnalyzer('ujutUfgebdo')
    
    #video = VideoAnalyzer('sXLhYStO0m8') #sexing skeleton 1
    #video = VideoAnalyzer('rFRO8IwB8aY') # Lesson Med 33 minutes low score and very slow
    #vid_id = "6leS5eEO2N8"
    vid_id = "GdPVu6vn034"
    video = VideoAnalyzer(vid_id)
    video.analyze_video(_show_info=True)
    #segmentation_data = db_mongo.get_video_segmentation(vid_id)
    #video.set(video_slidishness=segmentation_data["video_slidishness"],slide_startends=segmentation_data["slide_startends"])
    #video.reconstruct_slides_from_times_set()
    results = video.extract_titles()
    print(results)
    return

    # print results
    image = ImageClassifier(image_and_scheme=[None, COLOR_BGR])
    video_ref = LocalVideo(vid_id)
    from matplotlib import pyplot as plt
    fig, ax = plt.subplots(nrows=ceil(len(results)/3),ncols=3, figsize=(16,9))
    j = 0
    for (title,start_end_seconds,bb) in results:
        axis = ax[floor(j/3),j%3]
        video_ref.set_num_frame(video_ref.get_num_frame_from_time(start_end_seconds[0]))
        title = title.rstrip('\n')
        axis.set_title(f"'Title: {title}'\nstart frame: {video_ref.get_num_frame_from_time(start_end_seconds[0])}   time: {start_end_seconds[0]}")
        image.set_img(draw_bounding_boxes_on_image(video_ref.extract_next_frame(),[bb]))
        image._debug_show_image(axis)
        j+=1

    plt.show()

if __name__ == '__main__':
    _main_in_segmentation()
    #vid_id = "JDmNvQj0I5A"
    #segmentation_data = db_mongo.get_video_segmentation(vid_id)
    #video = VideoAnalyzer(vid_id)
    #video.set(segmentation_data['video_slidishness'],segmentation_data['slidish_frames_startend'])
    #video.set(slide_startends = segmentation_data['slide_startends'])
    #video.reconstruct_slides_from_times_set()
    #video.set(titles=segmentation_data["slide_titles"])
    #video.adjust_or_insert_definitions_and_indepth_times(None)
    #_test_and_save_segment_video(vid_id)