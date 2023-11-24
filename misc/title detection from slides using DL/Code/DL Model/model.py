# Define the Sequential model
# A sequential model is appropriate for a plain stack of layers where each layer has exactly one input tensor and one output tensor.
model = tf.keras.Sequential([
    # The first LSTM layer to the model with 64 units (or cells). input_shape defines the shape of the input data. 
    LSTM(64, input_shape=(num_frames_per_video, X_train_features.shape[1]), return_sequences=True, kernel_regularizer=l2(0.01)),
    # Dropout is a regularization technique where a proportion (in this case, 60%) of randomly selected neurons are ignored during training to prevent overfitting.
    Dropout(0.6),
    # The second LSTM layer with 64 units, also returning sequences.
    LSTM(64, return_sequences=True, kernel_regularizer=l2(0.01)),
    # Dropout with a dropout rate of 40%.
    Dropout(0.4),
    # The third LSTM layer with 64 units and sequence output.
    LSTM(64, return_sequences=True, kernel_regularizer=l2(0.01)),
    # Dropout with a dropout rate of 20%.
    Dropout(0.2),
    # The Flatten layer is used to flatten the 3D output to 1D, preparing the data for the final dense layer.
    Flatten(),
    # A dense layer with 1 unit and a sigmoid activation function, which is often used for binary classification problems.
    Dense(1, activation='sigmoid', kernel_regularizer=l2(0.01))
])

# Compile the model
'''  This line compiles the model. It specifies the optimizer as Adam, binary crossentropy as the loss function (suitable for 
binary classification problems), and accuracy as the metric to monitor during training '''
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Define early stopping
''' It creates an EarlyStopping callback. also monitors the validation loss, waits for 5 epochs where the validation loss 
doesn't improve (patience=5), and restores the model's best weights when the monitoring quantity has stopped improving. '''
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model with more epochs
''' This line trains the model. It uses X_train_sequences as input sequences, y_train as the corresponding targets, runs 
for 20 epochs, uses a batch size of 32, and splits 20% of the training data for validation. The EarlyStopping callback is 
passed to monitor the validation loss and apply early stopping. '''
history = model.fit(X_train_sequences, y_train, epochs=20, batch_size=32, validation_split=0.2, callbacks=[early_stopping])

# Evaluate the model
# This line evaluates the trained model on the test data (X_test_sequences and y_test) and computes the loss and accuracy.
loss, accuracy = model.evaluate(X_test_sequences, y_test)
# Print the test accuracy achieved by the model after evaluation.
print(f"Test accuracy: {accuracy}")
   
