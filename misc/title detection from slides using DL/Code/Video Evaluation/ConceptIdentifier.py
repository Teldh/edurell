"""
Created on Fri Sep 15 14:34:21 2023

@author: Mujtaba
"""

# These lines import necessary Python libraries and modules.
import os  # provides functions for working with the operating system, including file and directory operations.
import re  # Allows working with regular expressions.
import nltk  # Imports the Natural Language Toolkit (NLTK) library for natural language processing.
from nltk.corpus import stopwords  # Imports the NLTK's stopwords corpus, which contains common stop words used for text analysis.
from nltk.tokenize import word_tokenize  # Imports a tokenizer from NLTK for word tokenization.

# These lines download NLTK data. The first line downloads the NLTK "stopwords" corpus, 
# and the second line downloads NLTK's "punkt" tokenizer models. These downloads are required for the NLTK functions used in the code.
nltk.download('stopwords')
nltk.download('punkt')


class ConceptIdentifier:
    """
    ConceptIdentifier is a class that identifies concepts related to specified keywords in video subtitles and the extracted titles.

    Parameters:
    
    - video_folder (str): Path to the folder containing the video subtitle file.
    """
    
    def __init__(self, video_folder):
        self.video_folder = video_folder

    def parse_srt(self, subtitle_path):
        """
        Parses a SubRip(.srt) subtitle file and extracts the relevant data.

        Parameters:
        
        - subtitle_path (str): Path to the SubRip subtitle file.

        Returns:
        
        - list: List of dictionaries containing subtitle data (index, start_time, end_time, text).
        """
        
      #  Initializes an empty list to store subtitle data.
        subtitles = []
      # opens the subtitle file specified by subtitle_path for reading, using UTF-8 encoding.
        with open(subtitle_path, "r", encoding="utf-8") as file:
          # Reads the contents of the file, splits it into subtitle blocks separated by two newlines ("\n\n"), and stores them in the lines list.
            lines = file.read().split("\n\n")
          # Processes each subtitle block:
            for line in lines:
              # Splits each subtitle block into its individual parts using newline characters.
                parts = line.split("\n")
              # Checks if there are at least three parts (index, timestamps, and text).
                if len(parts) >= 3:
                  
                  # Extracts relevant data from the subtitle block, such as the index, start and end timestamps, and the text. Appends this data as a 
                  # dictionary to the subtitles list and the method returns a list of subtitle data.
                    index = parts[0]
                    timestamps = parts[1].replace(",", ".").split(" --> ")
                    start_time = timestamps[0]
                    end_time = timestamps[1]
                    text = " ".join(parts[2:])
                    subtitles.append({
                        "index": int(index),
                        "start_time": start_time,
                        "end_time": end_time,
                        "text": text
                    })
        return subtitles

    def contains_keyword(self, subtitle_text, keyword):
        """
        Checks if a subtitle text contains any of the defined keywords along with the titles extracted and categorizes it as "Definition" or "In-depth Explanation."

        Parameters:
        
        - subtitle_text (str): Subtitle text.
        - keyword (str): Keywords from the subtitle text to check for.

        Returns:
        
        - str or None: "Definition" or "In-depth Explanation" if a match is found, None otherwise.
        """
      
        # Splits the keyword into individual words.
        split_keywords = keyword.split()
      #  Creates a list of regular expressions for each word in the keyword, ignoring case and looking for whole word matches.
        keyword_patterns = [re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE) for word in split_keywords]
      # Self-defined regular expressions that match phrases indicative of definitions or in-depth explanations.
        definition_pattern = re.compile(r'(refers to|means|is called|in the|signifies |denote|describe|represent|stands for|define|characterize|convey|serves as|imply|implies)', re.IGNORECASE)
        in_depth_pattern = re.compile(r'(explain|provides details about|elaborates on|significance|purpose|explore|examine|analyze|investigate|breaks down|comprehensive analysis)', re.IGNORECASE)

      # The method checks if any of the keyword patterns match the subtitle_text. If a match is found:
      # It checks if definition_pattern matches subtitle_text, and if so, returns "Definition."
      # It checks if in_depth_pattern matches subtitle_text, and if so, returns "In-depth Explanation."
      # If no match is found, it returns None.
        if any(pattern.search(subtitle_text) for pattern in keyword_patterns):
            if definition_pattern.search(subtitle_text):
                return "Definition"
            elif in_depth_pattern.search(subtitle_text):
                return "In-depth Explanation"
        return None

    def extract_keywords(self, subtitles):
        """
        Extracts unique keywords from subtitle texts after filtering the stop word (common words like "the," "and," etc.).

        Parameters:
        
        - subtitles (list): List of dictionaries containing subtitle data.

        Returns:
        
        - list: List of unique keywords.
        """

      # Initializes an empty set to store unique keywords.
        keywords = set()
      # The method iterates through each subtitle:
        for subtitle in subtitles:
          # Retrieves the subtitle text.
            text = subtitle["text"]
          # Tokenizes the text into individual words using NLTK's tokenizer.
            words = word_tokenize(text)
          
          # It checks each word to ensure it's not a stop word (common words like "the," "and," etc.) and that it consists of alphabetic characters.
          # If a word meets these criteria, it is added to the keywords set. The method returns the list of unique keywords.
            for word in words:
                if word.lower() not in stopwords.words('english') and word.isalpha():
                    keywords.add(word.lower())
        return list(keywords)

    def process_subtitles(self, subtitle_name, extracted_titles):
        """
        Processes video subtitles and extracted titles to identify concepts related to specified keywords.

        Parameters:
        
        - subtitle_name (str): Name of the subtitle file.
        - extracted_titles (list): List of extracted titles.

        Returns:
        
        - None
        """

      # Constructs the full path to the subtitle file.
        subtitle_path = os.path.join(self.video_folder, subtitle_name)
      # Parses the subtitle file and stores the subtitle data in the subtitles list.
        subtitles = self.parse_srt(subtitle_path)
      # extracts keywords from the subtitles and store them in subtitle_keywords.
        subtitle_keywords = self.extract_keywords(subtitles)
      # Initializes a dictionary called processed_subtitles with each keyword (from extracted_titles) as a key, and an empty set as the corresponding value.
        processed_subtitles = {keyword: set() for keyword in extracted_titles}

      
      # The method processes each title from extracted_titles: filtered_words is created by converting title words to lowercase and filtering out stop words.
      # split_keywords contains the individual words from the title, and the title itself is appended to ensure it's considered as a keyword.
      # It initializes found as False to keep track of whether a concept was found.
      # It then loops through the split_keywords and subtitle data to find matches:
      # If a keyword matches a word in the subtitle text and hasn't been processed yet for that title, it calls contains_keyword to check if the subtitle text 
      # contains a concept related to that keyword. If a concept is found, it prints information about it, including the keyword, timestamps, result 
      # (e.g., "Definition" or "In-depth Explanation"), and the subtitle text. It adds the index of the processed subtitle to the processed_subtitles set for that keyword. 
      # If no concept is found for a title, it prints that no definition or in-depth explanation was found.

        for title in extracted_titles:
            words = title.split()
            filtered_words = [word.lower() for word in words if word.lower() not in stopwords.words('english')]
            filtered_title = ' '.join(filtered_words)
            split_keywords = filtered_title.split()
            split_keywords.append(filtered_title)

            found = False

            for keyword in split_keywords:
                for subtitle in subtitles:
                    text = subtitle["text"]
                    if keyword.lower() in text.lower() and subtitle["index"] not in processed_subtitles[title]:
                        result = self.contains_keyword(text, keyword)
                        if result:
                            print(f"\nKeyword: {title}")
                            print(f"Timestamp {subtitle['start_time']} - {subtitle['end_time']}:\n{result}: {text}\n")
                            found = True

                        processed_subtitles[title].add(subtitle["index"])

            if not found:
                print(f"\nKeyword: {title}\nNo Definition or In-depth Explanation found\n")
