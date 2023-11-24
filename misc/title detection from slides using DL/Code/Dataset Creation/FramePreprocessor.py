"""
Created on Sun Jul 23 14:22:12 2023

@author: Mujtaba
""" 

# Import statements that bring in the necessary libraries, OpenCV (cv2) for working with video files and images and OS for interacting with the system.
import cv2
import os

class FramePreprocessor:
    """
    A class for preprocessing & distinguishing the image frames as slide or non-slide from a specified data folder and saving the results in separate subdirectories.
    
    Parameters:
    
    - data_folder (str): The directory containing image frames to be preprocessed.
    - results_folder (str): The directory where the preprocessed results will be stored.
    """
    
    def __init__(self, data_folder,results_folder):
        # This line stores the provided data_folder and results_folder as an attribute of the object, so they can be accessed throughout the class.
        self.data_folder = data_folder
        self.results_folder = results_folder

    # This method, preprocess_frames(), is responsible for preprocessing the image frames found in the specified data_folder.
    def preprocess_frames(self):
        """
        Preprocess image frames from data_folder and save the results in slides and non_slides subdirectories of results_folder.
        """
        
        # These lines create two subdirectories, 'slides' and 'non_slides', inside the data_folder using os.makedirs() only if they do not already exist. 
        os.makedirs(os.path.join(self.results_folder, 'slides'), exist_ok=True)
        os.makedirs(os.path.join(self.results_folder, 'non_slides'), exist_ok=True)
        # A counter variable x is initialized to keep track of the processed frames.
        x = 0
        # This line retrieves the list of folder names within the data_folder.
        folder_names = os.listdir(self.data_folder)

        # A loop is started to iterate over the folder names in data_folder.
        for folder_name in folder_names:
            # folder_path is constructed by joining data_folder and the current folder_name. This will be the path to the current folder being processed.
            folder_path = os.path.join(self.data_folder, folder_name)
            # This condition checks whether there is a folder with the name 'results' and skips it because the same folder name is used to save the results
            if folder_name == "results":
                continue
            # This condition checks whether the folder_name meets certain criteria, suggesting that it contains non-slide frames. It checks if the folder name
            # starts with 'V', and then there are two sub-conditions: 
            # 1. If the length of the folder name is 2 (e.g., 'V2') and the second character is a digit between 1 and 9, or
            # 2. If the length of the folder name is 3 (e.g., 'V25') and the second and third characters are digits between 1 and 50.
            # If any of these conditions are met, it's assumed that the folder contains non-slide frames. Otherwise, it's assumed to contain slide frames.
            if (folder_name.startswith('V') and ((len(folder_name) == 2 and folder_name[1].isdigit() and int(folder_name[1]) in range(1, 10)) or (len(folder_name) == 3 and folder_name[1:].isdigit() and int(folder_name[1:]) in range(1, 51)))):
                output_folder = 'non_slides'
            else:
                output_folder = 'slides'

            # This condition checks if the folder_path corresponds to an existing directory
            if os.path.isdir(folder_path):
                # If it's a directory, this line retrieves a list of filenames (image frames) within that directory.
                data_files = os.listdir(folder_path)

                # A nested loop is started to iterate through the image frame files within the current folder. 
                #The variable i keeps track of the index in the loop, and filename represents the name of the current frame file.
                for i, filename in enumerate(data_files):
                    # frame_path is constructed by joining folder_path and the current filename, creating the full path to the frame.
                    frame_path = os.path.join(folder_path, filename)
                    # cv2.imread() is used to read the image frame from frame_path, and the frame data is stored in the frame variable.
                    frame = cv2.imread(frame_path)

                    # This condition checks if the frame was successfully loaded. If frame is not None, it means the image was loaded successfully.
                    if frame is not None:
                        # The frame is resized to a new size of 324x224 pixels using cv2.resize().
                        frame = cv2.resize(frame, (324, 224))
                        # An output_filename is constructed, specifying the directory structure and the filename for the preprocessed frame. 
                        # The x counter is used to ensure each file has a unique name.
                        output_filename = f'{self.results_folder}/{output_folder}/{output_folder.lower()}_{x}.jpg'
                        # The preprocessed frame is saved using cv2.imwrite().
                        cv2.imwrite(output_filename, frame)
                        # The x counter is incremented to prepare it for the next processed frame.
                        x += 1
                    # If the frame could not be loaded (e.g., if it's not a valid image file), an error message is printed.    
                    else:
                        print(f"Failed to load frame from {frame_path}")
