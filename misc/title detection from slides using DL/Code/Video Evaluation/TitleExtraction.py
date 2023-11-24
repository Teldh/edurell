'''
Created on Fri Sep 08 23:19:44 2023

@author: farhan
'''

import os                              # for file operations
import pytesseract                     #  for using the Tesseract OCR engine
from PIL import Image                  # from the PIL (Python Imaging Library) for handling images
import cv2                             # from OpenCV for image processing tasks

class TitleExtraction:
    """
    TitleExtraction is a class that performs title extraction from images using Tesseract OCR.

    Parameters:
    
    - folder_path (str): Path to the folder containing images for title extraction.
    - tesseract_cmd (str): Path to the Tesseract OCR executable.
    - tessdata_dir_config (str): Configuration options for Tesseract OCR.
    """
    
    def __init__(self, folder_path, tesseract_cmd, tessdata_dir_config):
       
        self.folder_path = folder_path
        self.tesseract_cmd = tesseract_cmd
        self.tessdata_dir_config = tessdata_dir_config

    def preprocess_image_for_ocr(self, image_path):
        """
        Preprocesses an image for OCR.

        Parameters:
        
        - image_path (str): Path to the image file.

        Returns:
        
        - PIL.Image: Processed image for OCR.
        """

        ''' It reads the image using OpenCV, converts it to grayscale, applies binary thresholding, and inverts the colors. 
        The processed image is then converted back to a PIL Image and returned. '''
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        inverted_thresh = cv2.bitwise_not(thresh)
        return Image.fromarray(inverted_thresh)    

    def extract_titles_from_images(self):
        """
        Extracts titles from images in the specified folder using Tesseract OCR.

        Returns:
        
        - list: List of extracted titles.
        """

        ''' It initializes an empty list titles to store extracted titles. It then iterates through the image files in the folder, reads each image, 
        preprocesses it using the preprocess_image_for_ocr method, and extracts text using Tesseract OCR.
        It splits the extracted text into lines and iterates through them. If a non-empty line is found, it is considered as the title. If 
        a title is found and it is not already in the titles list, it is added to titles and printed as the extracted title. If the title is 
        repeated, it prints a message indicating the repetition. If no text is found in the image, it prints a corresponding message.
        '''
        titles = []
        data_files = os.listdir(self.folder_path)

        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        for i, filename in enumerate(data_files):
            image_path = os.path.join(self.folder_path, filename)
            preprocessed_image = self.preprocess_image_for_ocr(image_path)
            text = pytesseract.image_to_string(preprocessed_image, config=self.tessdata_dir_config)
            lines = text.split('\n')
            title = None

            for line in lines:
                stripped_line = line.strip()
                if stripped_line:
                    title = stripped_line
                    break

            if title:
                if title not in titles:
                    titles.append(title)
                    print("Title:", title)
                else:
                    print("Title repeated:", title, "in the image:", filename)
            else:
                print("No text found in the image:", filename)

        # returns the list of extracted titles
        return titles
