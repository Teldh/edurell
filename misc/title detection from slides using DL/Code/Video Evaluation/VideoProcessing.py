"""
Created on Wed Sep 27 19:23:12 2023

@author: Mujtaba
"""

import os  # for interacting with the operating system
from FrameExtractor import FrameExtractor  # class FrameExtractor imported from the FrameExtractor file.
from FrameDetection import FrameDetection  # class FrameDetection imported from the FrameDetection file.
from TitleExtraction import TitleExtraction # class TitleExtraction imported from the TitleExtraction file.
from ConceptIdentifier import ConceptIdentifier # class ConceptIdentifier imported from the ConceptIdentifier file.

class VideoProcessing:
  """
  VideoProcessing is a class that facilitates the processing of videos, including frame extraction, slide detection, title extraction, and concept identification.

  Parameters:
  
  - video_folder (str): Path to the folder containing the video file and subtitle file.
  """
  
  class NoSlidesException(Exception):
    """Exception class raised when no slides are detected in a video."""
    pass

  # This is the constructor of the VideoProcessing class. It takes the video_folder as a parameter and assigns it to an instance variable self.video_folder.
  def __init__(self, video_folder):
        self.video_folder = video_folder

  def process_video(self, video_name, subtitle_name):
        """
        Processes a video by extracting frames, detecting slides, extracting titles, and identifying concepts.

        Parameters:
        
        - video_name (str): Name of the video file.
        - subtitle_name (str): Name of the subtitle file.
        """
    
    # These lines construct the full paths to the video and subtitle files
        video_path = os.path.join(self.video_folder, video_name)
        subtitle_path = os.path.join(self.video_folder, subtitle_name)

    # These lines check if the video and subtitle files exist in the specified paths and store the results in the variables video_exists and subtitle_exists.
        video_exists = os.path.exists(video_path)
        subtitle_exists = os.path.exists(subtitle_path)

    # These lines check whether the video, subtitle, or both files are missing. If both are missing, it prints a message indicating that both are missing. 
    # If only the video is missing, it prints a message indicating that the video is missing. If only the subtitle is missing, 
    # it prints a message indicating that the subtitle is missing, and starts processing a new video
        if not video_exists and not subtitle_exists:
            print(f"\nVideo file '{video_name}' and subtitle file '{subtitle_name}' don't exist.\nProcessing a new Video now!")
        elif not video_exists:
            print(f"\nVideo file '{video_name}' doesn't exist.\nProcessing a new Video now!")
        elif not subtitle_exists:
            print(f"\nSubtitle file '{subtitle_name}' doesn't exist.\nProcessing a new Video now!")
          # If both the video and subtitle files exist, it proceeds to the following steps.
        else:

          # In this block, it enters a loop and asks the user for the interval (in seconds) to capture each frame. It repeatedly prompts for input until a valid integer
          # is entered. Once a valid interval is entered, it initializes output_folder as the video name(without extension) and uses a FrameExtractor 
          # to extract frames from the video at the specified interval.It then breaks out of the loop
            while True:
                intervals = input("\nAfter how many seconds do you want to capture each frame: ")
                if intervals.isdigit():
                    intervals = int(intervals)
                    print("\nProcessing ...")
                    output_folder = os.path.join(self.video_folder, os.path.splitext(video_name)[0])
                    frame_extractor = FrameExtractor(video_path)
                    frame_extractor.extract_frames(output_folder, intervals)
                    break
                else:
                    print("\nError: Please enter a valid integer for the interval.\n")
                  
         # In this block, it enters another loop where the user is prompted to check the frames that were captured. The user can enter 'yes' to proceed 
         # or any other input to continue checking. Once 'yes' is entered, it breaks out of the loop.
            while True:
                check_frames = input("\nPlease check the frames captured and delete if there are any identical frames captured. Once done, enter 'yes' to proceed, and any other input to continue checking): ")
                if check_frames.lower() == 'yes':
                    break

            # It creates an instance of the FrameDetection class with the path to the output_folder and the model_path.
            frame_detection = FrameDetection(output_folder, model_path)

            # It tries to perform slide detection using the perform_detection method of the frame_detection object. If successful, it prints the slide percentage.
            # If the slide percentage is greater than 80%, it prints that the video contains slides. If the slide percentage is less than 80%, 
            # it raises a NoSlidesException and prints a message. If any other exception occurs during the process, it prints the error message
            try:
                slide_percentage = frame_detection.perform_detection()
                print("The slide percentage is:", slide_percentage)
                if slide_percentage > 80:
                    print("\nThe video contains slides\n")
                if slide_percentage < 80:
                    raise self.NoSlidesException("\nThe video does not contain slides.\n\nProcessing new Video now!")
            except Exception as e:
                print(f"{str(e)}")
                return
              

            # These lines define the Tesseract OCR command (tesseract_cmd) and configuration (tessdata_dir_config) to be used for title extraction.
            # It creates an instance of the TitleExtraction class with the output_folder, tesseract_cmd, and tessdata_dir_config defined earlier.
            # It then extracts titles from the images in the output folder.
            tesseract_cmd = r'C:\Users\User\Downloads\Tesseract-OCR\tesseract.exe'  # The absolute path to the Tesseract executable on your system
            tessdata_dir_config = r'--tessdata-dir "C:\Users\User\Downloads\Tesseract-OCR\tessdata" --psm 6 -l eng'  # sets the directory where Tesseract should look for its data files.
            title_extraction = TitleExtraction(output_folder, tesseract_cmd, tessdata_dir_config)
            extracted_title = title_extraction.extract_titles_from_images()

            # It creates an instance of the ConceptIdentifier class with the video_folder and processes the subtitles along with the extracted titles using the process_subtitles method.
            concept_identifier = ConceptIdentifier(self.video_folder)
            concept_identifier.process_subtitles(subtitle_name, extracted_title)
            # After processing the video, it prints a message indicating that it's ready to process a new video.
            print("\nProcessing a new video now!")

# Check if the script is being run as the main program.
if __name__ == "__main__":

  # In this block, it enters a loop to prompt the user for a folder name where video processing will take place. The user enters a folder name, 
  # and it checks if the folder already exists. If the folder doesn't exist, it creates the folder using os.makedirs(video_folder) and sets video_folder to the 
  # provided name. If the folder already exists, it prints a message asking the user to choose a different name.
  while True:
    user_input_folder_name = input("\nEnter a folder name for video processing: ")
    if not os.path.exists(user_input_folder_name):
      video_folder = user_input_folder_name
      os.makedirs(video_folder)
      break
    else:
      print("\nFolder already exists. Please choose a different name.")


  # In this block, it enters another loop to prompt the user to upload a model file. It constructs the full path to the model file using the video_folder and the 
  # provided model_name. If the model file exists, it checks whether it's a .h5 file, it breaks out of the loop if there exists a .h5 file, 
  # otherwise prints the error message. If the user enters 'quit', it prints a termination message and exits the program.
  # If the model file doesn't exist, it prompts the user to upload the model file.
  while True:
    model_name = input(f"\nUpload the model file under '{video_folder}' folder and enter the model file name (with extension, e.g., model.h5) or enter 'quit' to terminate the program: ")
    model_path = os.path.join(video_folder, model_name)
    
    if os.path.exists(model_path):
      if model_path.endswith(".h5"):
        break
      else:
        print("\nInvalid model file. Expected a .h5 file.")
    elif model_name=='quit':
      print("\nProgram terminated by the user")
      exit()
    else:
      print("\nThe model file doesn't exist in the provided folder. Please upload the model file.")

  # In this block, it enters a loop to prompt the user to upload both the video and subtitle files. It checks the format of the uploaded files.
  # If the user enters 'quit', it prints a termination message and exits the program.If both the video and subtitle files are not in the correct format, 
  # it prints a message and continues the loop. If only the video or subtitle file is not in the correct format, it prints a message and continues the loop.
  # If both files are in the correct format, it proceeds to process the video using the VideoProcessing class.
  while True:
    video_name = input(f"\nUpload the video file under '{video_folder}' folder and enter the video file name here (with extension, e.g., video.mp4) or (Press 'quit' to exit): ")
    if video_name == 'quit':
      print("Program terminated by user")
      exit()
    subtitle_name = input(f"\nUpload the subtitle file under '{video_folder}' folder and enter the subtitle file name (with extension, e.g., subtitle.srt) or (Press 'quit' to exit): ")
    
    if subtitle_name == 'quit':
      print("Program terminated by user")
      exit()
    elif not video_name.endswith('.mp4') and not subtitle_name.endswith('.srt'):
      print("Both the video and subtitle files are not in the correct format.\n\nProcessing a new Video now!\n")  
    elif not video_name.endswith('.mp4'):
      print("The video file is not in the correct format.\n\nProcessing a new Video now!")
    elif not subtitle_name.endswith('.srt'):
      print("The subtitle file is not in the correct format.\n\nProcessing a new Video now!")     

    else:
      # It creates an instance of the VideoProcessing class with the video_folder and then calls the process_video method with the video_name and subtitle_name.
      # It handles any exceptions of type VideoProcessing.NoSlidesException and prints the exception message if it occurs.
            video_processing = VideoProcessing(video_folder)
            try:
                video_processing.process_video(video_name, subtitle_name)
            except VideoProcessing.NoSlidesException as e:
                print(str(e))
              
              
