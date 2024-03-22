import os
import json
import requests
import pandas as pd
import requests_cache
from datetime import datetime
from bs4 import BeautifulSoup
from rich.console import Console



class FiiHunter:
    def __init__(self) -> None:
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

    def __openSettings(self) -> dict:
        try:
            with open(file='config/settings.json', mode='r', encoding='utf-8') as fileObj:
                settings = json.load(fp=fileObj)
                return settings

        except FileNotFoundError:
            self._console.print(f'[{self.__time()}] -> [[italic red]Settings file not found.[/]]')

    @staticmethod
    def __time() -> str:
        return datetime.now().strftime(format='%H:%M:%S')

    @staticmethod
    def __date() -> str:
        return datetime.now().strftime(format='%d-%m-%Y')

    def fundamentus(self) -> pd.DataFrame:
        data = []
        dataNotFound = []
        symbols = self.__settings['fundos']

        idx = 1
        with requests_cache.enabled('config/cache.db'):
            for symbol in symbols:
                symbol = symbol.upper()
                self._console.print(f'[{self.__time()}] -> [[italic yellow]Collecting fundamental data for ticker[/]]-[{idx} of {len(symbols)}] :: {symbol} -> ', end='')

                url = f"http://fundamentus.com.br/detalhes.php?papel={symbol}"
                content = requests.get(url=url, headers=self.__headers)

                if content.status_code == 200:
                    soup = BeautifulSoup(content.content, 'html.parser')

                    if soup.find(string='Nenhum papel encontrado') is None:
                        tables = soup.find(name='div', attrs={'class': 'conteudo clearfix'})
                        tables = soup.find_all(name='table', attrs={'class': 'w728'})

                        # --- Proper way to identify the values ---

                        # numTable = 2
                        # print("\n\n")
                        # print(f'Contains -{len(tables)}- tables.')
                        # i = 0
                        # for index, row in zip(tables[numTable].find_all(name='td', attrs={'class': 'label'}), tables[numTable].find_all(name='td', attrs={'class': 'data'})):
                        #     print(i, index)
                        #     print(i, row)
                        #     print('\n')
                        #     i += 1
                        # input("\n\n")

                        # ----------------------------------------------------

                        # Tabela 0
                        ativo = tables[0].find_all(name='td', attrs={'class': 'data'})[0].text
                        preco = float(tables[0].find_all(name='td', attrs={'class': 'data'})[1].text.replace('.', '').replace(',', '.'))
                        nome = tables[0].find_all(name='td', attrs={'class': 'data'})[2].text
                        precoMinimo52Sem = float(tables[0].find_all(name='td', attrs={'class': 'data'})[5].text.replace('.', '').replace(',', '.'))
                        segmento = tables[0].find_all(name='td', attrs={'class': 'data'})[6].text
                        precoMaximo52Sem = float(tables[0].find_all(name='td', attrs={'class': 'data'})[7].text.replace('.', '').replace(',', '.'))
                        volumeMedio2m = int(tables[0].find_all(name='td', attrs={'class': 'data'})[9].text.replace('.', ''))

                        # Tabela 1
                        nTotalCotas = tables[1].find_all(name='td', attrs={'class': 'data'})[1].text
                        relatorio = tables[1].find_all(name='td', attrs={'class': 'data'})[2].find(name='a')
                        relatorio = relatorio['href'] if relatorio is not None else "-"

                        # Tabela 2
                        dividendYield = tables[2].find_all(name='td', attrs={'class': 'data'})[4].text
                        dividendYield = float(dividendYield.replace('%', '').replace('.', '').replace(',', '.')) if dividendYield != '-' else 0
                        pvp = float(tables[2].find_all(name='td', attrs={'class': 'data'})[7].text.replace(',', '.'))
                        vpCota = tables[2].find_all(name='td', attrs={'class': 'data'})[8].text
                        vpCota = float(vpCota.replace('.', '').replace(',', '.')) if vpCota != '-' else 0
                        dividendoCota = tables[2].find_all(name='td', attrs={'class': 'data'})[5].text
                        dividendoCota = float(dividendoCota.replace('.', '').replace(',', '.')) if dividendoCota != '-' else 0
                        ffoCota = tables[2].find_all(name='td', attrs={'class': 'data'})[5].text
                        ffoCota = float(ffoCota.replace('.', '').replace(',', '.')) if ffoCota != '-' else 0
                        ffoYield = tables[2].find_all(name='td', attrs={'class': 'data'})[1].text
                        ffoYield = float(ffoYield.replace('%', '').replace('.', '').replace(',', '.')) if ffoYield != '-' else 0
                        ativos = int(tables[2].find_all(name='td', attrs={'class': 'data'})[25].text.replace('.', ''))
                        patrimLiq = int(tables[2].find_all(name='td', attrs={'class': 'data'})[26].text.replace('.', ''))

                        # Tabela 4
                        qtdImoveis = int(tables[4].find_all(name='td', attrs={'class', 'data'})[0].text)
                        qtdUnidades = tables[4].find_all(name='td', attrs={'class', 'data'})[3].text
                        qtdUnidades = int(qtdUnidades) if qtdUnidades != '' else 0
                        areaM2 = tables[4].find_all(name='td', attrs={'class', 'data'})[1].text
                        capRate = tables[4].find_all(name='td', attrs={'class', 'data'})[2].text
                        vacMedia = tables[4].find_all(name='td', attrs={'class', 'data'})[5].text
                        vacMedia = float(vacMedia.replace('%', '').replace(',', '.')) if vacMedia != '-' else 0
                        precoM2 = tables[4].find_all(name='td', attrs={'class', 'data'})[7].text

                        data.append(
                            [
                                ativo, segmento, nome, preco, precoMinimo52Sem, precoMaximo52Sem, volumeMedio2m, ativos, patrimLiq, nTotalCotas, dividendYield,
                                dividendoCota, pvp, vpCota, ffoCota, ffoYield, qtdImoveis, qtdUnidades, areaM2, capRate, vacMedia, precoM2,
                                relatorio
                            ]
                        )


                        self._console.print('[[bold green]Data collected successfully[/]]')

                    else:
                        self._console.print('[[bold red]Data not found[/]]')
                        dataNotFound.append(symbol)

                else:
                    self._console.print(f"Error code: {content.status_code}")
                    continue

                idx += 1

        os.system(command='cls' if os.name == 'nt' else 'clear')
        if dataNotFound:
            self._console.print(f'\n[[bold yellow]Unable to collect data from {len(dataNotFound)} ticker(s)[/]] -> {dataNotFound}')
            with open(f'Tickers without data ({self.__date()}).txt', 'w') as fileObj:
                fileObj.write(str(dataNotFound))

        columns = [
            'Ativo', 'Segmento', 'Nome', 'Cotação', 'Preço 52sem (Min)', 'Preço 52sem (Max)', 'Vol $ méd (2m)', 'Ativos',
            'Patrim. Líquido', 'N° total de cotas', 'Div. Yield', 'Dividendo/cota', 'P/VP', 'VP/Cota', 'FFO/Cota', 'FFO Yield',
            'Qtd. Imóveis', 'Qtd. Unidades', 'Área (m2)', 'Cap Rate', 'Vacância média', 'Preço do m2', 'Relatório'
        ]
        dfFundamentus = pd.DataFrame(data=data, columns=columns)
        return dfFundamentus

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        filter_ = (
            (dataframe['Div. Yield'] >= self.__settings['filtro']['Dividend yield (Min)']) &
            (dataframe['Vol $ méd (2m)'] > self.__settings['filtro']['Volume médio 2m (Min)']) &
            (dataframe['Qtd. Imóveis'] >= self.__settings['filtro']['Quantidade de imóveis (Min)']) &
            (dataframe['P/VP'] < self.__settings['filtro']['P/VP (Max)']) &
            (dataframe['P/VP'] > self.__settings['filtro']['P/VP (Min)']) &
            (dataframe['VP/Cota'] > dataframe['Cotação'] if self.__settings['filtro']['VP/Cota > Preço cota'] else None) &
            (dataframe['Vacância média'] < self.__settings['filtro']['Vacância média (Max)'])
        )

        return dataframe[filter_]

    def save_file(self, dataframe: pd.DataFrame) -> None:
        folder = self.__settings['pasta']
        try:
            os.mkdir(path=folder)

        except FileExistsError:
            pass

        filename = f"FII Results ({self.__date()}).xlsx"
        dataframe.to_excel(excel_writer=os.path.join(folder, filename), index=False)
        self._console.print(f'[[bold yellow]Result saved to excel[/]] -> ({os.path.join(folder, filename)})')

    def ranking(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe.copy()
        dataframe['Ranking'] = 0
        for column in self.__settings['ranking']:
            if self.__settings['ranking'][column] == "Max":
                index = dataframe[(dataframe[column] == dataframe[column].max())].index.values
                dataframe.loc[index[0], 'Ranking'] += 1 if len(index) == 1 else 0

            elif self.__settings['ranking'][column] == "Min":
                index = dataframe[(dataframe[column] == dataframe[column].min())].index.values
                dataframe.loc[index[0], 'Ranking'] += 1 if len(index) == 1 else 0

        return dataframe.sort_values(by='Ranking', ascending=False)

    def displayResult(self, dataframe: pd.DataFrame) -> None:
        self._console.print(f'\n\n[{self.__time()}] -> [[italic bold green]Resultado final resumido[/]]:')
        self._console.print(dataframe[['Ativo', 'Nome', 'Segmento', 'Cotação', 'Div. Yield', 'P/VP', 'VP/Cota', 'Dividendo/cota', 'Qtd. Imóveis', 'Qtd. Unidades', 'Vacância média', 'Ranking']].to_string(index=False) + "\n" if not dataframe.empty else "[bold red]Nenhuma oportunidade encontrada[/]\n")
