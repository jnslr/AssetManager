from pathlib import Path

from Tools.Definitons import Transaction

import json
import logging

class Config():
    def __new__(cls, *args, **kwds):
        instance = cls.__dict__.get("__instance__")
        if instance is not None:
            return instance
        cls.__instance__ = object.__new__(cls)
        cls.__instance__.init(*args, **kwds)
        return cls.__instance__

    def init(self):
        self.m_logger       = logging.getLogger(__name__)
        self.m_files        = []
        self.m_transactions = []
        
        self.m_configFile = Path(__file__).parent.parent.joinpath('config.json')
        self.m_outputDir  = Path(__file__).parent.parent.joinpath('output')
        self.m_outputDir.mkdir(exist_ok=True)

        self.m_config     = dict()

        try:
            if self.m_configFile.exists():
                self.m_config = json.loads(self.m_configFile.read_text())
            self.m_logger.info(f'Config loaded from {self.m_configFile}')
        except Exception as e:
            self.m_logger.error(f'Error loading config: {e}')

        for filePath in self.m_config.get('files', []):
            newFile = Path(filePath).expanduser()
            if not newFile.exists():
                self.m_logger.warning(f'Warning file or path {filePath} does not exist')
                continue
            if newFile.is_file():
                self.m_files.append(Path(filePath))
            if newFile.is_dir():
                self.m_files += list(newFile.glob('*.pdf'))
        self.m_logger.info(f'Found {len(self.m_files)} pdf-files for analysis')

        for t in self.m_config.get('transactions', []):
            self.m_transactions.append(Transaction(**t))
    
    def GetFiles(self) -> list[Path]:
        return self.m_files
    
    def GetTransactions(self) -> list[Transaction]:
        return self.m_transactions

    def GetOuputPath(self) -> Path:
        return self.m_outputDir
    
    def GetAlphaVantageApiKey(self) -> str:
        return self.m_config.get('aplhaVantageApiKey')
    
if __name__ == '__main__':
    logging.basicConfig(handlers=[logging.StreamHandler()], format=logging.BASIC_FORMAT, level=logging.DEBUG)
    Config()
