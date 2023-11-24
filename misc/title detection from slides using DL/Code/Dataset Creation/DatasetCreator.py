"""
Created on Fri Jul 28 15:56:19 2023

@author: Mujtaba
"""  

# These lines import the necessary modules and classes
import os     # for file and directory operations
from FrameExtractor import FrameExtractor   # for extracting frames from videos
from FramePreprocessor import FramePreprocessor   # preprocessing image frames

class DatasetCreator:
    """
    A class for creating a dataset by processing video files, extracting frames, and preprocessing the frames.
    
    Parameters:
    
    - video_folder (str): The directory where video files are located.
    - results_folder (str): The directory where results will be stored.
    """
    
    def __init__(self, video_folder='data', results_folder=None):
        # This line assigns the value of the video_folder parameter to the video_folder attribute of the class instance.
        self.video_folder = video_folder
        # If results_folder is None, this line creates a default results_folder by joining the video_folder with the subdirectory 'results' using the os.path.join function. 
        if results_folder is None:
            results_folder = os.path.join(video_folder, 'results')
        # This line assigns the value of the results_folder to the results_folder attribute of the class instance.
        self.results_folder = results_folder

    def process_videos(self):
        """
        Process video files in the specified folder, extract the frames and preprocess the frames using the classes imported.
        """
        
        # The infinite loop is started.
        while True:
            # This condition checks if a folder with the name 'data' already exists in the current directory.
            if os.path.exists(self.video_folder):
                #  If the 'data' folder exists, the user is prompted to either rename it or quit the program.
                user_input = input("\nA folder with the name 'data' already exists. Please rename it (type 'rename') and run the program again, or type 'quit' to terminate? ")
                # If the user chooses to rename, they are prompted to enter a new name for the folder. 
                # The os.rename() function is used to rename the 'data' folder to the new name provided by the user. After renaming the folder, the loop is exited.
                if user_input == 'rename':
                    new_name = input("Enter a new name for the 'data' folder: ")
                    os.rename(self.video_folder, new_name)
                    break
                # This condition checks if the user entered 'quit'. If the user chooses to quit, a termination message is printed, and the program is terminated using exit().    
                elif user_input == 'quit':
                    print("Program terminated.")
                    exit()
                # If the user enters an incorrect input, they are informed to enter either 'rename' or 'quit'.     
                else:
                    print("Incorrect input. Please type 'rename' or 'quit' to terminate.")
            # If there is no existing 'data' folder, this block of code is executed.        
            else:
                # Exit the loop if 'data' folder doesn't exist
                break

        # Create the 'data' folder if it doesn't exist
        os.makedirs(self.video_folder)
        print(f"\n'{self.video_folder}' Folder Created!")

        # These lines provide instructions for the user, explaining the naming convention for videos. 
        # Users are prompted to add videos to the 'data' folder and type 'yes' to continue.
        print(f"\nINSTRUCTIONS: Please note that for a non-slide video dataset, a video name should start with 'V' and contains 1 or 2 digits after 'V' (for example V1, V19 or V43). \n\nThe program works in such a way that the videos with names (V1, V2,...V50) will be categorized under non-slide videos, and videos with any other name will be categorized under slide videos. So you can have a dataset of 50 non-slide videos.\n\nOnce you have read the instructions, add the videos in '{self.video_folder}' folder accordingly and type 'yes' to continue")

        # The infinite loop is started.
        while True:
            # The user is prompted to enter either 'yes' to continue or 'quit' to terminate the program.
            user_input = input(f"\n\nType 'yes' to continue or 'quit' to terminate the program: ")
            # This condition checks if the user entered 'yes', indicating their intention to continue.
            if user_input == 'yes':
                # This condition checks if there are no files in the 'data' folder, which implies that the user has not added any video files, and prints the following message.
                if not os.listdir(self.video_folder):
                    print("Error: No video files in the folder. Please upload the dataset video files and then type 'yes' to continue.")
                # If there are video files, the loop is exited.
                else:
                    break
            # This condition checks if the user entered 'quit', prints the message and terminates the program using exit().        
            elif user_input == 'quit':
                print("Program terminated.")
                exit()
            # If the user enters an incorrect input, they are informed to enter either 'yes' or 'quit'.    
            else:
                print("Incorrect input. Please type 'yes' or 'quit.")

        # A loop is started to iterate over the files in the 'data' folder.
        for video_name in os.listdir(self.video_folder):
            # This condition checks if the file is not a video file (i.e., it doesn't have the '.mp4' extension).
            if not video_name.endswith('.mp4'):
                # If it's not a video file, a message is printed indicating that the file is skipped, and the loop continues to the next file.
                print(f"\nSkipping video '{video_name}' because it's not a video file")
                continue

            # If it is a video file, the full path to the video file is constructed.
            video_path = os.path.join(self.video_folder, video_name)
            # An output_folder path is constructed by removing the file extension(.mp4) from video_name. This is where the extracted frames will be saved.
            output_folder = os.path.join(self.video_folder, os.path.splitext(video_name)[0])
            # An instance of the FrameExtractor class is created, providing the video_path and output_folder as arguments to the constructor.
            frame_extractor = FrameExtractor(video_path, output_folder)
            # The extract_frames() method is called to extract frames from the video and save them in the specified output_folder.
            frame_extractor.extract_frames()

        # An instance of the FramePreprocessor class is created, providing the video_folder and results folder as an argument to the constructor.
        frame_preprocessor = FramePreprocessor(self.video_folder, self.results_folder)
        # The preprocess_frames() method is called to preprocess the extracted frames in the 'data' folder.
        frame_preprocessor.preprocess_frames()
        # A success message is printed to indicate that the program has executed successfully.
        print("\nProgram Executed Successfully")

# Checks if the script is being executed as the main program. 
if __name__ == "__main__":
    #  An instance of the DatasetCreator class is created
    dataset_creator = DatasetCreator()
    # The process_videos() method is called to execute the whole program
    dataset_creator.process_videos()
