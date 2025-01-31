"""
Plagiarism Checker by Peter Ton

Problem Statement: Write a program to scan and output the similar sections of text between two input files.

This program searches through the two input files and detects similar sections of text between them.
A section of text is defined as a consecutive group of words with a specified word count.
To find similar sections of text, the program will search for common words between both text files.
Then, the program will compare text sections centered around a common word, counting the number of common words in both sections.
The program will output the sections of text between both files that are similar.

The program also must do this efficiently and quickly in order to handle large text files.
"""

searchRadius = 8 # How many words to search for to the left and right of a given word
percentCutoff = 40/100 # The cutoff ratio of similar words to total words in a text section

# Open and read the input files, removing line breaks, and storing the text in variables text1 and text2
inputFile1 = open("input1.txt", "r")
inputFile2 = open("input2.txt", "r")
text1 = inputFile1.read().replace("\n", " ").replace("\r", " ")
text2 = inputFile2.read().replace("\n", " ").replace("\r", " ")
inputFile1.close()
inputFile2.close()

# Create a structure for individual words and related information
class Word():
    """
    text: a string containing the actual text information
    startIndex: the index, relative to the original text file, of the first character in the word
    endIndex: the index, relative to the original text file, of the last character in the word
    wordIndex: the index of the word relative to the list of words
    nearbyWords: a set containing all unique words that are within the searchRadius of this word
    nearbyIndex: the indices, relative to the original text file, of the first and last character of the nearby text section
    """
    def __init__(self, text, startIndex, endIndex, wordIndex):
        self.text = text
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.wordIndex = wordIndex
        self.nearbyWords = set()
        self.nearbyIndex = []
    
    # Function to find nearby words within the search radius and the indices of the text section containing those nearby words
    def findNearbyWords(self, words, i, numOfWords):
        self.nearbyWords = set()
        self.nearbyIndex = [self.startIndex, self.endIndex]

        # Use the search radius to calculate a minimum and maximum word index to search through
        searchMin = self.wordIndex - searchRadius
        if self.wordIndex < searchRadius:
            searchMin = 0
        elif self.wordIndex > numOfWords - searchRadius - 1:
            searchMin = numOfWords - searchRadius*2 - 1
        searchMax = searchMin + searchRadius*2

        # Search for nearby words, starting from the previous word, going backward
        j = i-1
        while j >= 0:
            if words[j].wordIndex < searchMin:
                break
            self.nearbyWords.add(words[j].text)
            self.nearbyIndex[0] = words[j].startIndex
            j -= 1
        # Search for nearby words, starting from the next word, going forward
        j = i+1
        while j < len(words):
            if words[j].wordIndex > searchMax:
                break
            self.nearbyWords.add(words[j].text)
            self.nearbyIndex[1] = words[j].endIndex
            j += 1

# Function to format and extract words from the text extracted from a file
def extractWords(text):
    text = text.strip().lower() # Remove whitespace from the start and end of the text and set all letters to lowercase

    # Filter non-alphnumeric and non-space characters from the string and keep track of the remaining character's indices
    filteredText = ""
    charIndex = []
    for i in range(len(text)):
        char = text[i]
        if char.isalnum() or char == " ":
            filteredText += char
            charIndex.append(i)

    # Separate the words from the text into a list
    words = []
    startIndex = 0
    for i in range(len(filteredText)):
        char = filteredText[i]
        if char == " ":
            words.append(Word(filteredText[startIndex:i], charIndex[startIndex], charIndex[i-1], len(words)))
            startIndex = i+1
    words.append(Word(filteredText[startIndex:len(filteredText)], charIndex[startIndex], charIndex[len(filteredText)-1], len(words)))

    return words

# Function to create a dictionary to instantly retrieve a word's index, given the word
def findWordIndex(words):
    wordIndex = {}
    for i in range(len(words)):
        text = words[i].text
        if text not in wordIndex:
            wordIndex[text] = []
        wordIndex[text].append(i)
    return wordIndex

# Create a structure for text sections and related information
class TextComparison:
    """
    index1: the indices, relative to text file 1, of the first and last character in the first text section
    index2: the indices, relative to text file 2, of the first and last character in the second text section
    similarity: the number of similar words between the two compared text sections
    """
    def __init__(self, index1, index2, similarity):
        self.index1 = index1
        self.index2 = index2
        self.similarity = similarity


# Extract the words from the input file text
words1 = extractWords(text1)
words2 = extractWords(text2)
# Keep track of how many words are in the file
numOfWords1 = len(words1)
numOfWords2 = len(words2)
# If a file is too short, end the program
if numOfWords1 <= searchRadius*2:
    print("The length of file 1 is too short.")
    exit()
if numOfWords2 <= searchRadius*2:
    print("The length of file 2 is too short.")
    exit()

# Find common words between both sets of words
wordsSet1 = set()
wordsSet2 = set()
for word in words1:
    wordsSet1.add(word.text)
for word in words2:
    wordsSet2.add(word.text)
commonWords = wordsSet1.intersection(wordsSet2)

# Remove all words that are not common between both files
for i in range(len(words1)-1, -1, -1):
    if words1[i].text not in commonWords:
        words1.pop(i)
for i in range(len(words2)-1, -1, -1):
    if words2[i].text not in commonWords:
        words2.pop(i)

wordIndex1 = findWordIndex(words1)
wordIndex2 = findWordIndex(words2)

# Find and update the nearby words for all words in a file
for i in range(len(words1)):
    words1[i].findNearbyWords(words1, i, numOfWords1)
for i in range(len(words2)):
    words2[i].findNearbyWords(words2, i, numOfWords2)

# Find matching text sections
textComparisons = []
for word in words1: # For all words in the first file's word list
    # Find the locations of matching words in the second file's word list
    matches = wordIndex2[word.text]
    similarity = 0
    similarIndex1 = []
    similarIndex2 = []
    for match in matches:
        word2 = words2[match]
        nearby = word.nearbyWords.intersection(word2.nearbyWords)

        # The similarity of two text sections is the number of common words between their nearby word lists
        if similarity < len(nearby):
            similarity = len(nearby)
            similarIndex1 = word.nearbyIndex
            similarIndex2 = word2.nearbyIndex
    
    # If the similarity of the two text sections is past the cutoff, add it to a list
    if (similarity+1) / (searchRadius*2+1) >= percentCutoff:
        textComparisons.append(TextComparison(similarIndex1, similarIndex2, similarity))

# Sort the text sections from most similar to least similar
textComparisons.sort(key=lambda x: x.similarity, reverse=True)


# Filter out overlapping text sections so that you only have unique text sections
uniqueComparisons = []
for i in range(len(textComparisons)):
    textComparison = textComparisons[i]

    isOverlapping = False
    for uniqueComparison in uniqueComparisons:
        if textComparison.index1[0] <= uniqueComparison.index1[1] and textComparison.index1[1] >= uniqueComparison.index1[0]:
            isOverlapping = True
            break
    if not isOverlapping:
        uniqueComparisons.append(textComparison)

# For each similarity, print out the similar sections of text and write it to a file
outputFile = open("plagiarism_checker_output.txt", "w")
if len(uniqueComparisons) == 0:
    outputFile.write("No similarities found between file 1 and file 2.")
else:
    outputText = []
    for uniqueComparison in uniqueComparisons:
        output1 = text1[uniqueComparison.index1[0]:uniqueComparison.index1[1]+1]
        output2 = text2[uniqueComparison.index2[0]:uniqueComparison.index2[1]+1]
        outputText.append("There are " + str(uniqueComparison.similarity+1) + " similar words between the following:\n    '" + output1 + "'\n    '" + output2 + "'\n\n")
    outputFile.writelines(outputText)
    for text in outputText:
        print(text)
outputFile.close()