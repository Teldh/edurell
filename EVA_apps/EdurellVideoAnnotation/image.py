import cv2
import pytesseract
import os

import mediapipe as mp
import numpy as np
from numpy.linalg import norm

class ImageClassificator:
    
    """
    Wraps an image to find patterns in it

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
        else:
            self._image = None

    def detect_faces(self, model=1,min_conf=0.5) -> bool:
        with self._mp_face_detection.FaceDetection(model_selection=model, min_detection_confidence=min_conf) as face_detection:
            self.face_results = face_detection.process(self._image)
            return bool(self.face_results.detections)

    def detect_text(self,only_title=False,return_text=False,with_contours=False):
        '''
        search and save text internally
        returns True if text has been found
        '''
        if self._image is not None:
            self.text_contours = extract_text(self._image, only_title)
            if return_text and with_contours:
                return self.text_contours
            elif return_text and not with_contours:
                return [elem[0] for elem in self.text_contours]
            return bool(self.text_contours)
        return False

    def get_detected_text(self, with_contours=False):
        if self.text_contours is not None:
            if with_contours:
                return self.text_contours
            else:
                return [elem[0] for elem in self.text_contours]
        return None

    def get_max_size_text(self, return_index = False):
        texts_with_contour = self.text_contours
        if texts_with_contour is not None:
            max_index = -1
            max_norm = -1
            for indx, text_with_contour in enumerate(texts_with_contour):
                curr_norm = norm(np.array([text_with_contour[1][2],text_with_contour[1][3]]))
                if max_norm < curr_norm:
                    max_index = indx
                    max_norm = curr_norm
            if not return_index:
                return [texts_with_contour[max_index]]
            else:
                return max_index, texts_with_contour[max_index][0]
        if not return_index:
            return None
        else:
            return -1, None

    def get_smaller_text(self):
        texts_with_contour = self.text_contours.copy()
        texts_with_contour.remove(self.get_max_size_text(return_index=True)[0])
        return [elem[0] for elem in texts_with_contour]

    def get_min_size_text(self):
        texts_with_contour = self.text_contours
        if texts_with_contour is not None:
            min_index = -1
            min_norm = np.inf
            for indx, text_with_contour in enumerate(texts_with_contour):
                curr_norm = norm(np.array([text_with_contour[1][2],text_with_contour[1][3]]))
                if min_norm > curr_norm:
                    min_index = indx
                    min_norm = curr_norm
            return [texts_with_contour[min_index][0]]
        return None

    def get_stat_params(self):
        if self._image is not None:
            flatten = self._image.flatten()
            return (np.mean(flatten),np.var(flatten))
        return (0,0)
    
    def is_empty_transition_image(self,var_threshold=1e-2):
        return self.get_stat_params()[1] < var_threshold

    def get_cosine_similarity(self,other_image:'ImageClassificator',on_histograms=True,rounding_decimals:int= 8):
        '''
        Compute cosine similarity between two images histograms, if not on_histograms 
        it computes between pixel value and position (may be faster)
        '''
        if self._image is None:
            return 0
        assert self._image.shape == other_image._image.shape
        round = np.round; norm = np.linalg.norm; dot = np.dot; diag = np.diag
        
        if on_histograms:   # looks like it's faster
            this_mat = self.get_hists()
            other_mat = other_image.get_hists()
            cv2.normalize(this_mat,this_mat)
            cv2.normalize(other_mat,other_mat)
        else:
            img_shape = self._image.shape
            if len(img_shape) == 3 and img_shape[2] == 3:
                this_mat_uint8 = np.reshape(self._image, (img_shape[0]*img_shape[1],img_shape[2]))
                other_mat_uint8 = np.reshape(other_image._image, (img_shape[0]*img_shape[1],img_shape[2]))
            else:
                this_mat_uint8 = np.reshape(self._image, (1,img_shape[0]*img_shape[1])).astype(np.float32,copy=False)
                other_mat_uint8 = np.reshape(other_image._image, (1,img_shape[0]*img_shape[1])).astype(np.float32,copy=False)
            this_mat = np.zeros(this_mat_uint8.shape,dtype='f')
            other_mat = this_mat.copy()
            cv2.normalize(this_mat_uint8,this_mat)
            cv2.normalize(other_mat_uint8,other_mat)
        cosine_sim = round( diag(dot(this_mat,other_mat.T))/(norm(this_mat,axis=1)*norm(other_mat,axis=1)), 
                            decimals=rounding_decimals)
        return cosine_sim


    def get_hists(self):
        '''
        generate image histogram
        '''
        img = self._image
        if not img is None:
            num_colors = 1 if len(self._image.shape) == 2 or self._image.shape[-1] == 1 else 3
            hists = np.zeros((num_colors,256),dtype='f')
            for channel in range(num_colors):
                hists[channel,:] = cv2.calcHist([img],channels=[channel],mask=None,histSize=[256],ranges=[0,256]).T/(np.prod(img.shape))
            return hists
        return None
    
    def get_img(self, text_bounding_boxes=False):
        if not text_bounding_boxes or not self.text_contours:
            return self._image
        return draw_bounding_boxes(self._image,[elem[1] for elem in self.text_contours])

    def set_img(self,img):
        self._image = img
        self.text_contours = None
        return self


def draw_bounding_boxes(img, contours:'list[tuple[(int,int,int,int)]]'):
    img = img.copy()
    img.flags.writeable = True
    for xywh in contours:
        x = xywh[0]; y = xywh[1]; w = xywh[2]; h = xywh[3]
        img=cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
    img.flags.writeable = False
    return img


def extract_text(img,only_title:bool):
    '''RGB or GRAYSCALED with grayscaled'''
    img_bw = img.copy()
    img_bw.flags.writeable = True
    if len(img.shape) > 2 and img.shape[2] == 3:
        img_bw = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    ret, img_thresholded = cv2.threshold(img_bw, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
    img_dilated = cv2.dilate(img_thresholded, rect_kernel, iterations = 3)
    contours, hierarchy = cv2.findContours(img_dilated, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    texts_with_contour = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        img_cropped = img[y:y + h, x:x + w]
        text = pytesseract.image_to_string(img_cropped)
        text = text.replace('\x0c','').lstrip().rstrip()
        if text:
            texts_with_contour.append((text,(x,y,w,h)))
    if only_title and len(texts_with_contour) > 0:
        max_index = -1
        max_norm = -1
        for indx, text_with_contour in enumerate(texts_with_contour):
            curr_norm = norm(np.array([text_with_contour[1][2],text_with_contour[1][3]]))
            if max_norm < curr_norm:
                max_index = indx
                max_norm = curr_norm
        return [texts_with_contour[max_index]]

    return texts_with_contour

        

import os
#from words import extract_keywords, extract_title

if __name__ == '__main__':
    img = cv2.cvtColor(cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "svm_dataset","slide","PPLop4L2eGk_6.png")), cv2.COLOR_BGR2RGB)
    classif = ImageClassificator(img)
    print(classif.detect_faces())
    text = classif.detect_text(return_text=True)
    print(f"text: {text}")
    #for sentence in text:
    #    print(f"sentence: {sentence}")
    #    print(f"title: {extract_title(sentence)}")
    #    print(f"keywords: {extract_keywords(sentence)}")  



#UNUSED
#def color_histogram_on_clusters(video_url, cluster_starts, cluster_ends, S, seconds_range):
#    """
#    Take a list of clusters and compute the color histogram on end and start of the cluster
#    :param video_url: video url from youtube
#    :param cluster_list
#    :param S: scala per color histogram
#    :param seconds_range: aggiustare inizio e fine dei segmenti in base a differenza nel color histogram
#    """
#
#    if "watch?v=" in video_url:
#        video_id = video_url.split("?v=")[-1]
#        #print(video_id)
#        #video_id = video_url.split('&')[0].split("=")[1]
#    else:
#        video_id = video_url.split("/")[-1]
#    #video_id = video_url.split('&')[0].split("=")[1]
#
#    current_path = os.path.dirname(os.path.abspath(__file__))
#    video_path = os.path.join(current_path, "static", "videos", video_id, video_id + ".mp4")
#    #cap = get_youtube_cap(video_url)
#    cap = cv2.VideoCapture(video_path)
#    if not cap.isOpened():
#        video_path = video_path.replace(".mp4",".mkv")
#        cap = cv2.VideoCapture(video_path)
#    print(video_path)
#    fps = cap.get(cv2.CAP_PROP_FPS)
#    print("fps:", fps)
#
#    # cluster_ends = []
#    # cluster_starts = []
#    # for c in cluster_list:
#    #     cluster_ends.append(int(c.end_time * fps))
#    #     cluster_starts.append(int(c.start_time * fps))
#
#
#    #prendo frame iniziali e finali dei segmenti
#    cluster_frame_ends = []
#    cluster_frame_starts = []
#    for i, c in enumerate(cluster_starts):
#        cluster_frame_ends.append(int(cluster_ends[i] * fps))
#        cluster_frame_starts.append(int(cluster_starts[i] * fps))
#
#    print("PRIMA:")
#    print(cluster_frame_starts)
#    print(cluster_frame_ends)
#    print()
#
#    frame_number = 0
#    summation = 0
#    frame_to_skip = int(fps)* 10 #guardo un frame al secondo
#
#    previous_hist = []
#    all_diffs = []
#    images_path = []
#
#    '''Calcolo le dif per trovare threshold con la formula '''
#    print("Histograms Progress: ", end="")
#    while cap.isOpened():
#
#        ret, current_frame = cap.read()
#        cap.set(1, frame_number)
#
#        if ret:
#            current_frame = cv2.resize(current_frame, (240, 180))
#
#            image = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
#            hist = cv2.calcHist([image], [0], None, [32], [0, 128])
#            hist = cv2.normalize(hist, hist)
#
#            if frame_number > 0:
#
#                diff = 0
#                for i, bin in enumerate(hist):
#                    diff += abs(bin[0] - previous_hist[i][0])
#                all_diffs.append(diff)
#                summation += diff
#
#            frame_number += frame_to_skip
#            previous_hist = hist
#
#            if cv2.waitKey(1) & 0xFF == ord('q'):
#                break
#
#        else:
#            break
#            
#    cap.release()
#    threshold = S * (summation / frame_number)
#
#    '''
#    Controllo se c'è un cambio scena in un intorno di "seconds_range" frames dalla fine ed inizio di ciascun cluster.
#    '''
#
#    start_changes = []
#    end_changes = []
#
#    for end in cluster_frame_ends:
#        change_found = False
#        for i in range(seconds_range):
#            end_diff = int(end / frame_to_skip)
#
#            if end_diff + i < len(all_diffs) and all_diffs[end_diff + i] > threshold:
#                sec = (end + i) / fps
#                end_changes.append(sec)
#                change_found = True
#                break
#
#        if not change_found:
#            end_changes.append(-1)
#
#
#
#    for j, start in enumerate(cluster_frame_starts):
#        change_found = False
#        for i in range(seconds_range):
#            start_diff = int(start/frame_to_skip)
#
#            if start_diff - i >= 0 and all_diffs[start_diff - i] > threshold:
#                sec = (start - i) / fps
#                start_changes.append(sec)
#                change_found = True
#                break
#
#        if not change_found:
#            start_changes.append(-1)
#
#
#
#    # for i, c in enumerate(cluster_list):
#    #     if start_changes[i] != -1:
#    #         c.start_time = start_changes[i]
#    #     if end_changes[i] != -1:
#    #         c.end_time = end_changes[i]
#
#    for i, c in enumerate(cluster_starts):
#        if start_changes[i] != -1:
#            cluster_starts[i] = start_changes[i]
#        if end_changes[i] != -1:
#            cluster_ends[i] = end_changes[i]
#
#        cluster_starts[i] = round(cluster_starts[i], 2)
#        cluster_ends[i] = round(cluster_ends[i], 2)
#
#    #print(cluster_starts)
#
#    # salvo immagini da mostrare nella timeline
#    cap = get_youtube_cap(video_url)
#
#    for i, start in enumerate(cluster_frame_starts):
#
#        cap.set(1, start)
#        ret, current_frame = cap.read()
#
#        current_path = os.path.dirname(os.path.abspath(__file__))
#        image_name = str(i) #str(cluster_starts[i]).replace(".","_")
#
#        saving_position = os.path.join(current_path, "static", "videos", video_id, image_name + ".jpg")
#        print(saving_position)
#        #saving_position = "videos\\" + video_id + "\\" + str(start) + ".jpg"
#        cv2.imwrite(saving_position, current_frame)
#        images_path.append("videos/" + video_id + "/" + image_name + ".jpg")
#
#    cap.release()
#    #print(images_path)
#    ''' Ritorno le path delle immagini della timeline'''
#    return images_path, cluster_starts, cluster_ends