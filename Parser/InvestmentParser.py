import logging
import pickle
import datetime
import multiprocessing

import pymupdf

from pathlib     import Path

from Tools.Configuration  import Config
from Tools.Definitons     import Transaction, TransactionType, InvalidFileException, ParseResult

from .OnvistaParser  import OnvistaParser
from .BaaderParser   import BaaderParser
from .ScalableParser import ScalableParser


def AnalyzeFile(filePath:Path) -> Transaction:
    logger = logging.getLogger(__name__)
    try:
        doc  = pymupdf.open(filePath) # open a document
        page = next(doc.pages(0))
        if page.search_for('onvista bank') or page.search_for('onvist a bank'):
            return OnvistaParser(doc).GetTransaction()
        elif page.search_for('Baader Bank AG'):
            return BaaderParser(doc).GetTransaction()
        elif page.search_for('Scalable Capital Bank GmbH') or page.search_for('Scalable Capital GmbH'):
            return ScalableParser(doc).GetTransaction()
        else:
            raise InvalidFileException("Invalid file")
    except InvalidFileException as e:
        logger.error(f'Error analyzing {filePath}: {e}')


def ParseInvestements():
    logger = logging.getLogger(__name__)
    config = Config()

    p = multiprocessing.Pool(16)

    transactions = []
    for t in p.imap_unordered(AnalyzeFile, config.GetFiles()):
        transactions.append(t)
        logger.info(f'Analyzed {len(transactions)}/{len(config.GetFiles())} pdf-files')

    transactions += config.GetTransactions()
    logger.info(f'Added {len(config.GetTransactions())} transactions specified in configuration')
    
    res = ParseResult(transactions=transactions)
    outputFile = config.GetOuputPath().joinpath('transactions.pickle')
    outputFile.write_bytes(pickle.dumps(res))

    logger.info(f'Parsed {len(transactions)} transactions -> Saved to {outputFile}')