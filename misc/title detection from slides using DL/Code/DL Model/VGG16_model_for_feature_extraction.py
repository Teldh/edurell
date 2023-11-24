# This line initializes a VGG16 model using TensorFlow's Keras API. The weights='imagenet' argument specifies that the pre-trained weights for the VGG16 model 
# on the ImageNet dataset should be used. include_top=False means that the final fully connected layers of the VGG16 model (used for classification) are not included,
# as you intend to use the model for feature extraction. input_shape=(224, 324, 3) sets the input shape of the model to 324x224 pixels with 3 color channels (RGB).
vgg_model = tf.keras.applications.VGG16(weights='imagenet', include_top=False, input_shape=(224, 324, 3))

# This line sets the trainable attribute of the VGG16 model to False, indicating that you want to freeze the model's weights. 
# This means that the model's pre-trained weights won't be updated during training, and it will act as a fixed feature extractor.
vgg_model.trainable = False

# This line extracts features from each frame in the training set, X_train, using the extract_features function defined earlier. It iterates over each frame
# in X_train, reads the image using OpenCV (cv2.imread(frame)), extracts features, and collects these features into an array X_train_features.
# The resulting array contains features for each frame in the training set.
X_train_features = np.array([extract_features(cv2.imread(frame)) for frame in X_train])
# Similar to the previous line, this line extracts features from each frame in the testing set, X_test, and stores them in the array X_test_features.
X_test_features = np.array([extract_features(cv2.imread(frame)) for frame in X_test])

# This line sets the number of frames to 1. It indicates that each video is treated as a sequence of single frames, and you want to consider one frame at a time for analysis.
num_frames_per_video = 1 

# These lines calculate the number of samples in the training set (num_samples) and ensure it's a multiple of the num_frames_per_video. 
# This ensures that you're working with a number of frames that is evenly divisible by the number of frames you want to consider per video.
num_samples = X_train_features.shape[0]
num_samples -= num_samples % num_frames_per_video

# Here, the features in X_train_features are reshaped to represent sequential data. The reshaping is done by taking the first num_samples features and arranging 
# them into a three-dimensional array with dimensions (number_of_samples, num_frames_per_video, feature_dim). This structure represents the features for each video,
# with each video containing num_frames_per_video frames.
X_train_sequences = X_train_features[:num_samples].reshape(-1, num_frames_per_video, X_train_features.shape[1])

# This line adjusts the labels for the training set (y_train) to match the number of samples used in X_train_sequences. 
# This ensures that the labels correspond to the number of video frames considered.
y_train = y_train[:num_samples]  # Ensure that y_train matches the number of samples

# Similar to the training set, these lines calculate the number of samples in the testing set (num_samples_test) and ensure it's a multiple of num_frames_per_video.
num_samples_test = X_test_features.shape[0]
num_samples_test -= num_samples_test % num_frames_per_video

# Here, the features in X_test_features are reshaped in the same way as the training set to represent sequential data. This creates a similar structure for the testing set
X_test_sequences = X_test_features[:num_samples_test].reshape(-1, num_frames_per_video, X_test_features.shape[1])

# Just like with the training set, this line adjusts the labels for the testing set (y_test) to match the number of video frames considered in X_test_sequences. 
# This ensures that the labels correspond to the number of video frames in the testing set.
y_test = y_test[:num_samples_test]
