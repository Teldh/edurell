from dataclasses import dataclass

@dataclass
class TimedAndFramedText:
    text: str
    frames_window: 'tuple[(int,int)]'
    xywh: 'tuple[(int,int,int,int)]'


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

from sentence_transformers import SentenceTransformer, util
from Cluster import create_cluster_list, aggregate_short_clusters
from audio_transcription import speech_from_youtube, get_timed_sentences
from image import color_histogram_on_clusters
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

video_quello_corto = "https://www.youtube.com/watch?v=qgCvnogeN2s"
video_quello_medio = "https://www.youtube.com/watch?v=0K2qhSTrXtE&ab_channel=DocSpotDocSpo"
video_quello_lungo = "https://www.youtube.com/watch?v=DHXwC0xt1hk&t"
video_quello_indexato = "https://www.youtube.com/watch?v=URtsnESYcPk&ab_channel=DerekBanas"

mooc_intro = "https://www.youtube.com/watch?v=KuMRk-arGAk&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV"
mooc_1 = "https://www.youtube.com/watch?v=sXLhYStO0m8&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=2"
mooc_2 = "https://www.youtube.com/watch?v=g8w-IKUFoSU&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=3"
mooc_3 = "https://www.youtube.com/watch?v=D4PGqxGWCT0&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=4"
mooc_4 = "https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5"
mooc_5 = "https://www.youtube.com/watch?v=wbqpzILKENI&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=6"

mooc = mooc_1

from video import LocalVideo

def frames_segmentation(video:LocalVideo):
    return None
#TODO copy from video __main__


def segmentation(video:str, c_threshold, sec_min, S, frame_range, subtitles, video_id):
    """
    :param video: youtube url
    :param c_threshold: threshold per la similarità tra frasi
    :param sec_min: se un segmento è minore di sec_min verrà unito con il successivo
    :param S: scala per color histogram
    :param frame_range: aggiustare inizio e fine dei segmenti in base a differenza nel color histogram nel frame_range
    :return: segments
    """

    video_id = video.split('&')[0].split("=")[1]

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

        rete = os.path.join(os.path.dirname(os.path.abspath(__file__)), "punctuator", "Demo-Europarl-EN.pcl")
        print(rete)
        p = Punctuator(rete)
        punctuated_transcription = p.punctuate(transcription)

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
        images_path, start_times, end_times = color_histogram_on_clusters(video, start_times, end_times, S, frame_range)
    else:
        print("keyframes already present")
        images = []
        for File in os.listdir(path):
            if File.endswith(".jpg"):
                images.append(File.split(".")[0])

        images.sort(key=int)
        images_path = ["videos/" + video_id + "/" + im + ".jpg" for im in images]



    return start_times, end_times, images_path, punctuated_transcription


if __name__ == '__main__':
    segmentation("https://www.youtube.com/watch?v=TpcbfxtdoI8", 0.19, 20, 1, 375)
    #segmentation("https://www.youtube.com/watch?v=KkgkZwQ9HgQ", 0.22, 40, 1, 375)