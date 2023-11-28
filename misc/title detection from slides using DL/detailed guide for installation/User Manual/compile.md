**COMPILING THE "DATASET CREATION" CODE**

Follow these steps to compile the dataset creation code:

* **Download the Code:** Download and save the python files (FrameExtractor.py, FramePreprocessor.py & DatasetCreator.py) on your system.

* **Important instructions:** You can have 50 videos categorized under non slide video dataset. The name of the videos should be of format V1,V2,V3 upto V50. If you want to extend the number of non slide videos, go to line 39 of FramePreprocessor.py:

  _if (folder_name.startswith('V') and ((len(folder_name) == 2 and folder_name[1].isdigit() and int(folder_name[1]) in range(1, 10)) or (len(folder_name) == 3 and folder_name[1:].isdigit() and int(folder_name[1:]) in range(1, 51)))):_

   and update the range from 51 up to your desired number.

**COMPILING THE "DL MODEL" CODE**

The model was trained on Google Colab, so you should also use Google Colab for the smooth execution of the code.

1. **Open Google Colab:** Mount your Google Drive with Colab and make the following directories on your Google Drive:
* My Drive/SE_Project/slides
* My Drive/SE_Project/non_slides
  
2. **Import dataset**: Upload the image dataset from slide and non-slide folders created using 'DatasetCreator.py' file in the slide and non_slide folders of your drive.

3. **Compile the Code:** Copy the code from the following files on your Colab file, and add a new code cell for each file:
   1. _important libs.py_
   2. _data_loader.py_
   3. _feature_extraction_function.py_ (A function for extracting features from an image using the VGG16 model)
   4. _VGG16_model_for_feature_extraction.py_
   5. _model.py_ (This file contains the Sequential model applied. You can modify this file if you want to train the model with some changes to check the performance)
   6. _model_evaluation.py_ (You can check the evaluation through this file. A graph is also plotted to show the comparison b/w train and validation accuracy)
   7. _model_prediction.py_ (The threshold of 0.5 is set to determine if the frame is a slide or not. Below 0.5 means the frame is not a slide)
   8. _save model_ (it's very important to save your model otherwise you'll have to train all the datasets again)

**COMPILING THE "VIDEO EVALUATION" CODE**

1. Once the model is saved, download the saved model to your system.
2. If you just want to execute the already-created model, go to the 'Saved DL Model for SlideDetection' file under the 'Video Evaluation' folder and download the model using the link and password mentioned in the file.
   
   **Note**: Please make sure to enter the correct tesseract_cmd & tessdata_dir_config path in line 81 & 82 of the VideoProcessing.py file before running
   the program.
4. Download the python files(FrameExtractor.py, FrameDetection.py, TitleExtraction.py, ConceptIdentifier.py & VideoProcessing.py) on your pc

