import datetime
import pymupdf # imports the pymupdf library

from Tools.Definitons import Transaction, TransactionType, InvalidFileException
from Tools.Helpers import findBoundingRect
from Tools.Helpers import moveRect, setRectHeight, setRectWidth
from Tools.Helpers import getNumberFromText

class OnvistaParser():
    def __init__(self, doc: pymupdf.Document):
        self.m_doc = doc
        self.m_page1 = next(self.m_doc.pages(0))
        
        self.m_transaction = None
        self.ParseType()
        self.m_infoArea = self.m_page1.get_drawings()[0]['rect']
        self.ParseIsin()     
        self.ParseDate()
        self.ParseTotal()
        self.ParseCost()
        self.ParseQuantity()
        self.ParseDividend()
        self.ParseStockPrice()
        self.ParseProfit()

    def ParseType(self):
        self.m_type = None
        if self.m_page1.search_for('Wir haben für Sie gekauft'):
            self.m_type = TransactionType.BUY
        if self.m_page1.search_for('Wir haben für Sie verkauft'):
            self.m_type = TransactionType.SELL
        if self.m_page1.search_for('Erträgnisgutschrift aus Wertpapieren'):
            self.m_type = TransactionType.DIVIDEND
        
        if self.m_type is None:
            raise InvalidFileException(f'Document {self.m_doc.name} has unknown type')
        
    def ParseIsin(self):
        isinBox     = findBoundingRect(self.m_page1, 'ISIN')
        moveRect(isinBox, moveY=isinBox.height) # Move to the beginning of the isin
        setRectWidth(isinBox, 100)
        setRectHeight(isinBox, isinBox.height*2)
        self.m_isin = self.m_page1.get_textbox(isinBox).strip()
        assert len(self.m_isin)==12
    
    def ParseDate(self):
        if self.m_type == TransactionType.DIVIDEND:
            dateBox = findBoundingRect(self.m_page1, 'Ex-Tag')
            moveRect(dateBox, moveY=dateBox.height) # Move to the beginning of the isin
            setRectWidth(dateBox, 70)
            setRectHeight(dateBox, dateBox.height*2)
            dateText    = self.m_page1.get_textbox(dateBox).strip()
            self.m_date = datetime.datetime.strptime(dateText,'%d.%m.%Y').date()
        if self.m_type in [TransactionType.BUY, TransactionType.SELL]:
            dateBox = findBoundingRect(self.m_page1, 'Handelstag')
            moveRect(dateBox, moveX=dateBox.width) # Move to the beginning of the date
            setRectWidth(dateBox, 100)
            dateText    = self.m_page1.get_textbox(dateBox).strip()
            self.m_date = datetime.datetime.strptime(dateText,'%d.%m.%Y').date()

    def ParseCost(self):
        self.m_cost = None
        if self.m_type == TransactionType.BUY:
            self.m_cost = 0
            try:
                costBox  = findBoundingRect(self.m_page1, 'Orderprovision')
                costBox.x0 = (self.m_page1.rect.width-120) # Move to right-50
                setRectWidth(costBox,120)
                costText = self.m_page1.get_textbox(costBox)
                self.m_cost += getNumberFromText(costText)
            except:
                pass
            try:
                costBox  = findBoundingRect(self.m_page1, 'Handelsplatzgebühr')
                costBox.x0 = (self.m_page1.rect.width-120) # Move to right-50
                setRectWidth(costBox,120)
                costText = self.m_page1.get_textbox(costBox)
                self.m_cost += getNumberFromText(costText)
            except:
                pass

    def ParseTotal(self):
        self.m_currency = "EUR"
        if self.m_type in [TransactionType.BUY, TransactionType.SELL]:
            totalBox  = findBoundingRect(self.m_page1, 'Kurswert')
            totalBox.x0 = (self.m_page1.rect.width-120) # Move to right-50
            setRectWidth(totalBox,120)
            totalText = self.m_page1.get_textbox(totalBox)
            self.m_total     = getNumberFromText(totalText)

        if self.m_type == TransactionType.DIVIDEND:
            dividendBox = findBoundingRect(self.m_page1, 'Betrag zu Ihren Gunsten')
            moveRect(dividendBox, moveY=dividendBox.height)
            dividendBox.x1 = self.m_page1.rect.x1           # Make it span up tu the right
            setRectHeight(dividendBox, dividendBox.height*2)
            self.m_total = getNumberFromText(self.m_page1.get_textbox(dividendBox))

    def ParseStockPrice(self):
        if not self.m_type in [TransactionType.BUY, TransactionType.SELL]:
            self.m_stockPrice = None
            return
        priceBox = findBoundingRect(self.m_page1, 'Kurs ')
        moveRect(priceBox,moveY=priceBox.height)
        setRectHeight(priceBox, priceBox.height*2)
        setRectWidth(priceBox, 150)
        self.m_stockCurrency = self.m_page1.get_textbox(priceBox).split(' ')[0]
        self.m_stockPrice = getNumberFromText(self.m_page1.get_textbox(priceBox))
    
    def ParseQuantity(self):
        quantityBox = findBoundingRect(self.m_page1, 'Nominal')
        moveRect(quantityBox,moveY=quantityBox.height)
        setRectHeight(quantityBox, quantityBox.height*2)
        quantityBox = findBoundingRect(self.m_page1, 'STK', clip=quantityBox)
        moveRect(quantityBox,moveX=quantityBox.width)
        setRectWidth(quantityBox,50)
        self.m_quantity = getNumberFromText(self.m_page1.get_textbox(quantityBox))

    def ParseDividend(self):
        if not self.m_type == TransactionType.DIVIDEND:
            self.m_stockDividend = None
            self.m_stockCurrency = None
            return
        
        dividendBox  = findBoundingRect(self.m_page1, 'Ausschüttungsbetrag pro Stück')
        
        moveRect(dividendBox,moveY=dividendBox.height)
        setRectHeight(dividendBox, dividendBox.height*2)
        setRectWidth(dividendBox,25)
        self.m_stockCurrency = self.m_page1.get_textbox(dividendBox).strip()

        moveRect(dividendBox, moveX=dividendBox.width)
        setRectWidth(dividendBox,100)
        self.m_stockDividend = getNumberFromText(self.m_page1.get_textbox(dividendBox))

    def ParseProfit(self):
        if not self.m_type == TransactionType.SELL:
            self.m_profit = None
            return
        soldBox  = findBoundingRect(self.m_page1, 'Gesamtveräußerungsergebnis vor Anwendung einer TFQ')
        soldBox.x0 = (self.m_page1.rect.width-120) # Move to right-50
        setRectWidth(soldBox,120)
        soldText = self.m_page1.get_textbox(soldBox)
        self.m_profit = getNumberFromText(soldText)

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
            cost = self.m_cost,
            profit=self.m_profit
        )
