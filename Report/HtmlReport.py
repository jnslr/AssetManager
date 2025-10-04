import io
import pickle
from pathlib import Path
from dataclasses import asdict

import pandas as pd

import plotly.express as px

from Tools.Configuration import Config
from Tools.Definitons import ParseResult, TransactionType
from HistoricalData.HistoryData import getHistory

def GenerateReport():
    config  = Config()
    history = getHistory()

    parsedData = config.GetOuputPath().joinpath('transactions.pickle')
    
    res:ParseResult = pickle.loads(parsedData.read_bytes())
    records = [asdict(t) for t in res.transactions if t is not None]
    df = pd.DataFrame.from_records(records)
    df = df.sort_values(by=['date'])

    df.loc[df['type']==TransactionType.SELL,'quantity'] = -1*df.loc[df['type']==TransactionType.SELL,'quantity'] 
    df['netInvest'] = df['total'].where(df['type'] == TransactionType.BUY, other=0) - df['total'].where(df['type'] == TransactionType.SELL, other=0) 
    df['investWithCost'] = df['netInvest'] + df['cost'].fillna(0) + df['profit'].fillna(0)

    dividends    = df[df['type'] == TransactionType.DIVIDEND]
    transactions = df[df['type'].isin( [TransactionType.BUY, TransactionType.SELL] )]
    transactions['currentInvest'] = df['netInvest'].cumsum()

    totalRealizedProfit   = sum(df['profit'].where(df['type'] == TransactionType.SELL, other=0) )
    totalWithdrawnInvests = sum(df['total'].where( df['type'] == TransactionType.SELL, other=0)) - totalRealizedProfit

    perShareInvest =  transactions.groupby(['isin']).agg({'netInvest':'sum', 'investWithCost':'sum', 'quantity':'sum'})
    yearlyInvests   = transactions.groupby([lambda x: df['date'][x].year, 'isin']).agg({'netInvest':'sum'})
    totalInvests    = sum(transactions['netInvest'])
    currentInvest   = totalInvests-totalWithdrawnInvests

    yearlyDividends = dividends.groupby([lambda x: df['date'][x].year, 'isin']).agg({'total':'sum'})
    stockDividends  = dividends.groupby(['isin']).agg({'total':'sum'})
    totalDividends  = dividends.agg({'total':'sum'})

    transactionsTable = transactions.style
    transactionsTable.format(precision=2, thousands=".", decimal=",")
    transactionsTable.set_table_attributes('class="invest-table"')  



    fig = px.line(x=transactions['date'], y= transactions['currentInvest'], markers=True)
    investGraph = io.StringIO()
    fig.write_html(investGraph)

    # fig = px.line(x=list(history.values())[1].index, y=list(history.values())[1]['4. close'], markers=True)
    # investGraph = io.StringIO()
    # fig.write_html(investGraph)


    fig = px.bar(x=dividends['date'], y= dividends['total'])
    dividendGraph = io.StringIO()
    fig.write_html(dividendGraph)    

    style = f'''
    <style>
    table {{
        width: 100%;
    }}
    table, th, td {{
        border: 1px solid black;
        border-collapse: collapse;
    }}

    tr:nth-child(even) {{
        background-color: #D6EEEE;
    }}

    tr:hover {{background-color: #D6EEEE;}}

    </style>
    ''' 

    summary = f'''
    <h1>summary</h1>
    <h2>Investments</h>
    {investGraph.getvalue()}

    <h3>Transactions</h3>
    {transactionsTable.to_html(classes='transaction-table', index=False)}

    <h3>Yearly Invests</h3>
    {yearlyInvests.to_html()}

    <h3>Total per share</h3>
    {perShareInvest.to_html()}

    <h3>Total</h3>
    Total investments up to now: {totalInvests} € <br>
    Sold Investements: {totalWithdrawnInvests} € plus profit of {totalRealizedProfit} € <br>
    CurrentInvestment: {round(currentInvest)} €

    <h2>Dividends</h>
    {dividendGraph.getvalue()}


    {dividends.to_html(index=False)}


    <h3>Yearly Dividends</h3>
    {yearlyDividends.to_html()}
    '''
    config.GetOuputPath().joinpath('summary.html').write_text(style+summary)


if __name__ == '__main__':
    GenerateReport()