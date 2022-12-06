# -*- coding: utf-8 -*-
# Library of functions used to convert a Wikipedia screenshot to text
# The only function which should be imported is convertWikiImageToText()
# All other functions are used internally and shouldn't be modified without an
# understanding of the full library


import cv2
import numpy
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def getLineCount(image: "numpy.ndarray") -> int:
    """
    A function which detects line of text in an input image and returns the number
    of lines detected.

    Parameters
    ----------
    image : numpy.ndarray
        Input image.    
    
    Returns
    -------
    int
        The number of lines detected in image.

    """
    gaussianBlurKernelSize = (5, 5)
    lineDetectionKernelSize = (20, 5)
    
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.GaussianBlur(image, gaussianBlurKernelSize, 0)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, lineDetectionKernelSize)
    image = cv2.dilate(image, kernel, iterations=1)

    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    return len(contours)


def getWordCount(image: "numpy.ndarray") -> int:
    """
    A function which detects words in an input image and returns the number
    of words detected.

    Parameters
    ----------
    image : numpy.ndarray
        Input image.

    Returns
    -------
    int
        The number of words detected in image.

    """
    
    gaussianBlurKernelSize = (5, 5)
    wordDetectionKernelSize = (3, 3)
    
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.GaussianBlur(image, gaussianBlurKernelSize, 0)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, wordDetectionKernelSize)
    image = cv2.dilate(image, kernel, iterations=1)

    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    return len(contours)


def getParagraphCount(image: "numpy.ndarray") -> int:
    """
    A function which detects paragraphs in an input image and returns the number
    of paragraphs detected.

    Parameters
    ----------
    image : numpy.ndarray
        Input image.

    Returns
    -------
    int
        The number of paragraphs detected in image.

    """
    
    gaussianBlurKernelSize = (5, 5)
    paragraphDetectionKernelSize = (5, 5)
    
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.GaussianBlur(image, gaussianBlurKernelSize, 0)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, paragraphDetectionKernelSize)
    image = cv2.dilate(image, kernel, iterations=1)

    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    return len(contours)


def getBackgroundColor(image: "numpy.ndarray") -> tuple:
    """
    Gets the background color of image. The backgroud color is determined
    by the most frequent color appearing in the image. This function assumes the 
    most frequent color is unique.

    Parameters
    ----------
    image : numpy.ndarray
        Input image.

    Returns
    -------
    tuple
        DESCRIPTION.

    """
    colorFreq = {}
    width, length, _ = image.shape
    
    for row in range(width):
        for column in range(length):
            pw = tuple(image[row, column])
            if pw not in colorFreq:
                colorFreq[pw] = 0
            colorFreq[pw]= colorFreq[pw] + 1
    backgroundColor = max(colorFreq, key=colorFreq.get)
    return backgroundColor


def contourWikipage(image: "numpy.ndarray") -> list:
    """
    Contours the full screenshot of a wikipedia article. This function is designed
    to detect contours which segment the wikipedia article into the side bar, 
    table of contents, main content, etc. 

    Parameters
    ----------
    image : numpy.ndarray
        Input image.

    Returns
    -------
    contours : list of numpy.ndarrays
        A list of contours which segment the article.

    """
    
    
    gaussianBlurKernelSize = (5, 5)
    contourWikiKernelSize = (6,10)
    
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    image = cv2.GaussianBlur(image, gaussianBlurKernelSize, 0)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, contourWikiKernelSize)
    image = cv2.dilate(image, kernel, iterations=3)

    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    return contours


def checkWikiTextContent(image: "numpy.ndarray") -> bool:
    """
    Checks if an image is cropped from a Wikipedia screenshot contains 
    content of the article. This is used to distinguish images of side banners, tables, 
    search bars, etc. from screenshots of the article's text. 
    An image is considered part of the article's text if:
        1) It contains at least 2 lines of text.
        2) It contains at least 10 words.
        3) Its background color is (255, 255, 255)

    Parameters
    ----------
    image : numpy.ndarray
        Input image.

    Returns
    -------
    bool

    """
    wikiBackgroundColor = (255, 255, 255)
    wordCount = getWordCount(image)
    sentenceCount = getLineCount(image)
    backgroundColor = getBackgroundColor(image)
    
    if sentenceCount>=2 and wordCount/sentenceCount >= 10:
        if backgroundColor == wikiBackgroundColor:
            return True
    return False


def criteriaToFill(image: "numpy.ndarray") -> bool:
    """
    Criteria to check if a contour shuold be filled with white. The criteria
    is checked using the image contained in the contour.
    The check is done by converting the image to a string using pytesseract.

    Parameters
    ----------
    image : "numpy.ndarray"
        Input image

    Returns
    -------
    bool
        Returne True is the image text starts with 'From Wikipedia' or '[edit]'
    """
    string = pytesseract.image_to_string(image)
    string = ''.join(string.split())
    if len(string)>=13 and string[:13] == 'FromWikipedia':
        return True
    elif len(string)>=6 and string == '[edit]':
        return True
    return False 


def fillText(image: "numpy.ndarray", criteriaToFill: callable) -> "numpy.ndarray":
    """
    Function to fill text in a wikipedia article with whitespace. This can be used to 
    ignore peices of text so they don't appear in the final output, e.g. the [edit]
    button

    Parameters
    ----------
    image : "numpy.ndarray"
        Input image.
    criteriaToFill : callable
        A callabe which whose only paramerter is a numpy.ndarray returns a bool. Used
        to determine if the image inside of a contour should be filled

    Returns
    -------
    numpy.ndarray
        The input image with the text filled

    """
    contoursToFill = []
    img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,3))
    img = cv2.dilate(img, kernel, iterations=3)

    contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        croppedImage = image[y:y+h, x:x+w]
        toFill = criteriaToFill(croppedImage)
        if toFill:
            contoursToFill.append(contour)
        
    
    if contoursToFill != []:
        cv2.fillPoly(image, pts = contoursToFill, color=(255,255,255))    
    return image 


def convertWikiImageToText(image: "numpy.ndarray") -> str:
    """
    

    Parameters
    ----------
    image : "numpy.ndarray"
        Input image.

    Returns
    -------
    str
        The text extracted from the wikipedia page.

    """
    imageText = ''
    content = []
    contours = contourWikipage(image.copy())
    
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        croppedImage = image[y:y+h, x:x+w]
        isTextContent = checkWikiTextContent(croppedImage)
        
        if isTextContent:
            content.append(croppedImage)
    content.reverse()
        
    for img in content:
        img= fillText(img, criteriaToFill)
        
        string = pytesseract.image_to_string(img)
        string = string.strip()
        imageText = imageText +'\n'+ string 
    return imageText
