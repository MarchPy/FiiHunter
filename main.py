from sys import argv
from FundsExplorer import FundsExplorer


def main():
    app = FundsExplorer()
    df_fundamentus = app.fundamentus()
    df_filtered = app.filter(dataframe=df_fundamentus)
    df_ranking = app.ranking(dataframe=df_filtered)
    app.display_result(dataframe=df_ranking)
    if "-s" in argv:
        app.save_file(dataframe=df_filtered)


main()
