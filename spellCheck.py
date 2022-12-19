# -*- coding: utf-8 -*-
"""

"""

from tqdm import tqdm
from pathlib import Path
import pandas as pd
import numpy as np

import cv2
from nltk.metrics.distance import edit_distance
from wikiImageLib import convertWikiImageToText

cwd = Path.cwd()
maxHeight = 15000
inputDir = cwd.joinpath('inputData')
inputPaths = list(inputDir.glob('*'))
results = {}


if cwd.joinpath('results.csv').exists():
    resultsDf = pd.read_csv('results.csv', index_col=0)
    results = resultsDf.to_dict(orient='index')    

for idx, inputPath in enumerate(tqdm(inputPaths)):
    
    if inputPath.stem not in results:
        result = {}
        
        inputText = inputPath.joinpath('text.txt')
        trueText = inputText.read_text(encoding='utf-8')
        
        inputScreenshot = inputPath.joinpath('screenshot.png')
        inputImage = cv2.imread(str(inputScreenshot))
        h, _, _ = inputImage.shape
    
        if h > maxHeight:
            result['distance'] = np.nan
            result['trueTextLength'] = len(trueText)
            result['imageTextLength'] = np.nan
            results[inputPath.stem] = result
        else:
            
            inputImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2RGB)
            
            imageText = convertWikiImageToText(inputImage)
            with inputPath.joinpath('imageText.txt').open('w') as f:
                f.write(imageText)
            distance = edit_distance(trueText, imageText)
            
            result['distance'] = distance
            result['trueTextLength'] = len(trueText)
            result['imageTextLength'] = len(imageText)
            results[inputPath.stem] = result
            
        if idx%5==0:
            resultsDf = pd.DataFrame().from_dict(results, orient='index')
            resultsDf.to_csv('results.csv', index=True)

    
resultsDf = pd.DataFrame().from_dict(results, orient='index')
resultsDf.to_csv('results.csv', index=True)