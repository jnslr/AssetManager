import csv
import json

from datetime import date, datetime
from dataclasses import dataclass
from pathlib import Path

@dataclass
class HistoryExchangeRate:
    """Class for keeping tra"""
    date: date
    value: float

def LoadHistoryData():
    historyDataPath = Path(__file__).parent.joinpath("HistoricalData/history_1390634-2014-10-05-Y10.csv")
    
    historyData = []
    with open(historyDataPath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile,delimiter=';')
        for r in reader:
            date  = datetime.strptime(r["Datum"], "%d.%m.%Y").date()
            value = float(r["Schluss"].replace(',','.'))
            historyData.append(HistoryExchangeRate(date,value))
    return historyData


EUR_Shares = ["DE000A0H0744", "IE00B1YZSC51"]

def ExportOrders(orderList):
    exchangeEURUSD = LoadHistoryData()
    activityDict = dict(activities=[])
    for order in orderList:
        orderType = "BUY"
        if order.quantity <0:
            orderType="SELL"

        if order.isin in EUR_Shares:
            unitPrice = order.unitPrice
            currency = "EUR"
        else:
            exchangeRate = [e.value for e in exchangeEURUSD if e.date == order.date][0]
            unitPrice = order.unitPrice*exchangeRate
            currency = "USD"
        
        activityDict["activities"].append({
            "currency": currency,
            "dataSource": "YAHOO",
            "date": order.date.isoformat(),
            "fee": 0,
            "quantity": abs(order.quantity),
            "type": orderType,
            "unitPrice": unitPrice,
            "symbol": order.isin
        })


    activityFile = Path(__file__).parent.joinpath("orderActivities.json")
    activityFile.write_text(json.dumps(activityDict))