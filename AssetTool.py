#!/usr/bin/env python
import logging

from argparse import ArgumentParser

from Parser.InvestmentParser    import ParseInvestements
from Report.HtmlReport          import GenerateReport
from Report.GhostfolioExporter  import ExportActivities
from HistoricalData.HistoryData import updateHistory

parser = ArgumentParser( prog='AssetTool', description='Import/Export/Analyze investments')
args = parser.add_argument('-p',  '--parse', action='store_true', help='Parse investment files and store in pickled format')
args = parser.add_argument('-r',  '--report', action='store_true', help='Generate investment report')
args = parser.add_argument('-e',  '--export', action='store_true', help='Export orderActivities.json for ghostfolio import')
args = parser.add_argument('-uh', '--updateHistory', action='store_true', help='Update historical data')

logging.basicConfig(handlers=[logging.StreamHandler()], format=logging.BASIC_FORMAT, level=logging.DEBUG)
args = parser.parse_args()

if args.updateHistory:
    updateHistory()
if args.parse:
    ParseInvestements()
if args.report:
    GenerateReport()
if args.export:
    ExportActivities()


