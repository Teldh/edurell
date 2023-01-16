import cv2
import pytesseract
from audio_transcription import get_youtube_cap
import os

import mediapipe as mp
import numpy as np


class ImageClassificator:
    
    """
    Wraps an image and finds patterns in it

    Arguments:
        image: the image in RGB or GRAYSCALE mode

    """

    text_contours = None
    face_results = None
    _mp_face_detection = mp.solutions.face_detection
    
    def __init__(self,image=None, image_shape=None) -> None:
        if image_shape is not None:
            self._image = np.zeros(image_shape, dtype=np.uint8)
        elif image is not None:
            self._image = image

    def detect_faces(self, model=1,min_conf=0.5) -> bool:
        with self._mp_face_detection.FaceDetection(model_selection=model, min_detection_confidence=min_conf) as face_detection:
            self.face_results = face_detection.process(self._image)
            return bool(self.face_results.detections)

    def detect_text(self,return_text=False,with_contours=False):
        '''
        search and save text internally 
        get_text() to obtain it
        returns True if text has been found
        '''
        self.text_contours = extract_text(self._image)
        if return_text and with_contours:
            return self.text_contours
        elif return_text and not with_contours:
            return [elem[0] for elem in self.text_contours]
        return bool(self.text_contours)

    def get_text(self, with_contours=False):
        '''
        Returns the already found text
        '''
        

    def get_stat_params(self):
        if self._image is not None:
            flatten = self._image.flatten()
            return (np.mean(flatten),np.var(flatten))
        return None
    
    def is_empty_transition_image(self,var_threshold=1e-2):
        if self._image is not None:
            return self.get_stat_params()[1] < var_threshold

    def get_hists(self):
        img = self._image
        if not img is None:
            num_colors = self.get_num_colors()
            hists = np.zeros((num_colors,256),dtype='f')
            for channel in range(num_colors):
                hists[channel,:] = cv2.calcHist([img],channels=[channel],mask=None,histSize=[256],ranges=[0,256]).T/(np.prod(img.shape))
            return hists
        return None
    
    def get_img(self, text_bounding_boxes=False):
        if not text_bounding_boxes or not self.words_results:
            return self._image
        return draw_bounding_boxes(self._image,self.text_contours)

    def get_num_colors(self):
        return 1 if len(self._image.shape) == 2 or self._image.shape[-1] == 1 else 3

    def set_img(self,img):
        self._image = img
        self.words_results = None
        self.words_results = None
        self.text_contours = None
        return self




def color_histogram_on_clusters(video_url, cluster_starts, cluster_ends, S, seconds_range):
    """
    Take a list of clusters and compute the color histogram on end and start of the cluster
    :param video_url: video url from youtube
    :param cluster_list
    :param S: scala per color histogram
    :param seconds_range: aggiustare inizio e fine dei segmenti in base a differenza nel color histogram
    """

    if "watch?v=" in video_url:
        video_id = video_url.split("?v=")[-1]
        #print(video_id)
        #video_id = video_url.split('&')[0].split("=")[1]
    else:
        video_id = video_url.split("/")[-1]
    #video_id = video_url.split('&')[0].split("=")[1]

    current_path = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(current_path, "static", "videos", video_id, video_id + ".mp4")
    #cap = get_youtube_cap(video_url)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        video_path = video_path.replace(".mp4",".mkv")
        cap = cv2.VideoCapture(video_path)
    print(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("fps:", fps)

    # cluster_ends = []
    # cluster_starts = []
    # for c in cluster_list:
    #     cluster_ends.append(int(c.end_time * fps))
    #     cluster_starts.append(int(c.start_time * fps))


    #prendo frame iniziali e finali dei segmenti
    cluster_frame_ends = []
    cluster_frame_starts = []
    for i, c in enumerate(cluster_starts):
        cluster_frame_ends.append(int(cluster_ends[i] * fps))
        cluster_frame_starts.append(int(cluster_starts[i] * fps))

    print("PRIMA:")
    print(cluster_frame_starts)
    print(cluster_frame_ends)
    print()

    frame_number = 0
    summation = 0
    frame_to_skip = int(fps)* 10 #guardo un frame al secondo

    previous_hist = []
    all_diffs = []
    images_path = []

    '''Calcolo le dif per trovare threshold con la formula '''
    print("Histograms Progress: ", end="")
    while cap.isOpened():

        ret, current_frame = cap.read()
        cap.set(1, frame_number)

        if ret:
            current_frame = cv2.resize(current_frame, (240, 180))

            image = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
            hist = cv2.calcHist([image], [0], None, [32], [0, 128])
            hist = cv2.normalize(hist, hist)

            if frame_number > 0:

                diff = 0
                for i, bin in enumerate(hist):
                    diff += abs(bin[0] - previous_hist[i][0])
                all_diffs.append(diff)
                summation += diff

            frame_number += frame_to_skip
            previous_hist = hist

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break
            
    cap.release()
    threshold = S * (summation / frame_number)

    '''
    Controllo se c'è un cambio scena in un intorno di "seconds_range" frames dalla fine ed inizio di ciascun cluster.
    '''

    start_changes = []
    end_changes = []

    for end in cluster_frame_ends:
        change_found = False
        for i in range(seconds_range):
            end_diff = int(end / frame_to_skip)

            if end_diff + i < len(all_diffs) and all_diffs[end_diff + i] > threshold:
                sec = (end + i) / fps
                end_changes.append(sec)
                change_found = True
                break

        if not change_found:
            end_changes.append(-1)



    for j, start in enumerate(cluster_frame_starts):
        change_found = False
        for i in range(seconds_range):
            start_diff = int(start/frame_to_skip)

            if start_diff - i >= 0 and all_diffs[start_diff - i] > threshold:
                sec = (start - i) / fps
                start_changes.append(sec)
                change_found = True
                break

        if not change_found:
            start_changes.append(-1)



    # for i, c in enumerate(cluster_list):
    #     if start_changes[i] != -1:
    #         c.start_time = start_changes[i]
    #     if end_changes[i] != -1:
    #         c.end_time = end_changes[i]

    for i, c in enumerate(cluster_starts):
        if start_changes[i] != -1:
            cluster_starts[i] = start_changes[i]
        if end_changes[i] != -1:
            cluster_ends[i] = end_changes[i]

        cluster_starts[i] = round(cluster_starts[i], 2)
        cluster_ends[i] = round(cluster_ends[i], 2)

    print(cluster_starts)

    # salvo immagini da mostrare nella timeline
    cap = get_youtube_cap(video_url)

    for i, start in enumerate(cluster_frame_starts):

        cap.set(1, start)
        ret, current_frame = cap.read()

        current_path = os.path.dirname(os.path.abspath(__file__))
        image_name = str(i) #str(cluster_starts[i]).replace(".","_")

        saving_position = os.path.join(current_path, "static", "videos", video_id, image_name + ".jpg")
        print(saving_position)
        #saving_position = "videos\\" + video_id + "\\" + str(start) + ".jpg"
        cv2.imwrite(saving_position, current_frame)
        images_path.append("videos/" + video_id + "/" + image_name + ".jpg")

    cap.release()
    #print(images_path)
    ''' Ritorno le path delle immagini della timeline'''
    return images_path, cluster_starts, cluster_ends


from numpy import round, dot, zeros
from numpy.linalg import norm

def cosine_similarity(image1:ImageClassificator,image2:ImageClassificator):
    assert image1.get_img().shape == image2.get_img().shape
    hists1 = image1.get_hists()
    hists2 = image2.get_hists()
    cv2.normalize(hists1,hists1)
    cv2.normalize(hists2,hists2)
    num_colors = hists1.shape[0]
    cosine_sim = zeros((1,num_colors),dtype='f')
    for color in range(num_colors):
        A = hists1[color,:]
        B = hists2[color,:]
        cosine_sim[0,color] = round(dot(A,B)/(norm(A)*norm(B)),decimals=4)
    return cosine_sim


def draw_bounding_boxes(img, contours):
    img = img.copy()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        img=cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
    return img


def extract_text(img):
    img = img.copy()
    img_bw = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    ret, img_thresholded = cv2.threshold(img_bw, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
    img_dilated = cv2.dilate(img_thresholded, rect_kernel, iterations = 3)
    contours, hierarchy = cv2.findContours(img_dilated, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    text_contour = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        img_cropped = img[y:y + h, x:x + w]
        text = pytesseract.image_to_string(img_cropped)
        text = text.replace('\x0c','')
        if text:
            text_contour.append((text,[x,y,w,h]))
    return text_contour

        

import os
from words import extract_keywords, extract_title

if __name__ == '__main__':
    img = cv2.cvtColor(cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "svm_dataset","slide","PPLop4L2eGk_6.png")), cv2.COLOR_BGR2RGB)
    classif = ImageClassificator(img)
    print(classif.detect_faces())
    print(classif.detect_text())
    text = classif.get_text()
    print(f"text: {text}")
    for sentence in text:
        print(f"sentence: {sentence}")
        print(f"title: {extract_title(sentence)}")
        print(f"keywords: {extract_keywords(sentence)}")
        # TODO: edit segmentation.py to segment video frames
        # TODO: recognize same frames and transition images
    