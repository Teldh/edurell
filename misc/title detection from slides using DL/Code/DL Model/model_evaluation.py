# Extract training and validation accuracy from the history
train_accuracy = history.history['accuracy'] # extracts the training accuracy values for each epoch from the history object and stores them in the train_accuracy variable
val_accuracy = history.history['val_accuracy'] # extracts the validation accuracy values for each epoch from the history object and stores them in the val_accuracy variable.

# Create a range of epochs for the x-axis
# It creates a range of values from 1 to the total number of epochs (+1) used during training. This range is typically used as 
# the x-axis values when plotting the training and validation accuracy.
epochs = range(1, len(train_accuracy) + 1)

# Plot training and validation accuracy
plt.figure(figsize=(10, 6)) # creates a new figure for the plot with a specific size (width: 10 inches, height: 6 inches)

''' This line plots the training accuracy values on the graph. The epochs variable is used for the x-axis, and train_accuracy is 
used for the y-axis. The label parameter specifies the label for the data, and marker='o' indicates that circular markers should 
be placed at the data points.'''
plt.plot(epochs, train_accuracy, label='Train Accuracy', marker='o')
plt.plot(epochs, val_accuracy, label='Validation Accuracy', marker='o') # plots the validation accuracy values on the same graph, using circular markers for data points.

plt.title('Train and Validation Accuracy') # sets the title of the plot to "Train and Validation Accuracy"
plt.xlabel('Epochs') # sets the label for the x-axis to "Epochs"
plt.ylabel('Accuracy') # sets the label for the y-axis to "Accuracy"
plt.legend() 
plt.grid(True) # adds a grid to the plot, making it easier to read the values
plt.show() # displays the plot

#Prints the summary of the model
'''
model.summary() function prints the summary of the model, displaying the architecture, number of parameters, and other details of each 
layer in the model. The summary is stored in the summary variable, although it is not used in the provided code snippet.
'''
summary = model.summary()
