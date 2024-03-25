import os
import json
import requests
import numpy as np
import pandas as pd
import requests_cache
from time import sleep
from bs4 import BeautifulSoup
from rich.console import Console
from src.YfScraper import YfScraper
from datetime import datetime, timedelta


class FiiHunter:
    def __init__(self) -> None:
        self.version = "1.0.0"
        self.author = "MarchPy"
        self.github = "https://github.com/MarchPy/FiiHunter"
        self._console = Console()
        self.__headers = {
            "Host": "fundamentus.com.br",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7"
        }
        self.__settings = self.__openSettings()

    def _helloMessage(self):
        helloMessage = f"""
        ███████╗██╗██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
        ██╔════╝██║██║    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
        █████╗  ██║██║    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ███████╔╝
        ██╔══╝  ██║██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
        ██║     ██║██║    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║ Author: {self.author}
        ╚═╝     ╚═╝╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ Version: {self.version}
        github: {self.github}

        Foram encontrados - {len(self.__settings['funds'])} - fundo(s)
        """     
        os.system(command='cls' if os.name == 'nt' else 'clear')
        self._console.print(helloMessage)        
        sleep(5)
    
    def __openSettings(self) -> dict:
        try:
            with open(file='config/settings.json', mode='r', encoding='utf-8') as fileObj:
                settings = json.load(fp=fileObj)
                return settings

        except FileNotFoundError:
            self._console.print(f'[{self.__time()}] -> [[italic red]Settings file not found.[/]]')
            return {}

    @staticmethod
    def __time() -> str:
        return datetime.now().strftime(format='%H:%M:%S')

    @staticmethod
    def __date() -> str:
        return datetime.now().strftime(format='%d-%m-%Y')

    def fundamentus(self) -> pd.DataFrame:
        data = []
        symbols = self.__settings['funds']

        idx = 1
        with requests_cache.enabled('config/cache.db'):
            for symbol in symbols:
                symbol = symbol.upper()
                self._console.print(f'[{self.__time()}] -> [[italic yellow]Collecting fundamental data for ticker[/]]-[{idx} of {len(symbols)}] :: {symbol} -> ', end='')

                url = f"http://fundamentus.com.br/detalhes.php?papel={symbol}"
                try:
                    content = requests.get(url=url, headers=self.__headers)
                    content.raise_for_status()  # Raises an exception for 4xx or 5xx status codes

                    soup = BeautifulSoup(content.content, 'html.parser')

                    if soup.find(string='Nenhum papel encontrado') is None:
                        tables = soup.find(name='div', attrs={'class': 'conteudo clearfix'})
                        tables = soup.find_all(name='table', attrs={'class': 'w728'})

                        # -------- Proper way to identify the values -------- #
                        # numTable = 4
                        # print("\n\n")
                        # print(f'Contains -{len(tables)}- tables.')
                        # i = 0
                        # for index, row in zip(tables[numTable].find_all(name='td', attrs={'class': 'label'}), tables[numTable].find_all(name='td', attrs={'class': 'data'})):
                        #     print(i, index)
                        #     print(i, row)
                        #     print('\n')
                        #     i += 1
                        # input("\n\n")
                        # ---------------------------------------------------- #

                        # Tabela 0
                        ativo = tables[0].find_all(name='td', attrs={'class': 'data'})[0].text
                        preco = float(tables[0].find_all(name='td', attrs={'class': 'data'})[1].text.replace('.', '').replace(',', '.'))
                        nome = tables[0].find_all(name='td', attrs={'class': 'data'})[2].text
                        precoMinimo52Sem = float(tables[0].find_all(name='td', attrs={'class': 'data'})[5].text.replace('.', '').replace(',', '.'))
                        segmento = tables[0].find_all(name='td', attrs={'class': 'data'})[6].text
                        precoMaximo52Sem = float(tables[0].find_all(name='td', attrs={'class': 'data'})[7].text.replace('.', '').replace(',', '.'))
                        volumeMedio2m = int(tables[0].find_all(name='td', attrs={'class': 'data'})[9].text.replace('.', ''))

                        # Tabela 1
                        nTotalCotas = int(tables[1].find_all(name='td', attrs={'class': 'data'})[1].text.replace('.', ''))
                        relatorio = (lambda x: x['href'] if x is not None else "-")(x=tables[1].find_all(name='td', attrs={'class': 'data'})[2].find(name='a'))

                        # Tabela 2
                        dividendYield = (lambda x: float(x.replace('%', '').replace('.', '').replace(',', '.')) if x != '-' else 0)(x=tables[2].find_all(name='td', attrs={'class': 'data'})[4].text)                        
                        pvp = float(tables[2].find_all(name='td', attrs={'class': 'data'})[7].text.replace(',', '.'))
                        vpCota = (lambda x: float(x.replace('.', '').replace(',', '.')) if x != '-' else 0)(x=tables[2].find_all(name='td', attrs={'class': 'data'})[8].text)
                        dividendoCota = (lambda x: float(x.replace('.', '').replace(',', '.')) if x != '-' else 0)(x=tables[2].find_all(name='td', attrs={'class': 'data'})[5].text)
                        ffoCota = (lambda x: float(x.replace('.', '').replace(',', '.')) if x != '-' else 0)(x=tables[2].find_all(name='td', attrs={'class': 'data'})[5].text)
                        ffoYield = (lambda x : float(x.replace('%', '').replace('.', '').replace(',', '.')) if x != '-' else 0)(x=tables[2].find_all(name='td', attrs={'class': 'data'})[1].text)                        
                        ativos = int(tables[2].find_all(name='td', attrs={'class': 'data'})[25].text.replace('.', ''))
                        patrimLiq = int(tables[2].find_all(name='td', attrs={'class': 'data'})[26].text.replace('.', ''))
                        receita3m = (lambda x: int(x.replace('.', '')))(x=tables[2].find_all(name='td', attrs={'class': 'data'})[12].text)
                        receita12m = (lambda x: int(x.replace('.', '')))(x=tables[2].find_all(name='td', attrs={'class': 'data'})[13].text)
                        rendDistrib3m = (lambda x: int(x.replace('.', '')))(x=tables[2].find_all(name='td', attrs={'class': 'data'})[21].text)
                        rendDistrib12m = (lambda x: int(x.replace('.', '')))(x=tables[2].find_all(name='td', attrs={'class': 'data'})[22].text)

                        # Tabela 4
                        qtdImoveis = int(tables[4].find_all(name='td', attrs={'class', 'data'})[0].text)
                        qtdUnidades = (lambda x: int(x) if x != '' else 0)(x=tables[4].find_all(name='td', attrs={'class', 'data'})[3].text)                        
                        areaM2 = int(tables[4].find_all(name='td', attrs={'class', 'data'})[1].text.replace('.', ''))
                        capRate = (lambda x: float(x.replace('.', '').replace(',', '.').replace('%', '')) if x != '-' else 0)(x=tables[4].find_all(name='td', attrs={'class', 'data'})[2].text)
                        vacMedia = (lambda x: float(x.replace('%', '').replace(',', '.')) if x != '-' else 0)(x=tables[4].find_all(name='td', attrs={'class', 'data'})[5].text)
                        precoM2 = (lambda x: int(x.replace('.', '')) if x != '-' else 0)(x=tables[4].find_all(name='td', attrs={'class', 'data'})[7].text)

                        data.append(
                            [
                                ativo, segmento, nome, preco, precoMinimo52Sem, precoMaximo52Sem, volumeMedio2m, ativos, patrimLiq, receita3m,
                                rendDistrib3m, receita12m, rendDistrib12m, nTotalCotas, dividendYield, dividendoCota, pvp, vpCota, ffoCota, ffoYield,
                                qtdImoveis, qtdUnidades, areaM2, capRate, vacMedia, precoM2, relatorio
                            ]
                        )

                        self._console.print('[[bold green]Data collected successfully[/]]')

                    else:
                        self._console.print('[[bold red]Data not found[/]]')

                except requests.RequestException as e:
                    self._console.print(f"Error fetching data for {symbol}: {e}")
                    continue

                idx += 1

        columns = [
            'Ativo', 'Segmento', 'Nome', 'Cotação', 'Preço 52sem (Min)', 'Preço 52sem (Max)', 'Vol $ méd (2m)', 'Ativos',
            'Patrim. Líquido', 'Receita (3m)', 'Rend. Distribuído (3m)', 'Receita (12m)', 'Rend. Distribuído (12m)', 'N° total de cotas', 'Div. Yield', 'Dividendo/cota', 'P/VP', 'VP/Cota', 'FFO/Cota', 'FFO Yield',
            'Qtd. Imóveis', 'Qtd. Unidades', 'Área (m2)', 'Cap Rate', 'Vacância média', 'Preço do m2', 'Relatório'
        ]
        dfFundamentus = pd.DataFrame(data=data, columns=columns)
        return dfFundamentus

    def technicalIndicators(self, dataframe: pd.DataFrame):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        end_date = end_date.strftime(format='%Y-%m-%d')
        start_date = start_date.strftime(format='%Y-%m-%d')

        dataframe = dataframe.copy()
        dataframe['Volat. Anualizada'] = 0.0
        for index, row in dataframe.iterrows():
            symbol = row['Ativo']
            try:
                df_yf = YfScraper(symbol=symbol, start_date=start_date, end_date=end_date, interval='1d').collect_data()
                if not df_yf.empty:
                    df_yf['daily_return'] = df_yf['Close'].ffill().pct_change()
                    desvio_padrao = df_yf['daily_return'].std()
                    volatilidade_anual = (desvio_padrao * np.sqrt(252)) * 100

                    dataframe.loc[index, 'Volat. Anualizada'] = float(f'{volatilidade_anual:.2f}')

                else:
                    dataframe.loc[index, 'Volat. Anualizada'] = 0

            except Exception as e:
                self._console.print(f"Error fetching technical indicators for {symbol}: {e}")

        return dataframe

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            condition_1 = dataframe['Div. Yield'] >= self.__settings['filter']['Dividend yield (Min)']
            condition_2 = dataframe['Vol $ méd (2m)'] > self.__settings['filter']['Volume médio 2m (Min)']
            condition_3 = dataframe['Qtd. Imóveis'] >= self.__settings['filter']['Quantidade de imóveis (Min)']
            condition_4 = dataframe['P/VP'] < self.__settings['filter']['P/VP (Max)']
            condition_5 = dataframe['P/VP'] > self.__settings['filter']['P/VP (Min)']
            condition_6 = dataframe['Vacância média'] < self.__settings['filter']['Vacância média (Max)']
            condition_7 = dataframe['Cap Rate'] >= self.__settings['filter']['Cap Rate (Min)']
            condition_8 = dataframe['Volat. Anualizada'] <= self.__settings['filter']['Volat. Anualizada (Max)']
            condition_9 = dataframe['VP/Cota'] > dataframe['Cotação'] if self.__settings['filter']['VP/Cota > Cotação'] else dataframe['Ativo'] == dataframe['Ativo']

            filter_ = (
                (condition_1) &
                (condition_2) &
                (condition_3) &
                (condition_4) &
                (condition_5) &
                (condition_6) &
                (condition_7) &
                (condition_8) &
                (condition_9)
            )

            return dataframe[filter_]

        except KeyError as e:
            self._console.print(f"Error filtering data: {e}")
            return pd.DataFrame()

    def saveFile(self, dataframe: pd.DataFrame) -> None:
        folder = self.__settings['diretorioResultado']
        try:
            os.makedirs(folder, exist_ok=True)

        except OSError as e:
            self._console.print(f"Error creating directory: {e}")
            return

        try:
            filename = f"FII Results ({self.__date()}).xlsx"
            dataframe.to_excel(excel_writer=os.path.join(folder, filename), index=False)
            self._console.print(f'[[bold yellow]Result saved to excel[/]] -> ({os.path.join(folder, filename)})')

        except Exception as e:
            self._console.print(f"Error saving file: {e}")

    def ranking(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe.copy()
        dataframe['Ranking'] = 0
        try:
            for column in self.__settings['ranking']:
                if self.__settings['ranking'][column] == "Max":
                    index = dataframe[(dataframe[column] == dataframe[column].max())].index.values
                    dataframe.loc[index[0], 'Ranking'] += 1 if len(index) == 1 else 0

                elif self.__settings['ranking'][column] == "Min":
                    index = dataframe[(dataframe[column] == dataframe[column].min())].index.values
                    dataframe.loc[index[0], 'Ranking'] += 1 if len(index) == 1 else 0

        except KeyError as e:
            self._console.print(f"[[red]Error ranking data[/]]: {e}")
            exit(code=1)

        return dataframe.sort_values(by='Ranking', ascending=False)

    def displayResult(self, dataframe: pd.DataFrame) -> None:
        self._console.print(f'\n\n[{self.__time()}] -> [[italic bold green]Resultado final resumido[/]]:')
        self._console.print(dataframe[['Ativo', 'Nome', 'Segmento', 'Cotação', 'VP/Cota', 'Div. Yield', 'P/VP', 'Dividendo/cota', 'Cap Rate', 'Qtd. Imóveis', 'Qtd. Unidades', 'Vacância média', 'Volat. Anualizada', 'Ranking']].to_string(index=False) + "\n" if not dataframe.empty else "[bold red]Nenhuma oportunidade encontrada[/]\n")
