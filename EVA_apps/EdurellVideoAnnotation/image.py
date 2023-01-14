import cv2
import pytesseract

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



import mediapipe as mp
import numpy as np
from dataclasses import dataclass

@dataclass
class ImageClassificator:
    
    """
    Classifies an image based on objects found in it

    Arguments:
        image: the image already in RGB mode

    """
    image = None
    text_contours = None
    face_results = None
    _mp_face_detection = mp.solutions.face_detection

    def detect_faces(self, model=1,min_conf=0.5) -> bool:
        with self._mp_face_detection.FaceDetection(model_selection=model, min_detection_confidence=min_conf) as face_detection:
            self.face_results = face_detection.process(self.image)
            return bool(self.face_results.detections)


    def detect_text(self):
        self.text_contours = extract_text(self.image)
        return bool(self.text_contours)

    def get_text(self, with_contours=False):
        if with_contours:
            return self.text_contours
        return [elem[0] for elem in self.text_contours]

    def get_stat_params(self):
        if self.image is not None:
            flatten = self.image.flatten()
            return (np.mean(flatten),np.var(flatten))
        return None
    
    def is_empty_transition_image(self,var_threshold=1e-2):
        if self.image is not None:
            return self.get_stat_params()[1] < var_threshold

    def get_hists(self):
        img = self.image
        if not img is None:
            histR = cv2.calcHist([img],channels=[0],mask=None,histSize=[256],ranges=[0,256])
            histG = cv2.calcHist([img],channels=[1],mask=None,histSize=[256],ranges=[0,256])
            histB = cv2.calcHist([img],channels=[2],mask=None,histSize=[256],ranges=[0,256])
            return [histR,histG,histB]
        return None

    def replace_img(self,img):
        self.image = img
        self.words_results = None
        self.words_results = None
        self.text_contours = None
        return self
    
    def get_img(self, text_bounding_boxes=False):
        if not text_bounding_boxes or not self.words_results:
            return self.image
        return draw_bounding_boxes(self.image,self.text_contours)
        #return _draw_bounding_boxes(self.image, self.words_results)
        

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
    