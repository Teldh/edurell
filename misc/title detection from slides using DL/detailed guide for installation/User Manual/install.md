**Installing Python and Dependencies**

**1. Install Python:** 
* If you don't have Python installed, download and install it from the official Python website: [Python Downloads](https://www.python.org/downloads/).

**2. Install pip:**
* Pip is a package manager for Python. If your Python installation doesn't include pip, you can follow the instructions here to install it: 
     [Installing pip](https://pip.pypa.io/en/stable/installation/)

**3. Install required Python packages:**

Open your terminal or command prompt. Navigate to the directory where the code is located. Run the following command to install the required Python packages:

* _pip install opencv-python numpy Pillow tensorflow nltk pytesseract scikit-learn_     

**4. Install Tesseract OCR:**

1. Install Tesseract OCR:

* Visit the official Tesseract OCR GitHub page for Windows: https://github.com/UB-Mannheim/tesseract/wiki 
* Download the latest version of the Tesseract OCR installer for Windows (e.g., tesseract-OCR-w64-setup-vX.XX.X.exe) from the "Releases" section. Make sure to download the correct version (32-bit or 64-bit) based on your system architecture.
* Install Tesseract OCR by running the downloaded installer and following the installation wizard's instructions. During installation, you can choose the components you want to install, but it's recommended to install everything for a complete setup.

2. Add Tesseract to the system PATH:

   After installation, you'll need to add the Tesseract executable directory to your system PATH. Here's how to do it:
* Open the Windows Control Panel.
* Search for "Environment Variables" and select "Edit the system environment variables."
* In the "System Properties" window, click the "Environment Variables" button.
* Under the "System Variables" section, find the "Path" variable and select "Edit."
* Click "New" and add the path to the Tesseract executable directory. By default, it's something like C:\Program Files\Tesseract-OCR (but as our program is executed in the downloads folder it's better to download the Tesseract in C:\Users\User\Downloads to avoid any errors).

3. Install pytesseract using pip:

   Open a command prompt or terminal on your Windows machine and run the following command to install pytesseract:
   * _pip install pytesseract_
