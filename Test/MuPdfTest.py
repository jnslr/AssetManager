import re
import datetime
from pathlib import Path
#from InvestmentParser import Transaction
import pymupdf # imports the pymupdf library

from Definitons import Transaction, TransactionType
from Helpers import findBoundingRect
from Helpers import moveRect, setRectHeight, setRectWidth
from Helpers import getNumberFromText
from OnvistaParser import OnvistaParser
from ScalableParser import ScalableParser



dir = Path('/home/jonas/Documents/BankingNeu/SC')
for p in dir.glob('*.pdf'):
    doc = pymupdf.open(p) # open a document
    try:
        print(ScalableParser(doc).GetTransaction())
    except Exception as e:
        print(f'Error in file {p}')
        print(e)

# dir = Path('/home/jonas/Documents/Banking/Kontoauszüge/Baader/')
# for p in dir.glob('*.pdf'):
#     doc = pymupdf.open(p) # open a document
#     try:
#         print(BaaderParser(doc).GetTransaction())
#     except AssertionError as e:
#         print(e)

# dir = Path('/home/jonas/Documents/Banking/Kontoauszüge/OnVista/')
# for p in dir.glob('*.pdf'):
#     doc = pymupdf.open(p) # open a document
#     try:
#         print(OnvistaParser(doc).GetTransaction())
#     except AssertionError as e:
#         print(e)
    
    
    #for page in doc: # iterate the document pages
        # text = page.get_text() # get plain text encoded as UTF-8
        # print(text)
        # blocks = page.get_text("blocks")
        # blocks.sort(key=lambda b: (b[1], b[0]))
        # for b in blocks:
        #     print(b)


        # infoArea = page.get_drawings()[0]['rect']
        
        # stockPrice = findNumericValue(page, 'Kurs ', extendX=100, extendY=50, clip=infoArea)
        # quantiy    = findNumericValue(page, 'STK',   extendX=50,  clip=infoArea)
        
        # isinBox  = findBoundingRect(page, 'ISIN:', extendX=80, clip=infoArea)
        # isinText = page.get_textbox(isinBox)
        # isin     = isinText.split(' ')[1]

        # dateBox  = findBoundingRect(page, 'Auftragsdatum: ', extendX=60, clip=infoArea)
        # dateText = page.get_textbox(dateBox)
        # date     = datetime.datetime.strptime(dateText.split('\n')[1],'%d.%m.%Y').date()

        # totalBox  = findBoundingRect(page, 'Zu Lasten Konto', extendX=500)
        # totalText = page.get_textbox(totalBox)
        # total     = getNumberFromText(totalText.split('\n')[-1])

        # print(stockPrice,quantiy, isin,date, total)

        # r = page.search_for('Kurs ')[0] # Rect(x0,y0,x1,y1) x=horizontal dir y=vertical dir
        # r[3] += 50 # Increase y1(height)
        # r[2] += 100 # Increase x1(width)
        # print(page.get_textbox(r))
        #findValue(page, 'Kurs ', extendX=100, extendY=50, useMatch=0)
