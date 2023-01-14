import youtube_dl
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from enum import Enum
from image import ImageClassificator
from math import floor



class OutputColors(Enum):

    GRAY = cv2.COLOR_BGR2GRAY
    RGB = cv2.COLOR_BGR2RGB


class LocalVideo:

    stored_num_frames = []
    
    def __init__(self,yt_video_id:str,output_color:int):
        if output_color!=OutputColors.GRAY and output_color!=OutputColors.RGB:
            raise Exception(f"Wrong parameter ouput_color value: {output_color}")
        current_path = os.path.dirname(os.path.abspath(__file__))
        self._vidcap = cv2.VideoCapture(os.path.join(current_path, "static", "videos", yt_video_id,f"{yt_video_id}.mp4"))
        if not self._vidcap.isOpened():
            raise Exception(f"Can't find video: {yt_video_id}")
        self._has_frame, self._frame = self._vidcap.read()
        self._frame.flags.writeable = False
        self._num_curr_frame : int = 0
        self._num_frames_skipped : int = 0
        self._output_color : Enum(OutputColors) = output_color.value
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._vidcap.relase()
    
    def clear_stored_frames(self):
        self.stored_num_frames = []

    def has_next_frame(self) -> bool:
        return self._has_frame

    def next_frame(self):
        if self._has_frame:
            curr_frame = cv2.cvtColor(self._frame, self._output_color)
            self._num_curr_frame += self._num_frames_skipped
            self._vidcap.set(cv2.CAP_PROP_POS_FRAMES,self._num_curr_frame + self._num_frames_skipped)
            self._has_frame, self._frame = self._vidcap.read()
            self._frame.flags.writeable = False
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

    def get_percentage_progression(self,rounding_decimals:int=2) -> float:
        return np.round(self._vidcap.get(cv2.CAP_PROP_POS_AVI_RATIO)*100, decimals=rounding_decimals)

    def get_num_frame(self):
        return self._num_curr_frame

    def rewind_video(self):
        self.set_frame_num(0)
    
    def retrieve_stored_num_frames(self):
        return self.stored_num_frames

    def set_sample_rate(self,rate_num_frames:int):
        self._num_frames_skipped = abs(floor(rate_num_frames))
    
    def set_frame_num(self,num_frame:int):
        self._num_curr_frame = num_frame
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES,self._num_curr_frame)
        self._has_frame, self._frame = self._vidcap.read()
        self._frame.flags.writeable = False

    def store_num_frame(self, num_frame:int):
        self.stored_num_frames.append(num_frame)



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



if __name__ == '__main__':

    #path_dataset = os.path.join(os.path.dirname(os.path.abspath(__file__)),"svm_dataset")
    #os.mkdir(path_dataset)
    #slide_path = os.path.join(path_dataset,"slide")
    #not_slide_path = os.path.join(path_dataset,"not_slide")
    #os.mkdir(slide_path)
    #os.mkdir(not_slide_path)

    #TODO these are parameters to divide between next and previous frame
    threshold_diff_distrib = {"mean, avg":[3, 100]}


    vid_id = "PPLop4L2eGk" # slide video
    #vid_id = "UuzKYffpxug" # slide + person video
    vid: LocalVideo = LocalVideo(vid_id,output_color=OutputColors.RGB)
    vid.set_sample_rate(vid.get_fps())
    print(vid.get_fps())
    
    height,width,depth = vid.get_dim_frame()
    means = []
    vars = []
    curr_frame_distrib = np.zeros((1,2),dtype=np.float)    
    prev_frame_distrib = np.zeros((1,2),dtype=np.float)
    prev_img = None
    threshold_diff_frames = np.ones((1,2),dtype=np.float)*threshold_diff_distrib["mean, avg"]
    curr_frame = ImageClassificator()
    #counters = [0,0]
    printed_progress = -1
    while vid.has_next_frame():
        curr_frame = curr_frame.replace_img(vid.next_frame())

        #prev_frame_distrib[:] = curr_frame_distrib
        #curr_frame_distrib[:] = curr_frame.get_statistical_analysis()
        #means.append(curr_frame_distrib[0,0])
        #vars.append(curr_frame_distrib[0,1])

        #empty transition image
        if curr_frame.is_empty_transition_image():
            continue
        hists = curr_frame.get_hists()
        plt.plot(hists[0]);plt.plot(hists[1]);plt.plot(hists[2])
        plt.show()
        plt.imshow(curr_frame.get_img())
        plt.show()
        input()
        #print(f"curr: {curr_frame_distrib}, prev: {prev_frame_distrib}")
        #print(np.greater(curr_frame_distrib - prev_frame_distrib, threshold_diff_frames))
        #if np.any(np.greater(curr_frame_distrib - prev_frame_distrib, threshold_diff_frames)):
        #    if curr_frame.detect_text():
        #        print("text")
        #        print(curr_frame.get_text())
        #        input()
        #    #print(vid.get_num_frame())
        #    img = curr_frame.get_img(text_bounding_boxes=True)
        #    plt.show()
        curr_percentage = vid.get_percentage_progression(rounding_decimals=0)
        if curr_percentage%2 == 0 and int(curr_percentage) != printed_progress:
            print(f"progression... {vid.get_percentage_progression(rounding_decimals=0)}%")
            printed_progress = int(curr_percentage)

            #print("****Processing frame****"); print(get_title(img))
            #value = bool(input("value?"))
            #path_curr_img = slide_path if value else not_slide_path
            #image.fromarray(img).save(path_curr_img+f"/{vid_id}_{counters[value]}.png")
            #counters[value]+=1
            

        
        #input("Enter to next frame, Ctr+C and Enter to exit")
        #if len(vars) > 10:
        #    plt.plot(means,label="means")
        #    plt.plot(vars,label="vars")
        #    plt.legend()
        #    plt.show()
        #else:
        #    plt.imshow(img.reshape((height,width,colors)))
        #    plt.show()
    plt.plot(means,label="means")
    print(f"avg_mean: {np.mean(means)}  var_mean: {np.var(means)}")
    plt.plot(vars,label="vars")
    plt.legend()
    plt.show()
    
    #download("https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5")