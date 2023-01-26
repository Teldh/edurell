from dataclasses import dataclass

@dataclass
class TimedAndFramedText:
    text: str
    start_end_frames: 'list[tuple[(int,int)]]'
    xywh: 'tuple[(int,int,int,int)]'
    
    def __lt__(self, other:'TimedAndFramedText'):
        self.start_end_frames[-1][1] < other.start_end_frames[0][0]


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

class PunctuatorSingleton:

    def __init__(self) -> None:
        self._punctuator = Punctuator(os.path.join(os.path.dirname(os.path.abspath(getfile(self.__class__))), "punctuator", "Demo-Europarl-EN.pcl"))

    def punctuate(self,text:str) -> 'list[(str)]':
        return self._punctuator.punctuate(text)

from video import LocalVideo

def frames_segmentation(video:LocalVideo):
    return None
#TODO copy from video __main__

from youtube_transcript_api import YouTubeTranscriptApi as YTTranscriptApi
from math import floor, log2
from numpy import clip

class Segmentator:

    def __init__(self,video_id:str,from_youtube:bool=True,load_video=True) -> None:
        if from_youtube:
            self._video_id = video_id
            self._transcripts = YTTranscriptApi.list_transcripts(video_id)
            if load_video:
                self._video = LocalVideo(video_id)
        else:
            raise Exception("not implemented!")
    
    def get_transcript(self,lang:str='en'):
        autogenerated = False
        try:
            transcript = self._transcripts.find_manually_created_transcript([lang])
        except:
            transcript = self._transcripts.find_generated_transcript([lang])
            autogenerated = True

        subs_dict = []
        for sub in transcript.fetch():

            subs_dict.append(
                {"text": sub["text"],
                 "start": sub["start"],
                 "end": sub["start"] + sub["duration"]}
            )

        return subs_dict, autogenerated
    
    #def load_video(self):
    #    video = LocalVideo(self._video_id)
    #    self._video = video
    #    return video
    
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
            punct = PunctuatorSingleton()
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
            print("Clusters done")

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
            images_path, start_times, end_times = self._video.create_keyframes(start_times, end_times, S, frame_range)
        else:
            print("keyframes already present")
            images = []
            for File in os.listdir(path):
                if File.endswith(".jpg"):
                    images.append(File.split(".")[0])

            images.sort(key=int)
            images_path = ["videos/" + video_id + "/" + im + ".jpg" for im in images]

        return start_times, end_times, images_path, punctuated_transcription

    def video_segmentation(self):

        class CongestionManager:
            '''
            LocalVideo wrapper
            Based on "TCP fast retransmit and fast recovery"
            
            :param vid_ref = reference to the video
            '''
            def __init__(self,vid_ref:LocalVideo,exp_base=1.1,lin_factor=2,max_exp_window_seconds=4,ratio_lin_exp_window_size=2):
                self.vid_ref = vid_ref
                self._curr_window_frame_size:int = 1
                vid_ref.set_sample_rate(1)
                self._curr_x = 1
                self._max_exp_window_frame_size = floor(vid_ref.get_fps()*max_exp_window_seconds)
                self._max_lin_window_frame_size = max_exp_window_seconds*ratio_lin_exp_window_size
                self._base = exp_base
                self._m = lin_factor
                self._y0_lin = self._max_exp_window_frame_size-lin_factor*(log2(self._max_lin_window_frame_size)/log2(exp_base))
                self._is_cong_avoid = False
                self._is_collided = False
            
            def _exp_step(self,value:int):
                return self._base**value
            
            def _lin_step(self,value:int):
                return self._m*value + self._y0_lin

            def get_video(self):
                return self.vid_ref

            def make_step_and_get_next_frame(self) -> bool:
                '''
                Returns next frame (or none if video ended) and true if max frame size is reached
                '''
                next_offset = 1
                if not self._is_collided:
                    if not self._is_cong_avoid:
                        # exponential step
                        next_offset = clip(self._exp_step(self._curr_x),1,self._max_exp_window_frame_size)
                        if next_offset == self._max_exp_window_frame_size:
                            self._is_cong_avoid = True
                    elif self._is_cong_avoid:
                        # linear step
                        next_offset = clip(self._lin_step(self._curr_x),1,self._max_lin_window_frame_size)
                    self._curr_x += 1
                self._curr_window_frame_size = int(next_offset)
                self.vid_ref.set_sample_rate(next_offset)
                return self.vid_ref.next_frame()

            def collision(self):
                rollback_steps = self._curr_window_frame_size
                video = self.vid_ref

                self.vid_ref.rewind_video(self.vid_ref.get_num_curr_frame()-self._curr_window_frame_size)
                self._is_collided = True

            #def still_colliding(self,contraction_coeff=0.999):
            #    self._curr_x *= contraction_coeff 

            def end_collision(self):
                self._is_collided = False
                self._curr_x = 1

        cm = CongestionManager(self._video)


if __name__ == '__main__':
    segmentator = Segmentator('PPLop4L2eGk')
    subtitles, autogenerated = segmentator.get_transcript()
    # segment the video with semantic similarity
    print("Entering segmentation")
    start_times, end_times, images_path, text = segmentator.transcript_segmentation(subtitles, 0.22, 35, 1, 15)
    print(text)
    print("exit segmentation")
    #segmentation("https://www.youtube.com/watch?v=TpcbfxtdoI8", 0.19, 20, 1, 375)
    #segmentation("https://www.youtube.com/watch?v=KkgkZwQ9HgQ", 0.22, 40, 1, 375)