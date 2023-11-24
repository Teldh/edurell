# This line creates a list slide_files containing the names of files in the directory 
# '/content/drive/My Drive/SE_Project/slides' that have the '.jpg' extension. It uses a list comprehension to filter the files with the '.jpg' extension.
slide_files = [f for f in os.listdir('/content/drive/My Drive/SE_Project/slides') if f.endswith('.jpg')]
# Similar to the previous line, this creates a list non_slide_files.
non_slide_files = [f for f in os.listdir('/content/drive/My Drive/SE_Project/non_slides') if f.endswith('.jpg')]

# This line creates a list slide_labels containing the label '1' repeated as many times as there are elements in the slide_files list. 
# These labels indicate that the corresponding images in slide_files are associated with slides.
slide_labels = [1] * len(slide_files)
# Similarly, this line creates a list non_slide_labels containing the label '0' repeated as many times as there are elements in the non_slide_files list. 
non_slide_labels = [0] * len(non_slide_files)

# Here, an empty list data is created. It is then populated with file paths for both slides and non-slides. 
# This is done by extending the data list with file paths for the images found in both the 'slides' and 'non_slides' directories. 
# The file paths are constructed by appending the file names to the respective directory paths.
data = []
data.extend(['/content/drive/My Drive/SE_Project/slides/' + file for file in slide_files])
data.extend(['/content/drive/My Drive/SE_Project/non_slides/' + file for file in non_slide_files])
# This line creates a labels list by concatenating the slide_labels and non_slide_labels lists. 
# It combines the labels for the slides and non-slides, matching them with the data in the data list.
labels = slide_labels + non_slide_labels

# These two lines convert the data and labels lists into NumPy arrays. 
# NumPy arrays are commonly used for numerical operations and are suitable for working with machine learning models.
data = np.array(data)
labels = np.array(labels)

# This line splits the data into training and testing sets using the train_test_split function from scikit-learn. 
# The data and labels arrays are split into X_train, X_test, y_train, and y_test. The test_size parameter specifies the proportion of data to include 
# in the testing set (in this case, 20%), and random_state sets the random seed for reproducibility.
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
