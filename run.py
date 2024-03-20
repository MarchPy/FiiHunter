from sys import argv
from FiiHunter  import FiiHunter 


def main():
    app = FiiHunter()
    df_fundamentus = app.fundamentus()
    df_filtered = app.filter(dataframe=df_fundamentus)
    df_ranking = app.ranking(dataframe=df_filtered)
    app.display_result(dataframe=df_ranking)
    if "-s" in argv:
        app.save_file(dataframe=df_ranking)

    app._console.input('[bold yellow]Precione qualquer tecla para encerrar o programa. [/]')
    

main()
