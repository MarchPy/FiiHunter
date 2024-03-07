from sys import argv
from FundExplorer import FundExplorer


def main():
    app = FundExplorer()
    df_fundamentus = app.fundamentus()
    df_filtered = app.filter(dataframe=df_fundamentus)
    app.display_result(dataframe=df_filtered)
    if "-s" in argv:
        app.save_file(dataframe=df_filtered)


main()
