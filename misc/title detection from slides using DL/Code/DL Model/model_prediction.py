predictions = model.predict(X_test_sequences) # It uses the trained model to make predictions on the test data X_test_sequences

# Since we're working on a binary classification problem, we can convert the probabilities to binary labels (0 or 1) using a threshold (e.g., 0.5).
threshold = 0.5

'''
This line converts the predicted probabilities into binary labels. For each probability in the predictions array, it checks whether 
the probability is greater than the specified threshold. If it is, the corresponding binary label is set to 1; otherwise, it's set to 0. 
The .astype(int) function ensures that the resulting array contains integers (0s and 1s).
'''
binary_predictions = (predictions > threshold).astype(int)

'''
This line computes the predicted class labels based on the highest probability in each prediction row. np.argmax() returns the 
indices of the maximum values along the specified axis (axis=1 here, indicating rows). In the context of binary classification, 
this effectively determines whether class 0 or class 1 has the higher probability for each prediction.
'''
predicted_class = np.argmax(predictions, axis=1)


# Print the predictions
print("Predictions (Probabilities):")
# print the predicted probabilities for each test sample. Each row corresponds to a test sample, and the columns represent the 
# predicted probabilities for class 0 and class 1.
print(predictions)

''' print the binary predictions obtained by applying the threshold to the predicted probabilities. Each row in binary_predictions 
represents the binary label (0 or 1) predicted for the corresponding test sample based on the specified threshold. '''
print("\nBinary Predictions:")
print(binary_predictions)
