import youtube_dl
import os
import cv2
from numpy import clip, reshape

from image import ImageClassifier, ColorScheme
from math import floor, ceil, log2
from inspect import getfile
from typing_extensions import Literal


class LocalVideo:
    '''
    Load local video given a video_id that is the name of both the folder and the file.mp4\n
    videos are stored inside LocalVideo_class_path/static/videos
    RGB are converted
    GRAYSCALE 

    Parameters
    ----------

    video_id : string to load video: /static/videos/{video_id}/{video_id}.mp4
    output_colors : must be a value from the ``class(Enum) ColorScheme``and is used for format conversions
    '''
    def __init__(self,video_id:str,output_colors:Literal[ColorScheme.RGB, ColorScheme.BGR],forced_frame_size:'tuple[int,int] | None'= None):
        if output_colors!=ColorScheme.GRAY and output_colors!=ColorScheme.RGB and output_colors!=ColorScheme.BGR:
            raise Exception(f"Wrong parameter ouput_color value: {output_colors}")
        else:
            self._output_colors = output_colors
            if output_colors == ColorScheme.GRAY:
                self._num_colors = 1
            else:
                self._num_colors = 3
        self._frame_size = forced_frame_size
        class_path = os.path.dirname(os.path.abspath(getfile(self.__class__)))
        self._vid_id = video_id
        self._vidcap = cv2.VideoCapture(os.path.join(class_path, "static", "videos", video_id,f"{video_id}.mp4"))
        if not self._vidcap.isOpened():
            raise Exception(f"Can't find video: {video_id}")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._vidcap.relase()
    
    def close(self):
        self._vidcap.release()
        del self

    def extract_next_frame(self):
        '''
        Retrieve current frame and proceedes to the next\n
        ``NO VALIDITY CHECKS ARE MADE``
        '''
        has_frame, image = self._vidcap.read()
        if not has_frame:
            return None
        if self._frame_size is not None:
            image = cv2.resize(image,self._frame_size)
        if self._output_colors != ColorScheme.BGR:
            image = cv2.cvtColor(image, self._output_colors.value)
        return reshape(image,(image.shape[0],image.shape[1],self._num_colors))
    
    def get_count_frames(self) -> int:
        return int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_dim_frame(self):
        return  int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)), \
                int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), \
                self._num_colors

    def get_fps(self) -> int:
        return int(self._vidcap.get(cv2.CAP_PROP_FPS))

    def get_id_vid(self) -> str:
        return self._vid_id

    def get_time_from_num_frame(self, num_frame:int):       #fr / (fr / s) = s
        '''
        In seconds
        '''
        return round(num_frame/self.get_fps(), ndigits=2)

    def get_num_frame_from_time(self,seconds:float):
        return round(seconds*self.get_fps())

    def rewind_video(self):
        self.set_num_frame(0)
    
    def set_num_frame(self,num_frame:int):
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES,num_frame)


def download(url):

    url_parsed = url.split('&')[0]
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

class VideoSpeedManager:
    '''
    LocalVideo wrapper\n
    Based on an adaptation of "TCP fast retransmit and fast recovery" algorithm\n
    https://encyclopedia.pub/media/common/202107/blobid20-60f5467ae42de.jpeg\n
    edited such that on collision (found text in the current frame)
    in whichever phase (slow start or congestion avoidance)
    it rolls back the video frame by frame to the first colliding frame,
    proceeds min_sample_rate_frame each until there's no collision anymore
    and then restarts with congestion avoidance 
    because this is a textual video overall

    ``min sample rate`` is defined as the minimum speed to reach a sensibility of 10^(-time_decimals_accuracy)

    In this project speed is locked
    
    Parameters
    ---------

    vid_ref : reference to the video

    time_decimals_accuracy : guarantes sampling of one frame every 10**(-decimals) seconds

    exp_base : base for the exponential increase of slow start

    lin_factor : m factor of the linear equation of the congestion avoidance increments

    max_exp_window_seconds : ssthresh in seconds 

    ratio_lin_exp_window_size : coeff of max_exp_window_factor that sets the clipping max speed

    '''
    def __init__(self,video_id:str,output_colors:Literal[ColorScheme.RGB, ColorScheme.BGR],out_frame_size:'tuple[int,int]'=(640,320),time_decimals_accuracy:int=1,exp_base:float=1.4,lin_factor:float=2,max_seconds_exp_window:float=5,ratio_lin_exp_window_size:float=1.5):
        self._init_params = (video_id,output_colors,out_frame_size,time_decimals_accuracy,exp_base,lin_factor,max_seconds_exp_window,ratio_lin_exp_window_size)
        
        vid_ref = LocalVideo(video_id=video_id,output_colors=output_colors,forced_frame_size=out_frame_size)
        max_size_exp_window_frames = int(vid_ref.get_fps()*max_seconds_exp_window)
        max_size_lin_window_frames = int(max_size_exp_window_frames*ratio_lin_exp_window_size)
        start_sample_rate = int(clip(vid_ref.get_fps()*(10**(-time_decimals_accuracy)),1,vid_ref.get_fps()))

        self.vid_ref = vid_ref
        self._curr_num_frame = -start_sample_rate
        self._curr_x = 0
        self._frames = None
        self._curr_start_end_frames = None
        self._min_window_frame_size = start_sample_rate
        self._max_size_exp_window_frames = max_size_exp_window_frames
        self._max_size_lin_window_frames = max_size_lin_window_frames
        self._exp_base = exp_base
        self._y0_exp = start_sample_rate
        self._m = lin_factor
        self._y0_lin = max_size_exp_window_frames-lin_factor*(log2(max_size_lin_window_frames)/log2(exp_base))
        self._is_cong_avoid = False
        self._is_collided = False
        self._is_video_ended = False
        self._is_forced_speed = False
    
    def _exp_step(self,value:int): # (base^x - 1) + y0
        return (self._exp_base**value-1) + self._y0_exp
    
    def _lin_step(self,value:int):
        return self._m*value + self._y0_lin

    def is_video_ended(self):
        return self._is_video_ended

    def close(self):
        self.vid_ref.close()

    def get_video(self):
        '''
        to use only for obtaining infos on frames, don't set anything if this class is used
        '''
        return self.vid_ref

    def get_curr_num_frame(self):
        return self._curr_num_frame
    
    def get_prev_num_frame(self):
        return self._curr_num_frame - self._curr_window_frame_size

    def get_frame_from_num(self,num_frame:int):
        prev_num_frame = self._curr_num_frame
        self.vid_ref.set_num_frame(num_frame)
        frame = self.vid_ref.extract_next_frame()
        self.vid_ref.set_num_frame(prev_num_frame)
        return frame

    def get_percentage_progression(self) -> int:
        if self._frames is not None:
            if len(self._frames) > 0:
                return ceil(self._curr_num_frame/self._frames[0][1] * 100)
            else:
                assert self._curr_start_end_frames is not None
                return ceil(self._curr_num_frame/self._curr_start_end_frames[1] * 100)
        return ceil(self._curr_num_frame/self.vid_ref.get_count_frames()*100)

    def get_time_curr_frame(self):
        '''
        In seconds
        '''
        return self.vid_ref.get_time_from_num_frame(self._curr_num_frame)

    def _debug_get_speed(self):
        if self._curr_window_frame_size is not None:
            return self._curr_window_frame_size
        return 0

    def _get_frame_from_internal_frames(self):
        curr_num_frame = self._curr_num_frame
        curr_start_end_frames = self._curr_start_end_frames
        if curr_start_end_frames is None or curr_num_frame + self._curr_window_frame_size >= curr_start_end_frames[1]:
            try:
                assert self._frames is not None
                self._curr_start_end_frames = self._frames.pop()
            except IndexError:
                self._frames = None
                return self.get_video().get_count_frames()
            return self._curr_start_end_frames[0]
        return self._curr_num_frame

    def get_frame(self):
        '''
        Returns next frame based on current speed and collision status
        if video is ended returns the last frame sets a flag
        '''
        if self._is_forced_speed:
            next_size_window_frame = self._curr_window_frame_size 
        else:
            if self._is_collided:
                next_size_window_frame = self._min_window_frame_size
            else:
                if self._is_cong_avoid:
                    # linear step
                    next_size_window_frame = clip(  self._lin_step(self._curr_x),
                                                    self._min_window_frame_size,
                                                    self._max_size_lin_window_frames )
                else:
                    # exponential step
                    next_size_window_frame = clip(  self._exp_step(self._curr_x),
                                                    self._min_window_frame_size,
                                                    self._max_size_exp_window_frames )
                    if next_size_window_frame == self._max_size_exp_window_frames:
                        self._is_cong_avoid = True
                self._curr_x += 1
               
        self._curr_window_frame_size = int(next_size_window_frame)
        
        if self._frames is not None:
            self._curr_num_frame = self._get_frame_from_internal_frames()
        
        vid_ref = self.vid_ref
        self._curr_num_frame += self._curr_window_frame_size 
        vid_ref.set_num_frame(self._curr_num_frame)
        frame = vid_ref.extract_next_frame()
        if frame is None:
            self._is_video_ended = True
            num_last_frame = vid_ref.get_count_frames()-1
            vid_ref.set_num_frame(num_last_frame)
            frame = vid_ref.extract_next_frame()
            self._curr_num_frame = num_last_frame + 1 
        return frame

    def _bin_search(self, min_offset:int, max_offset:int, step_size:int):
        L = min_offset
        R = max_offset
        vid_ref = self.vid_ref
        frame = ImageClassifier().set_color_scheme(vid_ref._output_colors)
        while L <= R:
            m = floor((L+R)/2)
            vid_ref.set_num_frame(m)
            if frame.set_img(vid_ref.extract_next_frame()).detect_text():
                R = m - 1
            else:
                L = m + 1
        else:
            m = ceil((L+R)/2)
        return m + m%step_size # align to the step_size


    def collide_and_get_fixed_num_frame(self):
        curr_num_frame = self._curr_num_frame
        max_rollback_frame = int(clip(curr_num_frame - self._curr_window_frame_size, 0, curr_num_frame))
        self._curr_num_frame = self._bin_search(    max_rollback_frame,
                                                    curr_num_frame,
                                                    self._min_window_frame_size )
        self._is_collided = True
        return self._curr_num_frame

    def end_collision(self):
        self._is_collided = False
        self._is_cong_avoid = True
        self._curr_x = 0
        self._y0_lin = self._min_window_frame_size

    def rewind_to(self,num_frame:int):
        if not self._is_forced_speed:
            if self._is_collided:
                prev_size_window_frame = self._min_window_frame_size
            elif self._is_cong_avoid:
                prev_size_window_frame = clip(  self._lin_step(self._curr_x-1),
                                                self._min_window_frame_size,
                                                self._max_size_exp_window_frames )
            else:
                prev_size_window_frame = clip(  self._exp_step(self._curr_x-1),
                                                self._min_window_frame_size,
                                                self._max_size_exp_window_frames )
        else:
            prev_size_window_frame = self._curr_window_frame_size
        self._curr_num_frame = num_frame - int(prev_size_window_frame)

    def reset(self):
        self.__init__(*self._init_params)

    def lock_speed(self,num_frames_skipped:int or None= None):
        self._is_forced_speed = True
        if num_frames_skipped is None:
            self._curr_window_frame_size = self._min_window_frame_size
        else:
            self._curr_window_frame_size = num_frames_skipped
    
    def _get_frame_offset(self,offset:int):
        prev_speed = self._curr_window_frame_size
        was_forced = self._is_forced_speed
        self._is_forced_speed = True
        self._curr_window_frame_size = offset
        frame = self.get_frame()
        self._curr_window_frame_size = prev_speed
        self._is_forced_speed = was_forced
        return frame

    def get_previous_frame(self):
        if self._curr_num_frame < 0:
            self._curr_num_frame = 1
        return self._get_frame_offset(-1)

    def get_following_frame(self):
        if self._is_video_ended:
            self._curr_num_frame -= 2
        return self._get_frame_offset(1)

    def set_analysis_frames(self,frames:'list[tuple[int,int]]'):
        self._frames = frames
    
if __name__ == '__main__':
    #vid_id = "PPLop4L2eGk" # slide video
    #vid_id = "YI3tsmFsrOg" # not slide video
    #vid_id = "UuzKYffpxug" # slide + person video
    #vid_id = "g8w-IKUFoSU" # forensic arch
    pass
    #color_scheme_for_analysis = ColorScheme.BGR
    #   BGR: is the most natural for Opencv video reader, so we avoid some matrix transformations
    #   RGB: should be used for debug visualization
    #   GRAY: can perform faster but less precise and may require more strict threshold 
    #         EDIT: grayscale don't work with face recognition so it's better not to use it 
    #extract_text_from_video(vid_id,color_scheme_for_analysis)
    #video.close()

#TODO   PROBABILMENTE COSÌ NON FUNZIONA CON VIDEO MOLTO MOVIMENTATI, DEVO SEGMENTARE CON COSINE DIST SUI BOUNDING BOXES O RISCHIO CHE UN MOVIMENTO IN WEBCAM A BORDO SCHERMO MI TRIGGERI IL CAMBIO SCENA
#       prima provo a farlo funzionare semplice

    
    
#download("https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5")