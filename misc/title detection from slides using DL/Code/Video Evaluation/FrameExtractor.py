"""
Created on Sat Sep 02 18:53:14 2023

@author: farhan
"""

import cv2     # cv2 is imported to use OpenCV functions
import os      # os is imported to perform file operations

class FrameExtractor:
    """
    A class for extracting frames from a video file and saving them as images.

    Parameters:
    
    - video_path (str): The path to the input video file.
    - cap (cv2.VideoCapture): VideoCapture object to read frames from the video.
    - frame_count (int): Counter for the total number of frames processed.
    - previous_frame (numpy.ndarray): The previous grayscale frame for comparison.
    - frame_skip (int): Counter for skipping frames based on the specified interval.
    """
    
    def __init__(self, video_path):
         
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.frame_count = 0
        self.previous_frame = None
        self.frame_skip = 0

    def are_frames_identical(self, frame1, frame2):
        """
        Checks if two frames are identical by comparing pixel values.

        Parameters:
        
        - frame1: First frame for comparison.
        - frame2: Second frame for comparison.

        Returns:
        
        - bool: True if frames are identical, False otherwise.
        """
        return (frame1 == frame2).all()

    def extract_frames(self, output_folder, interval_seconds):
        """
        Extracts frames from the video and saves them as images in the specified output folder.

        Parameters:
        
        - output_folder (str): The path to the folder where extracted frames will be saved.
        - interval_seconds (int): Time interval between extracted frames.
        """
         
        if not self.cap.isOpened():
            print("Error: Could not open video file.")
            return

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        
        ''' 
        Explanation for the below while loop code: 
        - The below code implements the actual frame extraction process using a loop. It reads frames from the video file 
        using self.cap.read(). If there are no more frames to read (ret is False), the loop breaks.
        - It calculates the current time in the video based on the frame count and frame rate.
        - If the current time is greater than or equal to the interval_seconds multiplied by the frame_skip count, a frame is 
        extracted. The frame is converted to grayscale using cv2.cvtColor for simplicity.
        - The extracted frame is saved as an image in the specified output_folder if it is different from the previous frame 
        (using the are_frames_identical method to compare frames). The frame is saved with a filename indicating its frame number.
        - The self.previous_frame variable is updated with the current grayscale frame for comparison in the next iteration.
       '''
        while True:
            ret, frame = self.cap.read()

            if not ret:
                break
            self.frame_count += 1

            current_time = self.frame_count / self.cap.get(cv2.CAP_PROP_FPS)

            if current_time >= self.frame_skip * interval_seconds:
                self.frame_skip += 1

                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if self.previous_frame is None or not self.are_frames_identical(gray_frame, self.previous_frame):
                    output_path = os.path.join(output_folder, f"frame_{self.frame_count}.jpg")
                    cv2.imwrite(output_path, frame)

                self.previous_frame = gray_frame

        self.cap.release()
        cv2.destroyAllWindows()  # After all frames are processed, OpenCV windows are destroyed using (cv2.destroyAllWindows())
