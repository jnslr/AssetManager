import requests
import pickle
import pandas as pd
import logging
from pathlib import Path

from Tools.Configuration import Config

API_URL  = 'https://www.alphavantage.co/query'

# See https://www.boerse-stuttgart.de/
# Search for ISIN, check SYMBOL in Stammdaten, append .DE
ISIN_TO_SYMBOL_MAP = {
    'IE00B4L5Y983': 'EUNL.DEX',
    'IE00BWTN6Y99': 'HDLV.DEX',
    'DE000A0H0744': 'EXXW.DEX',
    'IE00B1YZSC51': 'IQQY.DEX',
    'IE00B3RBWM25': 'VGWL.DEX',
    'IE00BJ0KDQ92': 'XDWD.DEX',
}

def updateIsinHistory(isin:str) -> pd.DataFrame:
    symbol = ISIN_TO_SYMBOL_MAP.get(isin)
    if symbol is None:
        raise AssertionError(f'ISIN {isin} not found')    

    params = {
        'apikey': Config().GetAlphaVantageApiKey(),
        'function': 'TIME_SERIES_DAILY',
        'outputsize': 'full',
        'symbol': symbol,
    }
    r = requests.get(API_URL, params=params)
    data = r.json()

    df = pd.DataFrame.from_records(data['Time Series (Daily)']).T
    df.index = pd.to_datetime(df.index)
    return df

def updateHistory():
    history = {}
    for isin in ISIN_TO_SYMBOL_MAP.keys():
        history[isin] = updateIsinHistory(isin)
        logging.getLogger(__name__).info(f'Updated history for {isin}: {history[isin].size} datapoints')

    getDataFile().write_bytes(pickle.dumps(history))

def getHistory():
    history = pickle.loads(getDataFile().read_bytes())
    return history

def getDataFile() -> Path:
    config = Config()
    return config.GetOuputPath().joinpath('history.pickle')
    