import datetime
import pymupdf # imports the pymupdf library

from Tools.Definitons import Transaction, TransactionType, InvalidFileException
from Tools.Helpers import findBoundingRect
from Tools.Helpers import moveRect, setRectHeight, setRectWidth
from Tools.Helpers import getNumberFromText

class BaaderParser():
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
        if self.m_page1.search_for('Wertpapierabrechnung: Kauf'):
            self.m_type = TransactionType.BUY
        if self.m_page1.search_for('Fondsausschüttung'):
            self.m_type = TransactionType.DIVIDEND
        
        if self.m_type is None:
            raise InvalidFileException(f'Document {self.m_doc.name} has unknown type')
        
    def ParseIsin(self):
        isinBox     = findBoundingRect(self.m_page1, 'ISIN:', clip=self.m_infoArea)
        moveRect(isinBox, moveX=isinBox.width) # Move to the beginning of the isin
        setRectWidth(isinBox, 80)
        self.m_isin = self.m_page1.get_textbox(isinBox).strip()
        assert len(self.m_isin)==12
    
    def ParseDate(self):
        dateNeedle  = 'Auftragsdatum:'
        if self.m_type == TransactionType.DIVIDEND:
            dateNeedle = 'Ex-Tag:'
        dateBox     = findBoundingRect(self.m_page1, dateNeedle, clip=self.m_infoArea)
        moveRect(dateBox, moveX=dateBox.width) # Move to the beginning of the date
        setRectWidth(dateBox, 60)
        dateText    = self.m_page1.get_textbox(dateBox).strip()
        self.m_date = datetime.datetime.strptime(dateText,'%d.%m.%Y').date()

    def ParseTotal(self):
        self.m_currency = "EUR"
        if self.m_type == TransactionType.BUY:
            totalBox  = findBoundingRect(self.m_page1, 'Kurswert')
            totalBox.x0 = (self.m_page1.rect.width-120) # Move to right-50
            setRectWidth(totalBox,120)
            totalText = self.m_page1.get_textbox(totalBox)
            self.m_total     = getNumberFromText(totalText)

        if self.m_type == TransactionType.DIVIDEND:
            # Find the first Bruttobetrag that is given in EUR
            bruttoRects = self.m_page1.search_for('Bruttobetrag')
            for r in bruttoRects:
                setRectWidth(r,self.m_page1.rect.width)
            bruttoRect = [r for r in bruttoRects if "EUR" in self.m_page1.get_textbox(r)][0]
            bruttoRect.x0 = (self.m_page1.rect.width-120) # Move to right-120
            setRectWidth(bruttoRect,120)
            self.m_total     = getNumberFromText(self.m_page1.get_textbox(bruttoRect))

    def ParseStockPrice(self):
        if not self.m_type == TransactionType.BUY:
            self.m_stockPrice = None
            return
        priceBox = findBoundingRect(self.m_page1, 'Kurs', clip=self.m_infoArea)
        moveRect(priceBox,moveY=priceBox.height)
        self.m_stockCurrency = self.m_page1.get_textbox(priceBox).strip()
        moveRect(priceBox,moveX=priceBox.width)
        setRectWidth(priceBox,100)
        self.m_stockPrice = getNumberFromText(self.m_page1.get_textbox(priceBox))
    
    def ParseQuantity(self):
        quantityBox = findBoundingRect(self.m_page1, 'Nominale', clip=self.m_infoArea)
        moveRect(quantityBox,moveY=quantityBox.height)
        quantityBox = findBoundingRect(self.m_page1, 'STK', clip=quantityBox)
        moveRect(quantityBox,moveX=quantityBox.width)
        setRectWidth(quantityBox,50)
        self.m_quantity = getNumberFromText(self.m_page1.get_textbox(quantityBox))

    def ParseDividend(self):
        if not self.m_type == TransactionType.DIVIDEND:
            self.m_stockDividend = None
            self.m_stockCurrency = None
            return
        
        dividendBox  = findBoundingRect(self.m_page1, 'Ausschüttung', clip=self.m_infoArea)
        
        moveRect(dividendBox,moveY=dividendBox.height)
        setRectWidth(dividendBox,25)
        self.m_stockCurrency = self.m_page1.get_textbox(dividendBox).strip()

        moveRect(dividendBox, moveX=dividendBox.width)
        setRectWidth(dividendBox,100)
        self.m_stockDividend = getNumberFromText(self.m_page1.get_textbox(dividendBox))


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