"""
Created on Wed Sep 06 11:13:40 2023

@author: Mujtaba
"""

# These lines import necessary Python libraries and modules. Here's what each 
import tensorflow as tf  # Imports the TensorFlow library, a popular deep learning framework.
from PIL import Image  # Imports the Image module from the Python Imaging Library (PIL), which is used for working with images.
import numpy as np  # Imports the numpy library used for numerical operations, including handling arrays and matrices.
import os  #  Imports the os module, which provides functions for working with the operating system, including file and directory operations.


class FrameDetection:
    """
    FrameDetection is a class that encapsulates frame detection functionality using a pre-trained VGG16 model
    and a saved model for binary prediction on image features.

    Parameters:
    
    - data_dir (str): The directory containing image files for frame detection.
    - model_path (str): The file path to the saved binary prediction model.

    Attributes:
    
    - vgg_model (tf.keras.Model): A pre-trained VGG16 model loaded from TensorFlow's applications with pre-trained weights. It is configured to exclude the top layer and takes 3-channel images with a shape of (224, 324, 3).
    """
  
    def __init__(self, data_dir, model_path):
      
        self.data_dir = data_dir
        self.model_path = model_path
        self.vgg_model = tf.keras.applications.VGG16(weights='imagenet', include_top=False, input_shape=(224, 324, 3))
        self.vgg_model.trainable = False

    def perform_detection(self):
        """
        Performs predictions on images using the saved model to check whether they contain slides or not.

        Returns:
        
        - float: The percentage of images predicted as slides based on binary predictions. Returns None if no valid predictions were made.
        """
      
      #  Prints a message indicating that the saved model is being loaded.
        print(f"\nLoading the saved model")
      # Loads a pre-trained model from the specified file path (self.model_path) using TensorFlow's Keras API. This model will be used for making predictions.
        model = tf.keras.models.load_model(self.model_path)

      # Initializes an empty list to store the continuous predictions.
        predictions = []
      # Initializes an empty list to store binary predictions.
        binary_predictions = []

      #  Iterates through the files in the directory specified by self.data_dir.
        for filename in os.listdir(self.data_dir):
          # Constructs the full path of the image file.
            image_path = os.path.join(self.data_dir, filename)

          # Opens the image file using the PIL Image module.
            img = Image.open(image_path)
          # Resizes the image to a specific size of (324, 224).
            img = img.resize((324, 224))

          # Converts the opened image into a NumPy array, making it suitable for numerical operations.
            img_array = np.array(img)
          #  Converts the data type of the image array to float32.
            img_array = img_array.astype(np.float32)
          # Preprocesses the image using VGG16's preprocessing function to make it suitable for input to the VGG16 model.
            img_array = tf.keras.applications.vgg16.preprocess_input(img_array)

          # Passes the preprocessed image through the VGG16 model to obtain features. The result is flattened to a 1D array.
            img_features = self.vgg_model.predict(np.expand_dims(img_array, axis=0)).flatten()
          # Reshapes the features to match the expected input shape for the LSTM model.
            img_features = img_features.reshape(1, 1, -1)

          # Makes predictions using the loaded model on the image features.
            prediction = model.predict(img_features)
          # Appends the continuous predictions to the predictions list.
            predictions.append(prediction)

          #  Converts the continuous prediction to a binary prediction by thresholding at 0.5 (if greater, set to 1; otherwise, set to 0).
            binary_prediction = (prediction > 0.5).astype(int)
          #  Appends the binary prediction to the binary_predictions list.
            binary_predictions.append(binary_prediction)

      #  Checks if there are binary predictions in the binary_predictions list.
        if binary_predictions:
          # Calculates the slide percentage by taking the sum of binary predictions and dividing by the total number of predictions, then multiplying by 100.
            slide_percentage = (sum(binary_predictions) / len(binary_predictions)) * 100
          # Returns the calculated slide percentage.
            return slide_percentage

      #  If there are no binary predictions, i.e., binary_predictions is empty, returns None to indicate that no valid predictions were made.
        else:
            return None
