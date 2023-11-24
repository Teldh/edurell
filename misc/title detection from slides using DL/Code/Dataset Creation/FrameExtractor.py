"""
Created on Sat Jun 10 18:33:24 2023

@author: farhan
"""  

# These import statements bring in the necessary libraries, OpenCV (cv2) for working with video files and images and OS for interacting with the system.
import cv2
import os
    

class FrameExtractor:
    """
    The FrameExtractor class is designed for extracting frames from a video file at specified intervals
    and saving them to a designated output folder.
    
    Parameters:
    
    - video_path (str): The path to the input video file.
    - output_folder (str): The folder where extracted frames will be saved.
    """    
    
    def __init__(self, video_path, output_folder):         #     Initializes the FrameExtractor object.
        
        #These lines store the provided video_path and output_folder as attributes of the object so that they can be accessed throughout the class.
        self.video_path = video_path
        self.output_folder = output_folder

        # This line calls the get_interval_seconds() method to retrieve the interval gap in seconds between frame captures. 
        # This interval is stored as an attribute, interval_seconds.
        self.interval_seconds = self.get_interval_seconds()
        
    def are_frames_identical(self, frame1, frame2):
        """
        Checks if two frame objects are identical.

        Parameters:
        
        - frame1: First frame object   
        - frame2: Second frame object

        Returns:
        
        - bool: True if frames are identical, False otherwise
        """
        return (frame1 == frame2).all()
    
    def get_interval_seconds(self):
        """
        Gets the interval (in seconds) from the user to give a break of a few seconds between frame captures to avoid identical frame capturing.

        Returns:
        
        - int: The interval in seconds
        """

        # The code inside the loop is placed inside a try block to handle potential exceptions. The input line prompts the user to input the desired interval in seconds.
        # The os.path.basename(self.video_path) extracts the filename from the full path of the video file, which is used in the user prompt.
        while True:
            try:
                user_input = input(f"\nEnter the intervals in seconds after which you want to capture each frame for the video with name '{os.path.basename(self.video_path)}' (type 'stop' to terminate the program): ")
                print("\nProcessing...")

                # If the user enters 'stop', the program prints a message and uses exit() to terminate the program.
                if user_input.lower() == 'stop':
                    print("Program terminated by user.")
                    exit()  

                # If the user did not enter 'stop', the input is converted to an integer, assuming it's a valid interval value.
                interval_seconds = int(user_input)
                # This condition checks if the entered interval is a positive integer. If it is, the method returns the interval in seconds, and the loop terminates.
                if interval_seconds > 0:
                    return interval_seconds
                # If the entered interval is not a positive integer, an error message is printed.
                else:
                    print("\nInterval must be a positive integer.")
                    
            # This except block is executed if a ValueError exception is raised, which occurs when the user enters something that can't be converted to an integer.        
            except ValueError:
                print("\nPlease enter a valid integer for the interval.")
                
    def extract_frames(self):
        """
        Opens the video file, extracts frames with the help of the previous function defined, and saves the results to the output folder.
        """

        # A VideoCapture object is created by passing the video_path to it. This object is used to read the video frames.
        cap = cv2.VideoCapture(self.video_path)

        # This condition checks if the video file was successfully opened. If it wasn't, it means there was an issue opening the video file, an error message is printed, 
        # and the method returns, terminating further execution.
        if not cap.isOpened():
            print("/nError: Could not open the video file.")
            return

        # This condition checks if the specified output_folder exists. If it doesn't, the code proceeds to create the folder.
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # This variable is initialized to keep track of the number of frames processed.
        frame_count = 0
        # This variable will store the previous frame, which is used to compare with the current frame to detect changes.
        previous_frame = None
        # frame_skip is used to keep track of the frames to skip based on the interval specified by the user.
        frame_skip = 0

        # An infinite loop is started to iterate through the frames of the video.
        # cap.read() reads the next frame from the video. ret will be True if a frame is successfully read, and frame will contain the frame data.
        while True:
            ret, frame = cap.read()

            # This condition checks if the frame reading was unsuccessful, which happens when there are no more frames to read.
            # If there are no more frames to read, the loop is exited.
            if not ret:
                break

            # frame_count is incremented to keep track of the current frame being processed.
            frame_count += 1
            # current_time is calculated by dividing frame_count by the frames per second (FPS) of the video, giving the current time in seconds.
            current_time = frame_count / cap.get(cv2.CAP_PROP_FPS)

            # This condition checks if the current time is greater than or equal to frame_skip * self.interval_seconds. 
            # If it is, it means it's time to capture a frame based on the user-defined interval.
            if current_time >= frame_skip * self.interval_seconds:
                # frame_skip is incremented to keep track of how many frames have been skipped.
                frame_skip += 1

                # The current frame is converted to grayscale using cv2.cvtColor(). This step simplifies frame comparison.
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # This condition checks if the previous_frame is None (meaning it's the first frame) or if the current frame is not identical to the previous frame. 
                # If either condition is true, the current frame is saved.
                if previous_frame is None or not self.are_frames_identical(gray_frame, previous_frame):
                    # The path for saving the frame is constructed using os.path.join(). The filename includes the frame count for uniqueness.
                    output_path = os.path.join(self.output_folder, f"frame_{frame_count}.jpg")
                    # The current frame is saved to the output path using cv2.imwrite().
                    cv2.imwrite(output_path, frame)

                # The previous_frame is updated with the current grayscale frame for future comparison.
                previous_frame = gray_frame

        # After processing all frames, the video capture object is released to free up system resources.
        cap.release()
        # Finally, any OpenCV windows that may be open are closed.
        cv2.destroyAllWindows()
