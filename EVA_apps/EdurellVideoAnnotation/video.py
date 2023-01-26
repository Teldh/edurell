import youtube_dl
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from enum import Enum
from image import ImageClassificator, draw_bounding_boxes
from math import floor, ceil
from inspect import getfile


class OutputColors(Enum):

    GRAY = cv2.COLOR_BGR2GRAY
    RGB = cv2.COLOR_BGR2RGB


class LocalVideo:
    '''
    Load local video given a video_id that is the name of both the folder and the file.mp4\n
    videos are stored inside LocalVideo_class_path/static/videos
    '''
    def __init__(self,video_id:str,output_colors:int=OutputColors.RGB):
        if output_colors!=OutputColors.GRAY and output_colors!=OutputColors.RGB:
            raise Exception(f"Wrong parameter ouput_color value: {output_colors}")
        else:
            self._output_colors = output_colors.value
        class_path = os.path.dirname(os.path.abspath(getfile(self.__class__)))
        self._vid_id = video_id
        self._vidcap = cv2.VideoCapture(os.path.join(class_path, "static", "videos", video_id,f"{video_id}.mp4"))
        if not self._vidcap.isOpened():
            raise Exception(f"Can't find video: {video_id}")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._vidcap.relase()
    
    def create_keyframes(self,start_times,end_times,S,seconds_range, image_scale:float=0.5):
        """
        Take a list of clusters and compute the color histogram on end and start of the cluster
        :param cluster_list
        :param S: scala per color histogram
        :param seconds_range: aggiustare inizio e fine dei segmenti in base a differenza nel color histogram
        """
        assert len(start_times) == len(end_times)
        start_end_frames = [(self.get_num_frame_from_time(s_time),self.get_num_frame_from_time(e_time)) 
                                for s_time,e_time in zip(start_times,end_times)]

        curr_num_frame = 0
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, curr_num_frame)
        has_frame,curr_frame = self._vidcap.read()
        next_frame_offset = 10*self.get_fps()
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
            self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, curr_num_frame)
            has_frame,curr_frame = self._vidcap.read()
            prev_hist = hist

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        threshold = S * (summation / curr_num_frame)

        '''
        Controllo se c'è un cambio scena in un intorno di "seconds_range" frames dalla fine ed inizio di ciascun cluster.
        '''

        #start_changes = []
        #end_changes = []
        fps = self.get_fps()

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

                if np.all(changes_found): break

        # salvo immagini da mostrare nella timeline
        vidcap = self._vidcap
        images_path = []
        for i, start_end in enumerate(start_end_frames):

            vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_end[0])
            ret, image = vidcap.read()
            assert ret
            image = cv2.resize(image,(np.array([image.shape[1],image.shape[0]],dtype='f')*image_scale).astype(int))
            current_path = os.path.dirname(os.path.abspath(__file__))
            image_name = str(i) #str(cluster_starts[i]).replace(".","_")

            saving_position = os.path.join(current_path, "static", "videos", self._vid_id, image_name + ".jpg")
            #print(saving_position)
            #saving_position = "videos\\" + video_id + "\\" + str(start) + ".jpg"
            cv2.imwrite(saving_position, image)
            images_path.append("videos/" + self._vid_id + "/" + image_name + ".jpg")

        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, self._num_curr_frame)
        #print(images_path)
        ''' Ritorno le path delle immagini della timeline'''
        return images_path, start_times, end_times

    def close(self):
        self._vidcap.release()
        del self

    def extract_next_frame(self):
        '''
        Retrieve current frame and proceedes to the next
        NO VALIDITY CHECKS ARE MADE
        '''
        has_frame, image = self._vidcap.read()
        if has_frame:
            image = cv2.cvtColor(image, self._output_colors)
            image.flags.writeable = False
        else:
            return None
        return image
    
    def get_count_frames(self) -> int:
        return self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_dim_frame(self):
        return  int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)), \
                int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), \
                3 if self._output_colors == OutputColors.RGB else None

    def get_fps(self) -> int:
        return self._vidcap.get(cv2.CAP_PROP_FPS)

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

from math import log2
from numpy import clip
from words import text_cosine_dist 

class VideoSpeedManager:
    '''
    LocalVideo wrapper
    Based on an adaptation of "TCP fast retransmit and fast recovery" algorithm\n
    https://encyclopedia.pub/media/common/202107/blobid20-60f5467ae42de.jpeg\n
    edited such that on collision (found text in the current frame)
    in whichever phase (slow start or congestion avoidance)
    it rolls back the video frame by frame to the first colliding frame,
    proceeds min_sample_rate_frame each until there's no collision anymore
    and then restarts with congestion avoidance 
    because this is a textual video overall

    min sample rate is defined as the minimum amount of frame to sample one frame every 0.1 seconds
    
    :param vid_ref = reference to the video
    :param exp_base = base for the exponential increase of slow start
    :param lin_factor = m factor of the linear equation of the congestion avoidance increments
    :param max_exp_window_seconds = ssthresh in seconds 
    :param ratio_lin_exp_window_size = coeff of max_exp_window_factor that sets the clipping max speed
    '''
    def __init__(self,vid_ref:LocalVideo,time_decimals_accuracy:int=1,exp_base:float=1.4,lin_factor:float=2,max_seconds_exp_window:float=5,ratio_lin_exp_window_size:float=1.5):
        max_size_exp_window_frames = int(vid_ref.get_fps()*max_seconds_exp_window)
        max_size_lin_window_frames = int(max_size_exp_window_frames*ratio_lin_exp_window_size)
        start_sample_rate = int(clip(vid_ref.get_fps()*(10**(-time_decimals_accuracy)),1,vid_ref.get_fps()))

        self.vid_ref = vid_ref
        self._curr_num_frame = -start_sample_rate
        self._min_window_frame_size = start_sample_rate
        self._curr_x = 0
        self._max_size_exp_window_frames = max_size_exp_window_frames
        self._max_size_lin_window_frames = max_size_lin_window_frames
        self._exp_base = exp_base
        self._y0_exp = start_sample_rate
        self._m = lin_factor
        self._y0_lin = max_size_exp_window_frames-lin_factor*(log2(max_size_lin_window_frames)/log2(exp_base))
        self._is_cong_avoid = False
        self._is_collided = False
        self._is_video_ended = False
    
    def _exp_step(self,value:int): # (base^x - 1) + y0
        return (self._exp_base**value-1) + self._y0_exp
    
    def _lin_step(self,value:int):
        return self._m*value + self._y0_lin

    def is_video_ended(self):
        return self._is_video_ended

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

    def get_percent_curr_frame(self) -> int:
        return ceil(self._curr_num_frame/self.vid_ref.get_count_frames()*100)

    def get_time_curr_frame(self):
        '''
        In seconds
        '''
        return self.vid_ref.get_time_from_num_frame(self._curr_num_frame)

    def debug_get_speed(self):
        if self._curr_window_frame_size is not None:
            return self._curr_window_frame_size
        return 0

    def get_next_frame_and_update_step(self):
        '''
        Returns next frame based on current speed and collision status
        if video is ended returns the last frame sets a flag
        '''
        
        if not self._is_collided:
            if not self._is_cong_avoid:
                # exponential step
                next_size_window_frame = clip(  self._exp_step(self._curr_x),
                                                self._min_window_frame_size,
                                                self._max_size_exp_window_frames )
                if next_size_window_frame == self._max_size_exp_window_frames:
                    self._is_cong_avoid = True
            else:
                # linear step
                next_size_window_frame = clip(  self._lin_step(self._curr_x),
                                                self._min_window_frame_size,
                                                self._max_size_lin_window_frames )
            self._curr_x += 1
        else:
            next_size_window_frame = self._min_window_frame_size
        self._curr_window_frame_size = int(next_size_window_frame)
        vid_ref = self.vid_ref
        self._curr_num_frame = self._curr_num_frame + self._curr_window_frame_size 
        vid_ref.set_num_frame(self._curr_num_frame)
        frame = vid_ref.extract_next_frame()
        if frame is None:
            self._is_video_ended = True
            num_last_frame = vid_ref.get_count_frames()-1
            vid_ref.set_num_frame(num_last_frame)
            frame = vid_ref.extract_next_frame()
            self._curr_num_frame = num_last_frame + 1 
        return frame

    def _bin_search(self,vid_ref:LocalVideo, min_offset:int, max_offset:int, step_size:int):
        L = min_offset
        R = max_offset
        frame = ImageClassificator()
        while L <= R:
            m = floor((L+R)/2)
            vid_ref.set_num_frame(m)
            if frame.set_img(vid_ref.extract_next_frame()).detect_text(only_title=True):
                R = m - 1
            else:
                L = m + 1
        else:
            m = ceil((L+R)/2)
        return m + m%step_size # align to the step_size


    def collide_and_get_fixed_num_frame(self):
        curr_num_frame = self._curr_num_frame
        max_rollback_frame = clip(curr_num_frame - self._curr_window_frame_size, 0, curr_num_frame)
        self._curr_num_frame = self._bin_search(  self.vid_ref,
                                            max_rollback_frame,
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
        self._curr_num_frame = num_frame - prev_size_window_frame



from segmentation import TimedAndFramedText, PunctuatorSingleton
from pprint import pprint
from nltk import tokenize
import time

if __name__ == '__main__':
    start_time = time.time()
    vid_id = "PPLop4L2eGk" # slide video
    #vid_id = "YI3tsmFsrOg" # not slide video
    #vid_id = "UuzKYffpxug" # slide + person video
    #vid: LocalVideo = LocalVideo(vid_id,output_colors=OutputColors.GRAY)
    video = LocalVideo(vid_id,output_colors=OutputColors.GRAY) # for testing
    del vid_id
    vsm = VideoSpeedManager(video)

    #min_frames_speech_threshold = vsm.get_video().get_fps()*5*0
    #min_frames_distance = vsm.get_video().get_fps()*5
    
    #height,width,depth = vsm.get_video().get_dim_frame()
    #frame_size = (height,width) if depth is None else (height,width,depth)
    curr_frame = ImageClassificator()
    prev_frame = ImageClassificator()
    analysis_frame = ImageClassificator()
    num_start_frame = None

    output_TFT_list:'list[TimedAndFramedText]' = []
    printed_progress:int = -1
    counter:int = 0
    max_speed:int = 0
    collisions_TFT_stack:'list[TimedAndFramedText]' = []
    while not vsm.is_video_ended():

        # read a frame from video speed manager and update the step
        curr_frame.set_img(vsm.get_next_frame_and_update_step())
        if vsm._curr_num_frame > 535: #TODO fix here, print the picture
            print(vsm._curr_num_frame)

        #   if start frame not already set and there is text in the picture
        if len(collisions_TFT_stack) == 0:
            if curr_frame.detect_text():
                num_start_frame = vsm.collide_and_get_fixed_num_frame()
                curr_frame.set_img(vsm.get_frame_from_num(num_start_frame))
                texts_with_cnt = curr_frame.detect_text(return_text=True,with_contours=True)
                for text,xywh in texts_with_cnt:
                    collisions_TFT_stack.append(
                        TimedAndFramedText( text=text,
                                            start_end_frames=[(num_start_frame,-1)],
                                            xywh=xywh))

        # if there are collisions in the queue
        else: # we are in a collision window
            # if there's statistical difference from the last frame or video is ended -> scene changed, need to update queue
            if not np.all(curr_frame.get_cosine_similarity(prev_frame, on_histograms=True) >= 0.999) \
                or vsm.is_video_ended():

                #   detect text from the cosine-different frame and diff it with respect to the collisions stack
                #   save diffs in a mask
                texts_with_cnt = curr_frame.detect_text(return_text=True,with_contours=True)
                mask = np.zeros(len(collisions_TFT_stack),dtype=bool)
                if not vsm.is_video_ended():
                    for text_in_image,_ in texts_with_cnt:
                        for indx_in_stack, timedText_coll in enumerate(collisions_TFT_stack):
                            if text_in_image == timedText_coll.text:
                                mask[indx_in_stack] = True

                #   loop through the mask to decide if there's
                num_last_same_frame = vsm.get_prev_num_frame()
                for indx_in_stack,found_this_text_in_new_frame in sorted(enumerate(mask),reverse=True):
                    if not found_this_text_in_new_frame:
                        coll_TFT_elem = collisions_TFT_stack.pop(indx_in_stack)
                        coll_TFT_elem_text = coll_TFT_elem.text
                        coll_TFT_elem_start_frame = coll_TFT_elem.start_end_frames[0][0]
                        inserted = False
                        for output_TFT_elem in sorted(output_TFT_list,reverse=True):
                            if text_cosine_dist(output_TFT_elem.text, coll_TFT_elem_text) > 0.9:
                                output_TFT_elem.start_end_frames.append((coll_TFT_elem_start_frame,num_last_same_frame))
                                inserted = True
                                break
                        if not inserted:
                            coll_TFT_elem.start_end_frames[0] = (coll_TFT_elem_start_frame,num_last_same_frame)
                            output_TFT_list.append(coll_TFT_elem)

                ##   rollback to last same frame
                #vsm.rewind_to(num_last_same_frame)

                if len(collisions_TFT_stack)==0:
                    vsm.end_collision()
        
        prev_frame.set_img(curr_frame.get_img())

        curr_percentage = vsm.get_percent_curr_frame()
        max_speed = max(max_speed, vsm.debug_get_speed())
        if curr_percentage > printed_progress:
            print(" video analysis "+str(curr_percentage)+'%'+" progress"+"."*(counter%12)+" "*12,end="\r")
            printed_progress = curr_percentage
        else:
            print(" video analysis "+str(curr_percentage)+'%'+" progress"+"."*(counter%12)+" "*12,end="\r")

        counter += 1
    
    
    print()
    for output_TFT_elem in output_TFT_list:
        pprint(output_TFT_elem)

    #   merge adjacent frames
    for output_TFT_elem in output_TFT_list:
        start_end_frames = output_TFT_elem.start_end_frames
        merged_start_end_frames = []
        curr_end = None
        curr_start = None
        for new_start,new_end in start_end_frames:
            if curr_end is None:
                curr_start = new_start
                curr_end = new_end
            elif new_start == curr_end+1:
                curr_end = new_end
            else:
                merged_start_end_frames.append((curr_start,curr_end))
                curr_end = new_end
                curr_start = new_start
        merged_start_end_frames.append((curr_start,curr_end))
        output_TFT_elem.start_end_frames = merged_start_end_frames
    print()
    print(f"total time = {time.time()-start_time}")
    
    #from PIL import Image 
    #   DEBUG : print everything 
    for output_TFT_elem in output_TFT_list:
        print(output_TFT_elem)
        #image = Image.fromarray(vsm.get_frame_from_num(output_TFT_elem.start_end_frames[0][0]))
        #image.save(''.join(list(output_TFT_elem.text)[:5])+str(output_TFT_elem.start_end_frames[0][0])+".png")
        for start_end in output_TFT_elem.start_end_frames:
            text = ''.join(list(output_TFT_elem.text)[:15]).replace('\n','')
            #print(f"({video.get_time_from_num_frame(start_end[0])},{video.get_time_from_num_frame(start_end[1])})")
            if start_end[0] > 0:
                plt.imshow(vsm.get_frame_from_num(start_end[0]-1),cmap='gray')
                plt.title(f"'{text}' frame before the start ({start_end[0]-1})")
                plt.show()
            plt.imshow(draw_bounding_boxes(vsm.get_frame_from_num(start_end[0]),[output_TFT_elem.xywh]),cmap='gray')
            plt.title(f"'{text}' start {start_end[0]}")
            plt.show()
            plt.imshow(vsm.get_frame_from_num(start_end[0]+1),cmap='gray')
            plt.title(f"'{text}' frame after the start ({start_end[0]+1})")
            plt.show()
            plt.imshow(vsm.get_frame_from_num(start_end[1]-1),cmap='gray')
            plt.title(f"'{text}' frame before the end ({start_end[1]-1})")
            plt.show()
            plt.imshow(draw_bounding_boxes(vsm.get_frame_from_num(start_end[1]),[output_TFT_elem.xywh]),cmap='gray')
            plt.title(f"'{text}' end {start_end[1]}")
            plt.show()
            if start_end[1] < video.get_count_frames()-1:
                plt.imshow(vsm.get_frame_from_num(start_end[1]+1),cmap='gray')
                plt.title(f"'{text}' frame after the end ({start_end[1]+1})")
                plt.show()
            
    

    video.close()

    #TODO   write this function into segmentation.py

    #TODO   PROBABILMENTE COSÌ NON FUNZIONA CON VIDEO MOLTO MOVIMENTATI, DEVO SEGMENTARE CON COSINE DIST SUI BOUNDING BOXES O RISCHIO CHE UN MOVIMENTO IN WEBCAM A BORDO SCHERMO MI TRIGGERI IL CAMBIO SCENA
    #       prima provo a farlo funzionare semplice

    
    
    #download("https://www.youtube.com/watch?v=UuzKYffpxug&list=PLV8Xi2CnRCUm0QOaRfPuMzFNUVxmYlEiV&index=5")