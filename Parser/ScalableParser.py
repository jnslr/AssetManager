import datetime
import pymupdf # imports the pymupdf library

from Tools.Definitons import Transaction, TransactionType, InvalidFileException
from Tools.Helpers import findBoundingRect
from Tools.Helpers import moveRect, setRectHeight, setRectWidth
from Tools.Helpers import getNumberFromText

class ScalableParser():
    def __init__(self, doc: pymupdf.Document):
        self.m_doc = doc
        self.m_page1 = next(self.m_doc.pages(0))
        
        self.m_transaction = None
        self.ParseType()
        self.m_infoArea = self.m_page1.get_drawings()[0]['rect']
        self.ParseIsin()     
        self.ParseDate()
        self.ParseTotal()
        self.ParseQuantity()
        self.ParseDividend()
        self.ParseStockPrice()

    def ParseType(self):
        self.m_type = None
        if self.m_page1.search_for('Wertpapierabrechnung'):
            self.m_type = TransactionType.BUY
        if self.m_page1.search_for('Dividende'):
            self.m_type = TransactionType.DIVIDEND
        
        if self.m_type is None:
            raise InvalidFileException(f'Document {self.m_doc.name} has unknown type')
        
    def ParseIsin(self):
        self.m_isin = None
        
        if self.m_type == TransactionType.BUY:        
            buyBox = findBoundingRect(self.m_page1, 'Kauf')
            moveRect(buyBox, moveX=buyBox.width, moveY=buyBox.height)
            setRectWidth(buyBox, 80)
            self.m_isin = self.m_page1.get_textbox(buyBox).strip()
            assert len(self.m_isin)==12
        if self.m_type == TransactionType.DIVIDEND:        
            isinBox = findBoundingRect(self.m_page1, 'ISIN')
            moveRect(isinBox, moveX=isinBox.width) # Move to the beginning of the isin
            setRectWidth(isinBox, self.m_page1.rect.width)
            self.m_isin = self.m_page1.get_textbox(isinBox).strip()
            assert len(self.m_isin)==12
        assert self.m_isin is not None

    def ParseDate(self):
        dateNeedle  = 'Datum'
        if self.m_type == TransactionType.DIVIDEND:
            dateNeedle = 'Ex Tag'
        dateBox = findBoundingRect(self.m_page1, dateNeedle)
        moveRect(dateBox, moveX=dateBox.width) # Move to the beginning of the date
        setRectWidth(dateBox, self.m_page1.rect.width)
        dateText    = self.m_page1.get_textbox(dateBox).strip()
        self.m_date = datetime.datetime.strptime(dateText,'%d.%m.%Y').date()

    def ParseTotal(self):
        self.m_currency = "EUR"
        if self.m_type == TransactionType.BUY:
            totalBox  = findBoundingRect(self.m_page1, 'Kauf')
            totalBox.x0 = (self.m_page1.rect.width-120) # Move to right-50
            setRectWidth(totalBox,120)
            totalText = self.m_page1.get_textbox(totalBox)
            self.m_total     = getNumberFromText(totalText)

        if self.m_type == TransactionType.DIVIDEND:
            bruttoRect  = findBoundingRect(self.m_page1, 'Gutschrift')
            bruttoRect.x0 = (self.m_page1.rect.width-110)
            setRectWidth(bruttoRect,110)
            totalText = self.m_page1.get_textbox(bruttoRect)
            self.m_total     = getNumberFromText(self.m_page1.get_textbox(bruttoRect))

    def ParseStockPrice(self):
        if not self.m_type == TransactionType.BUY:
            self.m_stockPrice = None
            return
        
        orderInfo = findBoundingRect(self.m_page1, 'Kauf')
        setRectWidth(orderInfo,self.m_page1.rect.width)
        
        priceBox = findBoundingRect(self.m_page1, 'STK', clip=orderInfo)
        moveRect(priceBox, moveX=priceBox.width)
        setRectWidth(priceBox, 55)
        priceText = self.m_page1.get_textbox(priceBox)

        self.m_stockPrice = getNumberFromText(priceText)
    
    def ParseQuantity(self):
        self.m_quantity = None

        if self.m_type == TransactionType.BUY:
            quantityBox = findBoundingRect(self.m_page1, 'Kauf')
            setRectWidth(quantityBox,self.m_page1.rect.width)
            quantityBox = findBoundingRect(self.m_page1, 'STK', clip=quantityBox)
            quantityBox.x0 = quantityBox.x0 - 100
            quantityText = self.m_page1.get_textbox(quantityBox).strip('Stk')
            self.m_quantity = getNumberFromText(quantityText)
        if self.m_type == TransactionType.DIVIDEND:
            quantityBox  = self.m_page1.search_for('Berechtigte Anzahl')[0]
            moveRect(quantityBox,moveX=quantityBox.width)
            setRectWidth(quantityBox,self.m_page1.rect.width)
            quantityText = self.m_page1.get_textbox(quantityBox)
            self.m_quantity     = getNumberFromText(quantityText)

        assert self.m_quantity is not None

    def ParseDividend(self):
        if not self.m_type == TransactionType.DIVIDEND:
            self.m_stockDividend = None
            self.m_stockCurrency = None
            return
        
        dividendBox  = findBoundingRect(self.m_page1, 'Gutschrift')
        dividendBox.x0 = dividendBox.x1
        dividendBox.x1 = self.m_page1.rect.x1

        priceText,countText,totalText = self.m_page1.get_textbox(dividendBox).strip().split('\n')
        
        self.m_stockCurrency = priceText.split()[1].strip()
        self.m_stockDividend = getNumberFromText(priceText.split()[0])       


    def GetTransaction(self) -> Transaction:
        return Transaction(
            date=self.m_date,
            type=self.m_type,
            isin=self.m_isin,
            quantity=self.m_quantity,
            stockPrice=self.m_stockPrice,
            stockDividend=self.m_stockDividend,
            stockCurrency=self.m_stockCurrency,
            total=self.m_total,
            currency=self.m_currency,            
        )