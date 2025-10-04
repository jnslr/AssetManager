import json
import pickle

from Tools.Configuration import Config
from Tools.Definitons import ParseResult, TransactionType

def ExportActivities():

    config  = Config()
    
    parsedData = config.GetOuputPath().joinpath('transactions.pickle')
    res:ParseResult = pickle.loads(parsedData.read_bytes())
    res.transactions = [t for t in res.transactions if t is not None]

    activityDict = dict(activities=[])
    for order in res.transactions:
        orderType = "BUY"

        if order.type == TransactionType.SELL:
            orderType="SELL"

        if order.type != TransactionType.SELL and order.type != TransactionType.BUY:
            continue

        if order.cost is None:
            order.cost = 0.0
        
        activityDict["activities"].append({
            "accountId": None,
            "comment": None,
            "currency": order.currency,
            "dataSource": "YAHOO",
            "date": order.date.isoformat(),
            "fee": order.cost,
            "quantity": abs(order.quantity),
            "type": orderType,
            "unitPrice": order.stockPrice,
            "symbol": order.isin,
            "tags": []
        })


    activityFile = config.GetOuputPath().joinpath("orderActivities.json")
    activityFile.write_text(json.dumps(activityDict))