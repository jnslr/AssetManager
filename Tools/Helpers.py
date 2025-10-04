import re
import pymupdf

def getNumberFromText(text:str) -> float:
    numericText = text.replace('.','')
    numericText = re.sub(',','.', numericText)
    numericText = re.sub(r"[^\d\.]", "", numericText)
    return float(numericText)

def findBoundingRect(page: pymupdf.Page, needle:str, shiftX:int=0, shiftY:int=0, extendX:int = 0, extendY:int = 0, clip: pymupdf.Rect = None) -> pymupdf.Rect:
    rects = page.search_for(needle, clip=clip)
    if len(rects)<1:
        raise AssertionError(f'Needle {needle} not found in document {page.parent.name}')
    if len(rects)>1:
        raise AssertionError(f'Needle {needle} is not unique. It was found multiple times in document {page.parent.name} at {rects}')
    rect = rects[0]
    rect[0] += shiftX  # Move in x Direction
    rect[2] += shiftX  # Move in x Direction
    
    rect[1] += shiftY  # Move in y Direction
    rect[3] += shiftY  # Move in y Direction
    
    rect[2] += extendX # Increase x1(width)
    rect[3] += extendY # Increase y1(height)
    return rect

def moveRect(rect: pymupdf.Rect, moveX:int=0, moveY:int=0):
    rect[0] += moveX  # Move in x Direction
    rect[2] += moveX  # Move in x Direction
    
    rect[1] += moveY  # Move in y Direction
    rect[3] += moveY  # Move in y Direction

def setRectHeight(rect: pymupdf.Rect, height:int):
    rect[3] = rect[1]+height

def setRectWidth(rect: pymupdf.Rect, width:int):
    rect[2] = rect[0]+width

def findNumericValue(page: pymupdf.Page, needle:str, shiftX:int=0, shiftY:int=0, extendX:int=0, extendY:int=0, clip: pymupdf.Rect = None) -> float:
    rect = findBoundingRect(page,needle, shiftX, shiftY, extendX, extendY, clip)
    text = page.get_textbox(rect)
    return getNumberFromText(text)