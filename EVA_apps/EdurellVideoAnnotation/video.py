import youtube_dl
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from enum import Enum
from image import ImageClassificator
from math import floor, ceil



class OutputColors(Enum):

    GRAY = cv2.COLOR_BGR2GRAY
    RGB = cv2.COLOR_BGR2RGB


class LocalVideo:
    
    def __init__(self,yt_video_id:str,output_color:int):
        if output_color!=OutputColors.GRAY and output_color!=OutputColors.RGB:
            raise Exception(f"Wrong parameter ouput_color value: {output_color}")
        current_path = os.path.dirname(os.path.abspath(__file__))
        self._vidcap = cv2.VideoCapture(os.path.join(current_path, "static", "videos", yt_video_id,f"{yt_video_id}.mp4"))
        if not self._vidcap.isOpened():
            raise Exception(f"Can't find video: {yt_video_id}")
        self._has_frame, self._frame = self._vidcap.read()
        self._num_curr_frame : int = 0
        self._next_frame_offset : int = 1
        self._output_color : Enum(OutputColors) = output_color.value
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._vidcap.relase()

    def has_next_frame(self) -> bool:
        return self._has_frame

    def next_frame(self):
        '''
        Retrieve current frame and proceedes to the next
        '''
        if self._has_frame:
            image = self._frame
            image.flags.writeable = False
            curr_frame = cv2.cvtColor(image, self._output_color)
            self._num_curr_frame += self._next_frame_offset
            self._vidcap.set(cv2.CAP_PROP_POS_FRAMES,self._num_curr_frame)
            self._has_frame, self._frame = self._vidcap.read()
            return curr_frame
        return None
    
    def get_num_frames(self) -> int:
        return self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_dim_frame(self):
        return (int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), self._frame.shape[2])

    def get_fps(self) -> int:
        return self._vidcap.get(cv2.CAP_PROP_FPS)
    
    def get_time_from_num_frame(self, num_frame:int):       #fr / (fr / s) = s
        '''
        In seconds
        '''
        assert num_frame >= 0 and num_frame < self.get_num_frames()
        return num_frame/self.get_fps()

    def get_curr_time(self):
        '''
        In seconds
        '''
        return self.get_time_from_num_frame(self._num_curr_frame)

    def get_frame(self,num_frame:int):
        assert num_frame >= 0 and num_frame < self.get_num_frames()
        vid = self._vidcap
        vid.set(cv2.CAP_PROP_POS_FRAMES, num_frame-1)
        res, frame = vid.read()
        assert res
        vid.set(cv2.CAP_PROP_POS_FRAMES, self.get_num_curr_frame()-1)
        return frame

    def get_percentage_progression(self) -> int:
        return ceil(self.get_num_curr_frame()/self.get_num_frames()*100)

    def get_num_curr_frame(self):
        return self._num_curr_frame - self._next_frame_offset

    def close(self):
        self._vidcap.release()
        del self

    def rewind_video(self):
        self.set_frame_num(0)
    
    def retrieve_stored_num_frames(self):
        return self.stored_num_frames

    def set_sample_rate(self,rate_num_frames:int):
        self._next_frame_offset = abs(floor(rate_num_frames))
    
    def set_frame_num(self,num_frame:int):
        self._num_curr_frame = num_frame
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES,self._num_curr_frame)
        self._has_frame, self._frame = self._vidcap.read()
        self._frame.flags.writeable = False



def download(url):

    url_parsed = url.split('&')[0]
    print(url_parsed)

    video_id = url_parsed.split("=")[1]

    #"creo cartella"
    current_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_path, "static", "videos", video_id)
    if not os.path.exists(path):
        os.mkdir(path)

    video_path = os.path.join(path, '%(id)s.%(ext)s')
    print(path)
    #ydl = youtube_dl.YoutubeDL({'outtmpl': current_path + '\\static\\videos\\'+video_id+'\\%(id)s.%(ext)s'})
    ydl = youtube_dl.YoutubeDL({'outtmpl': video_path})

    with ydl:
        result = ydl.extract_info(url_parsed, download=True)

    #print(result)

    return video_id, result["title"], result["channel"], result["duration"]

from image import cosine_similarity
from segmentation import TimedAndFramedText as TFText
from pprint import pprint

if __name__ == '__main__':

    vid_id = "PPLop4L2eGk" # slide video
    #vid_id = "UuzKYffpxug" # slide + person video
    vid: LocalVideo = LocalVideo(vid_id,output_color=OutputColors.RGB)
    #vid.set_sample_rate(vid.get_fps())
    #TODO threshold for min frames window
    min_frames_threshold = vid.get_fps()
    
    height,width,depth = vid.get_dim_frame()
    curr_frame = ImageClassificator(image_shape=(height,width,depth))
    prev_frame = ImageClassificator(image_shape=(height,width,depth))
    analysis_frame = ImageClassificator()
    start_frame_num = None

    text_frames = []
    printed_progress = -1
    while vid.has_next_frame():
        curr_frame.set_img(vid.next_frame())

        #empty transition image NOT NEEDED
        #if curr_frame.is_empty_transition_image():
        #    continue
        
        cosine_sim = cosine_similarity(curr_frame, prev_frame)
        #if start frame not already set and there's statistical difference from the last frame and there is text in the picture -> this is a start frame
        if start_frame_num is None and not np.all(cosine_sim >= 0.999) and curr_frame.detect_text():
            #print("beginning frame section");plt.imshow(curr_frame.get_img());plt.title("curr frame");plt.show();plt.imshow(prev_frame.get_img());plt.title("prev frame");plt.show()
            start_frame_num = vid.get_num_curr_frame()
        #if start frame is set and there's statistical difference from the last frame -> scene changed
        elif start_frame_num is not None and ( not np.all(cosine_sim >= 0.999) or vid.get_num_curr_frame() == vid.get_num_frames()-1):
            #if the window is above treshold -> save window, then reset start frame
            curr_frame_num = vid.get_num_curr_frame()
            if curr_frame_num - start_frame_num >= min_frames_threshold:
                #print("ending frame section");plt.imshow(curr_frame.get_img());plt.title("curr frame");plt.show();plt.imshow(prev_frame.get_img());plt.title("prev frame");plt.show()
                print(f"segment duration {vid.get_time_from_num_frame(curr_frame_num)-vid.get_time_from_num_frame(start_frame_num)}s")
                mid_frame_num = floor((curr_frame_num-start_frame_num)/2)
                analysis_frame.set_img(vid.get_frame(mid_frame_num))
                texts_with_bb =  analysis_frame.detect_text(return_text=True,with_contours=True)
                for (text,xywh) in texts_with_bb:
                    x,y,w,h = xywh[0],xywh[1],xywh[2],xywh[3]
                    vid_text = TFText(text=text,frames_window=(start_frame_num,curr_frame_num),xywh=(x,y,w,h))
                    text_frames.append(vid_text)
                
            start_frame_num = None

        prev_frame.set_img(curr_frame.get_img())

        curr_percentage = vid.get_percentage_progression()
        if curr_percentage > printed_progress:
            print(f"progression... {vid.get_percentage_progression()}%")
            printed_progress = curr_percentage

    pprint(text_frames)


    #TODO   probably most efficient way is to firstly scan all the video with a 1 second coarse-grained window to find all text images
    #       saving those seconds in a cluster of mapped { words : [start_s,end_s] } 
    
    #       then scan those frames back and forward to find the complete window
    
    #       then write this function into segmentation.py
            
    #TODO   merge with segmentation in segmentation.py otherwise is gonna take ages to compute
    #TODO   PROBABILMENTE COSÌ NON FUNZIONA CON VIDEO MOLTO MOVIMENTATI, DEVO SEGMENTARE CON COSINE DIST SUI BOUNDING BOXES O RISCHIO CHE UN MOVIMENTO IN WEBCAM A BORDO SCHERMO MI TRIGGERI IL CAMBIO SCENA
    
    #download("https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5")