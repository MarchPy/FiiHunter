import os
import json
import requests
import numpy as np
import pandas as pd
import requests_cache
from io import StringIO
from datetime import datetime
from rich.console import Console


class FundsExplorer:
    def __init__(self) -> None:
        self.__console = Console()
        self.__header = {
            "Host": "fundamentus.com.br",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7"
        }
        self.__settings = self.__open_settings()

    def __open_settings(self):
        try:
            with open(file='config/settings.json', mode='r', encoding='utf-8') as fileObj:
                settings = json.load(fp=fileObj)
                return settings

        except FileNotFoundError:
            self.__console.print(f'[{self.__time()}] -> [[italic red]Arquivo settings.json não foi encontrado.[/]]')

    @staticmethod
    def __time():
        return datetime.now().strftime(format='%H:%M:%S')

    @staticmethod
    def __date():
        return datetime.now().strftime(format='%d-%m-%Y')

    def fundamentus(self) -> pd.DataFrame:
        df_fundamentus = pd.DataFrame()
        symbols = self.__settings['fundos']

        idx = 1
        with requests_cache.enabled('config/cache.db'):
            for symbol in symbols:
                symbol = symbol.upper()
                self.__console.print(f'[{self.__time()}] -> [[italic yellow]Coletando dados fundamentalistas para o ativo[/]]-[{idx} de {len(symbols)}] :: {symbol} -> ', end='')

                url = f"http://fundamentus.com.br/detalhes.php?papel={symbol}"

                try:
                    content = requests.get(url, headers=self.__header)

                    tables_html = pd.read_html(io=StringIO(content.text), decimal=',', thousands='.')
                    df_0 = tables_html[0]
                    df_1 = tables_html[1]
                    df_2 = tables_html[2]
                    df_3 = tables_html[3]
                    df_4 = tables_html[4]

                    df_final = pd.concat(objs=[
                            pd.concat(objs=[pd.concat([df_0[0], df_0[2]]), pd.concat([df_0[1], df_0[3]])], axis=1).T,
                            pd.concat(objs=[pd.concat([df_1[0], df_1[2]]), pd.concat([df_1[1], df_1[3]])], axis=1).T,
                            pd.concat(objs=[pd.concat([df_2[2], df_2[4]]), pd.concat([df_2[3], df_2[5]])], axis=1).T.drop(columns=0),
                            pd.concat(objs=[pd.concat([df_3[0], df_3[2]]), pd.concat([df_3[1], df_3[3]])], axis=1).T.drop(columns=0),
                            pd.concat(objs=[pd.concat([df_4[0], df_4[2], df_4[4]]), pd.concat([df_4[1], df_4[3], df_4[5]])], axis=1).T.drop(columns=0)
                        ], axis=1)

                    df_final.columns = df_final.iloc[0].str.replace(pat='?', repl='')

                    line = df_final[1:]
                    if not line.empty:
                        df_fundamentus = pd.concat([df_fundamentus, line])
                        self.__console.print('[[green]Dados fundamentalistas coletados[/]]')

                except (ValueError, IndexError):
                    self.__console.print('[[red]Não foi possível coletar os dados fundamentalistas[/]]')

                idx += 1
                
        columns_to_drop = [
            np.nan, 'Cart. de Crédito', 'Depósitos', 'Nro. Ações', 'Últ balanço processado', 'Data últ cot', 'Balanço Patrimonial',
            'Últimos 3 meses', 'Balanço Patrimonial', 'Últimos 12 meses', 'Receita', 'FFO', 'Resultado', 'Últ Info Trimestral', 'Relatório',
            'Mandato', 'Gestão', 'Venda de ativos', 'Rend. Distribuído'
        ]
        columns_to_int = [
            'Vol $ méd (2m)', 'Valor de mercado', 'Patrim Líquido', 'Nro. Cotas', 'Ativo', 'Venda de ativos', 
            'Qtd imóveis', 'Qtd Unidades', 'Área (m2)', 'Aluguel/m2', 'Preço do m2'
        ]
        columns_to_float = [
            'Cotação', 'Min 52 sem', 'Max 52 sem', 'P/VP', 'FFO/Cota', 'Dividendo/cota', 'VP/Cota',
            'FFO/Cota'
        ]
        columns_to_format_float = [
            'FFO Yield', 'Vacância Média', 'Cap Rate', 'Imóveis/PL do FII', 'Div. Yield'
        ]

        df_fundamentus = df_fundamentus.replace(to_replace=r'^-$', value='0', regex=True)
        df_fundamentus.fillna(value=0, inplace=True)

        for to_drop in columns_to_drop:
            try:
                df_fundamentus.drop(columns=[to_drop], inplace=True)

            except KeyError:
                pass

        for to_int in columns_to_int:
            try:
                df_fundamentus[to_int] = df_fundamentus[to_int].astype(np.int64)

            except KeyError:
                pass

        for to_float in columns_to_float:
            try:
                df_fundamentus[to_float] = df_fundamentus[to_float].astype(float)

            except KeyError:
                pass

        for to_format_float in columns_to_format_float:
            try:
                df_fundamentus[to_format_float] = df_fundamentus[to_format_float].str.replace(pat='.', repl='').str.replace(pat=',', repl='.').str.replace(pat='%', repl='').astype(float)

            except KeyError:
                pass

        df_fundamentus = df_fundamentus.reset_index(drop=True)
        return df_fundamentus

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        filter_ = (
            (dataframe['Div. Yield'] >= self.__settings['filtro']['Dividend yield (Min)']) &
            (dataframe['Vol $ méd (2m)'] >= self.__settings['filtro']['Volume médio 2m (Min)']) &
            (dataframe['Qtd imóveis'] >= self.__settings['filtro']['Quantidade de imóveis (Min)']) &
            (dataframe['P/VP'] <= self.__settings['filtro']['P/VP (Max)']) &
            (dataframe['P/VP'] >= self.__settings['filtro']['P/VP (Min)']) &
            (dataframe['VP/Cota'] > dataframe['Cotação'] if self.__settings['filtro']['VP/Cota > Preço cota'] else None) &
            (dataframe['Vacância Média'] <= self.__settings['filtro']['Vacância média (Max)'])
        )

        return dataframe[filter_]

    def save_file(self, dataframe: pd.DataFrame) -> None:
        folder = self.__settings['pasta']
        try:
            os.mkdir(path=folder)

        except FileExistsError:
            pass

        filename = f"Resultado dos fundos imobiliários ({self.__date()}).xlsx"
        dataframe.to_excel(excel_writer=os.path.join(folder, filename), index=False)
        self.__console.print(f'\n\n[[bold yellow]Resultado salvo em excel[/]] -> ({os.path.join(folder, filename)})')

    def display_result(self, dataframe: pd.DataFrame) -> None:
        print(dataframe.columns)
        self.__console.print(f'\n\n[{self.__time()}] -> [[italic bold green]Resultado final resumido:[/]]')
        self.__console.print(dataframe[['FII', 'Nome', 'Segmento', 'Cotação', 'Div. Yield', 'P/VP', 'VP/Cota', 'Dividendo/cota', 'Qtd imóveis', 'Qtd Unidades', 'Vacância Média']].to_string(index=False) + "\n" if not dataframe.empty else "[bold red]Nenhuma oportunidade encontrada[/]\n")
