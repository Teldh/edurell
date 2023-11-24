# This line defines a function named extract_features that takes one argument, frame. This function is designed to extract features from an input image frame.
def extract_features(frame):

    # Here, the frame is transformed using NumPy's np.expand_dims() function. It adds an extra dimension to the frame array along axis=0. 
    # This is done to make sure the frame is in the shape expected by the VGG16 model, which typically takes an array of shape (batch_size, height, width, channels).
    frame = np.expand_dims(frame, axis=0)

    # The frame is preprocessed using the preprocess_input function from the VGG16 model included in TensorFlow's Keras applications.
    frame = tf.keras.applications.vgg16.preprocess_input(frame)
    # This line returns the result of passing the preprocessed frame to the predict method of the vgg_model. The predict method applies the VGG16 model to the input data and generates a prediction. 
    # The result is then flattened using the flatten() method to create a one-dimensional array of features extracted from the image frame.
    return vgg_model.predict(frame).flatten()
