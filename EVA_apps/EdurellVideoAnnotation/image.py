import cv2
import pytesseract
import os

import mediapipe as mp
from mediapipe.framework.formats.detection_pb2 import Detection

from numpy import round, dot, diag, reshape, zeros, uint8, array, inf, mean, var, transpose, all, empty, abs
from numpy.linalg import norm
from enum import Enum
from typing_extensions import Literal

class ColorScheme(Enum):
    GRAY = cv2.COLOR_BGR2GRAY
    RGB = cv2.COLOR_BGR2RGB
    BGR = cv2.COLOR_BGR2GRAY + cv2.COLOR_BGR2RGB + 1

class _DistanceMeasMethods(Enum):
        COSINE_SIM = 0
        MEAN_ABSOLUTE_DIST = 1

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

class ImageClassifier:
    """
    Wraps an image to find patterns in it

    ----------
    Parameters:
    ----------
        image_and_scheme : a tuple of the image in RGB - BGR - GRAYSCALE mode and the color_scheme

        image_shape : alternatively can set shape of a total black image
    """

    _texts_with_contour:'list[tuple[str,tuple[int,int,int,int]]] | None' = None
    _faces:'list[Detection] | None' = None
    _threshold: 'tuple[float,float,float] or float or None'
    _comp_method:_DistanceMeasMethods or None
    
    def __init__(self,threshold:'tuple[float,float,float] or float or None'=None,comp_method:Literal['cos-sim','mean-abs-dist'] or None=None,image_and_scheme=None, image_shape=None) -> None:
        self._init_params_ = (threshold,comp_method,image_and_scheme,image_shape)
        if image_shape is not None:
            self._image = zeros(image_shape, dtype=uint8)
            self._color_scheme = None
        elif image_and_scheme is not None:
            self._image = image_and_scheme[0]
            self._color_scheme = image_and_scheme[1]
        else:
            self._image = None
            self._color_scheme = None
        self._threshold = threshold
        if comp_method == 'cos-dist':
            self._comp_method = _DistanceMeasMethods.COSINE_SIM.value
        else:
            self._comp_method = _DistanceMeasMethods.MEAN_ABSOLUTE_DIST.value

    def copy(self):
        '''
        makes copy of itself
        '''
        new_img = ImageClassifier(*self._init_params_)
        if self._image is not None:
            new_img._image = self._image
        return new_img

    def detect_faces(self, model:int=1, min_conf=0.2, return_contours=False):
        '''
        Search and save faces internally
        
        Parameters
        -----------
        
        model : int 0 for short range detection (2 meters from camera), 1 for long range detection (> 5 meters)
        min_conf: minimum confidence for the recognition

        Returns
        -----------
        True if at least one face has been found and return_contours is False
        otherwise returns the full array of contours for every face
        '''
        assert isinstance(model,int) and 0 <= model <= 1 and 0 <= min_conf <= 1
        if self._image is not None:
            with mp_face_detection.FaceDetection(model_selection=model, min_detection_confidence=min_conf) as face_detection:
                self._image.flags.writeable = False
                if self._color_scheme == ColorScheme.BGR:
                    self._image = cv2.cvtColor(self._image, cv2.COLOR_BGR2RGB)
                    self._faces = face_detection.process(self._image)
                    self._image.flags.writeable = True
                    self._image = cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR)
                else:
                    self._faces = face_detection.process(self._image)
                    self._image.flags.writeable = True
                if return_contours:
                    return self._faces.detections
                return bool(self._faces.detections)

    def detect_text(self,only_title=False,return_text=False,with_contours=False):
        '''
        Search and save text internally
        
        Returns
        -----------
        if only_title returns the text with biggest bounding boxes\n
        True if at least one face has been found and return_contours is False
        otherwise returns the full array of contours for every face
        '''
        assert self._image is not None and len(self._image.shape) == 3
        self._texts_with_contour = self._extract_text(only_title)
        if return_text and with_contours:
            return self._texts_with_contour
        elif return_text and not with_contours:
            return [elem[0] for elem in self._texts_with_contour]
        return bool(self._texts_with_contour)

    def draw_detected_faces(self):
        '''
        Draws detected faces on image and returns the image with contours
        '''
        assert self._faces is not None
        detections = self._faces
        image = self._image.copy()
        for detection in detections:
            mp_drawing.draw_detections(image, detection)
        return image

    def _extract_text(self, only_title:bool):
        '''
        RGB, BGR or GRAYSCALED but with len(image_shape) == 3 always
        '''
        img = self._image
        if self._color_scheme==ColorScheme.BGR:
            img_bw = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        elif self._color_scheme==ColorScheme.RGB:
            img_bw = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        else:
            img = self._image
            img = reshape(img,(img.shape[0],img.shape[1]))
            img_bw = img.copy()
        cv2.threshold(img_bw, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV,img_bw)
        cv2.dilate(img_bw, cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12)), img_bw,iterations = 3)
        
        contours, hierarchy = cv2.findContours(img_bw, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        texts_with_contour = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            img_cropped = img[y:y + h, x:x + w]
            text = pytesseract.image_to_string(img_cropped)
            text = text.replace('\x0c','').lstrip().rstrip()
            if text:
                texts_with_contour.append((text,(x,y,w,h)))
        # TODO improve
        if only_title and len(texts_with_contour) > 0: # finds max norm bounding boxes
            max_index = -1
            max_norm = -1
            for indx, text_with_contour in enumerate(texts_with_contour):
                curr_norm = norm(array([text_with_contour[1][2],text_with_contour[1][3]]))
                if max_norm < curr_norm:
                    max_index = indx
                    max_norm = curr_norm
            return [texts_with_contour[max_index]]

        return texts_with_contour

    def get_detected_text(self, with_contours=False):
        assert self._texts_with_contour is not None
        if with_contours:
            return self._texts_with_contour
        else:
            return [elem[0] for elem in self._texts_with_contour]

    def get_detected_faces(self,with_contours=False):
        assert self._faces is not None
        if with_contours:
            return self._faces
        else:
            return len(self._faces)

    def get_img_shape(self):
        assert self._image is not None
        return self._image.shape

    def get_max_size_text(self, return_index = False):
        texts_with_contour = self._texts_with_contour
        if texts_with_contour is not None:
            max_index = -1
            max_norm = -1
            for indx, text_with_contour in enumerate(texts_with_contour):
                curr_norm = norm(array([text_with_contour[1][2],text_with_contour[1][3]]))
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
        texts_with_contour = self._texts_with_contour.copy()
        texts_with_contour.remove(self.get_max_size_text(return_index=True)[0])
        return [elem[0] for elem in texts_with_contour]

    def get_min_size_text(self):
        texts_with_contour = self._texts_with_contour
        if texts_with_contour is not None:
            min_index = -1
            min_norm = inf
            for indx, text_with_contour in enumerate(texts_with_contour):
                curr_norm = norm(array([text_with_contour[1][2],text_with_contour[1][3]]))
                if min_norm > curr_norm:
                    min_index = indx
                    min_norm = curr_norm
            return [texts_with_contour[min_index][0]]
        return None

    def get_stat_params(self):
        if self._image is not None:
            flatten = self._image.flatten()
            return (mean(flatten),var(flatten))
        return (0,0)
    
    def is_empty_transition_image(self,var_threshold=1e-2):
        return self.get_stat_params()[1] < var_threshold

    def is_similar_to(self,other_image:'ImageClassifier'):
        comp_method = self._comp_method
        if comp_method == _DistanceMeasMethods.COSINE_SIM.value:
            return all(self.get_cosine_similarity(other_image) >= self._threshold)
        elif comp_method == _DistanceMeasMethods.MEAN_ABSOLUTE_DIST.value:
            return all(self.get_mean_distance(other_image) <= self._threshold)


    def get_cosine_similarity(self,other:'ImageClassifier',on_histograms=True,rounding_decimals:int= 10):
        '''
        Compute cosine similarity between two images

        Params
        ------ 
        on_histograms : FASTER if True analysis is performed on histograms
        rounding_decimals : number of decimals of precision
        
        Returns
        --------
        1xN numpy array with N as the number of color channels (3 for RGB-BGR and 1 for GRAYSCALE)
        '''
        assert self._image is not None and other._image is not None and self._image.shape == other._image.shape
        
        if on_histograms:   # looks like it's faster
            this_mat = self.get_hists(normalize=True)
            other_mat = other.get_hists(normalize=True)
        else:   # reshape to num_colors flatten rows, one for each color channel and normalize
            this_image = self._image
            other_image = other._image
            this_mat = reshape(this_image,(this_image.shape[2],this_image.shape[0]*this_image.shape[1])).astype(float)
            other_mat = reshape(other_image,(other_image.shape[2],other_image.shape[0]*other_image.shape[1])).astype(float)
            cv2.normalize(this_mat,this_mat,0,1,cv2.NORM_MINMAX)
            cv2.normalize(other_mat,other_mat,0,1,cv2.NORM_MINMAX)
        cosine_sim = round( diag(dot(this_mat,other_mat.T))/(norm(this_mat,axis=1)*norm(other_mat,axis=1)), 
                            decimals=rounding_decimals)
        return cosine_sim

    def get_mean_distance(self,other:'ImageClassifier',on_histograms=True):
        assert self._image is not None and other._image is not None
        if on_histograms:
            this_mat = self.get_hists(normalize=True)
            other_mat = other.get_hists(normalize=True)
            dists = abs(this_mat - other_mat)
            return mean(dists,axis=1)
        else:
            this_mat = self._image.astype(int)
            other_mat = other._image
            dists = abs(this_mat - other_mat)
            return mean(reshape(dists,(dists.shape[0]*dists.shape[1],dists.shape[2])),axis=0)

    def _get_grayscaled_img(self):
        if self._color_scheme == ColorScheme.BGR:
            return cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
        elif self._color_scheme == ColorScheme.RGB:
            return cv2.cvtColor(self._image, cv2.COLOR_RGB2GRAY)
        else:
            return self._image

    def get_hists(self,normalize:bool=False,bins:int=256,grayscaled=False):
        '''
        Generate image histogram\n
        
        Parameters
        ----------
        normalize : if true normalizes on minmax
        grayscaled : if true the image is processed to grayscale
        '''
        assert self._image is not None
        # CV2 calcHist is fast but can't calculate 3 channels at once 
        # so the fastest way is making a list of arrays and merging with cv2 merge
        if grayscaled:
            img = self._get_grayscaled_img()
        else:
            img = self._image
        img = cv2.split(img)
        num_channels = len(img)
        hists = []
        for col_chan in range(num_channels):
            hist = cv2.calcHist(img,channels=[col_chan],mask=None,histSize=[bins],ranges=[0,256])
            if normalize:
                cv2.normalize(hist,hist,0,1,cv2.NORM_MINMAX)
            hists.append(hist)
        hists = cv2.merge(hists)
        if len(hists.shape) > 2: hists = transpose(hists,(2,0,1))
        return reshape(hists,(num_channels,bins))
    
    def get_img(self, text_bounding_boxes=False):
        if not text_bounding_boxes or not self._texts_with_contour:
            return self._image
        return draw_bounding_boxes_on_image(self._image,[elem[1] for elem in self._texts_with_contour])

    def set_img(self,img):
        self._image = img
        self._texts_with_contour = None
        self._faces = None
        return self

    def set_color_scheme(self,color_scheme:Literal[ColorScheme.RGB, ColorScheme.BGR]):
        assert color_scheme == ColorScheme.BGR or color_scheme == ColorScheme.RGB or color_scheme == ColorScheme.GRAY 
        self._color_scheme = color_scheme
        return self
    
    def reset(self):
        return self.set_img(None)


def draw_bounding_boxes_on_image(img, bounding_boxes:'list[tuple[(int,int,int,int)]]'):
    img = img.copy()
    for xywh in bounding_boxes:
        x = xywh[0]; y = xywh[1]; w = xywh[2]; h = xywh[3]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
    return img
        


#from words import extract_keywords, extract_title

if __name__ == '__main__':
    import os
    img = cv2.cvtColor(cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)),"svm_dataset","screen01.png")), cv2.COLOR_BGR2RGB)
    classif = ImageClassifier(image_and_scheme=[img,ColorScheme.RGB])
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