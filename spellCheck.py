# -*- coding: utf-8 -*-
"""

"""

from tqdm import tqdm
from pathlib import Path
import pandas as pd

import cv2
from nltk.metrics.distance import edit_distance
from wikiImageLib import convertWikiImageToText

cwd = Path.cwd()
inputDir = cwd.joinpath('inputData')
inputPaths = list(inputDir.glob('*'))
results = {}

for inputPath in tqdm(inputPaths):
    result = {}
    
    inputText = inputPath.joinpath('text.txt')
    trueText = inputText.read_text(encoding='utf-8')
    
    inputScreenshot = inputPath.joinpath('screenshot.png')
    inputImage = cv2.imread(str(inputScreenshot))
    inputImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2RGB)
    
    imageText = convertWikiImageToText(inputImage)
    distance = edit_distance(trueText, imageText)
    
    result['distance'] = distance
    result['trueTextLength'] = len(trueText)
    result['imageTextLength'] = len(imageText)
    results[inputPath.stem] = result
    
results = pd.DataFrame().from_dict(results, orient='index')
results.to_csv('results.csv', index=True)