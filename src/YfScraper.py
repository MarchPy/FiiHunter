import requests
import requests_cache
import pandas as pd
from io import StringIO
from datetime import datetime
from rich.console import Console




class YfScraper:
    def __init__(self, symbol: str, start_date: str, end_date: str, interval: str) -> None:
        self.__console = Console()
        self.symbol = symbol
        self.interval = interval
        self.start_date_timestamp, self.end_date_timestamp = self.__convert_data_to_timestamp(
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def __time():
        return datetime.now().strftime('%H:%M:%S')
    
    def collect_data(self) -> pd.DataFrame:
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }

        url = f"https://query1.finance.yahoo.com/v7/finance/download/{self.symbol}.SA?period1={self.start_date_timestamp}&period2={self.end_date_timestamp}&interval={self.interval}"
        
        with requests_cache.enabled('config/cache.db'):
            content = requests.get(url=url, headers=hdr).text

        df = pd.read_csv(filepath_or_buffer=StringIO(initial_value=content))
        if not df.empty:
            self.__console.print(f'[{self.__time()}] -> [[italic yellow]History data collected successfully[/]] :: {self.symbol}')
            
            return df
        
        else:
            self.__console.print(f'[{self.__time()}] -> [[italic red]History data not found[/]] :: {self.symbol}')

            return df
    
    def __convert_data_to_timestamp(self, start_date: str, end_date: str) -> tuple:
        start_data_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_data_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        return start_data_timestamp, end_data_timestamp
