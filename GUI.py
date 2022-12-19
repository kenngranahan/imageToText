# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 14:59:48 2022

@author: User
"""

import tkinter as tk
from wikiImageLib import convertWikiImageToText
import PIL
from PIL import ImageGrab
from pathlib import Path
import io
import numpy as np
import cv2


class GraphicsInterface:
    
    def __init__(self, root):
        self.root = root
        self.textConverter = None
        self.image = None
        self.tkImage = None
        
        self.text = tk.Text(self.root, state=tk.DISABLED)
        self.xTextScrollBar = tk.Scrollbar(self.text, orient=tk.HORIZONTAL)
        self.yTextScrollBar = tk.Scrollbar(self.text, orient=tk.VERTICAL)
        
        self.xTextScrollBar.config(command = self.text.xview)
        self.yTextScrollBar.config(command = self.text.yview)
        
        self.text.config(xscrollcommand = self.xTextScrollBar.set)
        self.text.config(yscrollcommand = self.yTextScrollBar.set)
        
        self.xTextScrollBar.pack(side=tk.BOTTOM, fill=tk.X)
        self.yTextScrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        
    
        self.imageCanvas = tk.Canvas(self.root)
        self.imageCanvas.bind('<Button-1>', self.focusCanvas)
        self.imageCanvas.bind('<Control-v>', self.pasteImage)
        self.imageCanvas.bind('<Return>', self.convertToText)
        
        self.xImageScrollBar = tk.Scrollbar(self.imageCanvas, orient=tk.HORIZONTAL)
        self.yImageScrollBar = tk.Scrollbar(self.imageCanvas, orient=tk.VERTICAL)
        
        self.xImageScrollBar.config(command = self.imageCanvas.xview)
        self.yImageScrollBar.config(command = self.imageCanvas.yview)
        
        self.imageCanvas.config(xscrollcommand = self.xImageScrollBar.set)
        self.imageCanvas.config(yscrollcommand = self.yImageScrollBar.set)
        
        self.xImageScrollBar.pack(side=tk.BOTTOM, fill=tk.X)
        self.yImageScrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        self.imageCanvas.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
        
        
    
    def focusCanvas(self, event):
        self.imageCanvas.focus_set()
    
    def pasteImage(self, event):
        clipboardImage = ImageGrab.grabclipboard()
        if isinstance(clipboardImage, list):
            for entry in clipboardImage.copy():
                if entry[-4:] == '.png':
                    clipboardImage = PIL.Image.open(str(Path(entry)))
                    break
        elif clipboardImage is None:
            return None
        self.image = clipboardImage
        
        imageBytes = io.BytesIO()
        self.image.save(imageBytes, format=self.image.format)
        imageBytes = imageBytes.getvalue()
        self.tkImage = tk.PhotoImage(data=imageBytes)
        
        self.imageCanvas.create_image((0,0), image=self.tkImage, anchor ='nw')
        self.imageCanvas.config(scrollregion = self.imageCanvas.bbox(tk.ALL))
        self.xImageScrollBar.config(command=self.imageCanvas.xview)
        self.yImageScrollBar.config(command=self.imageCanvas.yview)
    
    def setTextConverter(self, converter):
        self.textConverter = converter
    
    def convertToText(self, event):
        if (self.setTextConverter is not None) and (self.image is not None):
            cv2Image = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            imageText = self.setTextConverter(cv2Image)
            self.setText(imageText)
        
    
    def setWindowTitle(self, title):
        self.root.title(title)
        
    def setImage(self, image):
        self.image = image
        imageBytes = io.BytesIO()
        self.image.save(imageBytes, format=self.image.format)
        imageBytes = imageBytes.getvalue()
        self.tkImage = tk.PhotoImage(data=imageBytes)
        
        self.imageCanvas.create_image((0,0), image=self.tkImage, anchor ='nw')
        self.imageCanvas.config(scrollregion = self.imageCanvas.bbox(tk.ALL))
        self.xImageScrollBar.config(command=self.imageCanvas.xview)
        self.yImageScrollBar.config(command=self.imageCanvas.yview)
    
    def getImage(self):
        return self.image
    
    def getText(self):
        return self.text
    
    def setText(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.insert(1.0, text)
        self.text.config(state=tk.DISABLED)
        self.xTextScrollBar.config(command=self.text.xview)
        self.yTextScrollBar.config(command=self.text.yview)


root = tk.Tk()
GI = GraphicsInterface(root)
GI.setWindowTitle('Wiki Image Converter')
GI.setTextConverter = convertWikiImageToText



if image is not None:
    print(image)
    #cv2Image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #imageText = convertWikiImageToText(cv2Image)
    #GI.setText(imageText)

root.mainloop()
