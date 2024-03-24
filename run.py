from sys import argv
from src.FiiHunter  import FiiHunter 


def main():
    app = FiiHunter()
    df_fundamentus = app.fundamentus()
    df_technical = app.technicalIndicators(dataframe=df_fundamentus)
    df_filtered = app.filter(dataframe=df_technical)
    df_ranking = app.ranking(dataframe=df_filtered)
    app.displayResult(dataframe=df_ranking)
    if "-s" in argv:
        app.save_file(dataframe=df_ranking)

    app._console.input('[bold yellow]Precione qualquer tecla para encerrar o programa. [/]')
    

main()
