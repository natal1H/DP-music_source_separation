import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

""" 
    Author:         Natália Holková
    Login:          xholko02
    File:           generate_model_graphs.py
    Description:    Generates graphs from MetaCentrum training document
"""

def setup_matplotlib():
    plt.rcParams['axes.titlesize'] = 'x-large'
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    plt.style.use("seaborn-darkgrid")

def get_df_from_sheet(excel_loc, sheet_name):
    df = pd.read_excel(excel_loc, sheet_name=sheet_name)
    df = df.drop(['xps', 'train log', 'valid log'], axis=1)

    return df


def plot_loss(df, name, save_loc=None):
    plt.clf()

    plt.plot(df["epoch"], df["train loss"], label="Train loss")
    plt.plot(df["epoch"], df["valid loss"], label="Valid loss", color="tab:orange")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title(name)
    plt.legend()

    if save_loc is not None:
        plt.savefig(save_loc)
    else:
        plt.show()


def plot_nsdr(df, name, save_loc=None):
    plt.clf()
    plt.axhline(y=0.0, color='k', linestyle='dotted')

    plt.plot(df["epoch"], df["valid nsdr"], color="tab:orange")
    plt.xlabel("Epoch")
    plt.ylabel("nSDR")
    plt.title(name)

    if save_loc is not None:
        plt.savefig(save_loc)
    else:
        plt.show()

def plot_nsdr_together(dfs, save_loc=None):
    plt.clf()
    plt.axhline(y=0.0, color='k', linestyle='dotted')

    plt.plot(dfs["remix"]["epoch"], dfs["remix"]["valid nsdr"], label="Remix only (12/3)")
    plt.plot(dfs["medley"]["epoch"], dfs["medley"]["valid nsdr"], label="Medley only (12/3)")
    plt.plot(dfs["remixMedley"]["epoch"], dfs["remixMedley"]["valid nsdr"], label="Remix + Medley (12/3)")
    plt.plot(dfs["biggerRemixMedley"]["epoch"], dfs["biggerRemixMedley"]["valid nsdr"], label="Remix + Medley (24/6)")
    plt.plot(dfs["biggestRemixMedley"]["epoch"], dfs["biggestRemixMedley"]["valid nsdr"], label="Remix + Medley (28/6)")

    plt.xlabel("Epoch")
    plt.ylabel("nSDR")
    plt.title("nSDR comparison")
    plt.legend(loc='lower right')

    if save_loc is not None:
        plt.savefig(save_loc)
    else:
        plt.show()


def plot_valid_loss_together(dfs, save_loc=None):
    plt.clf()

    plt.plot(dfs["remix"]["epoch"], dfs["remix"]["valid loss"], label="Remix only (12/3)")
    plt.plot(dfs["medley"]["epoch"], dfs["medley"]["valid loss"], label="Medley only (12/3)")
    plt.plot(dfs["remixMedley"]["epoch"], dfs["remixMedley"]["valid loss"], label="Remix + Medley (12/3)")
    plt.plot(dfs["biggerRemixMedley"]["epoch"], dfs["biggerRemixMedley"]["valid loss"], label="Remix + Medley (24/6)")
    plt.plot(dfs["biggestRemixMedley"]["epoch"], dfs["biggestRemixMedley"]["valid loss"], label="Remix + Medley (28/6)")

    plt.xlabel("Epoch")
    plt.ylabel("Valid loss")
    plt.title("Valid loss comparison")
    plt.legend(loc='upper right')

    if save_loc is not None:
        plt.savefig(save_loc)
    else:
        plt.show()


if __name__ == "__main__":
    setup_matplotlib()
    excel = "../metacentrum_separation_training.xlsx"
    df_remix = get_df_from_sheet(excel, "Remix (12/3)")
    df_medley = get_df_from_sheet(excel, "Medley (12/3)")
    df_remixMedley = get_df_from_sheet(excel, "Remix + Medley (12/3)")
    df_biggerRemixMedley = get_df_from_sheet(excel, "Remix + Medley (24/6)")
    df_biggestRemixMedley = get_df_from_sheet(excel, "Remix + Medley (28/6)")

    # Plots for remix only model
    plot_loss(df_remix, "Remix only model (12 channels, 3 depth)", "remix_loss.svg")
    plot_nsdr(df_remix, "Remix only model (12 channels, 3 depth)", "remix_nsdr.svg")

    # Plots for medley only model
    plot_loss(df_medley, "Medley only model (12 channels, 3 depth)", "medley_loss.svg")
    plot_nsdr(df_medley, "Medley only model (12 channels, 3 depth)", "medley_nsdr.svg")

    # Plots for remix + medley model
    plot_loss(df_remixMedley, "Remix + Medley model (12 channels, 3 depth)", "remixMedley_loss.svg")
    plot_nsdr(df_remixMedley, "Remix + Medley model (12 channels, 3 depth)", "remixMedley_nsdr.svg")

    # Plots for bigger remix + medley model
    plot_loss(df_biggerRemixMedley, "Remix + Medley model (24 channels, 6 depth)", "biggerRemixMedley_loss.svg")
    plot_nsdr(df_biggerRemixMedley, "Remix + Medley model (24 channels, 6 depth)", "biggerRemixMedley_nsdr.svg")

    # Plots for biggest remix + medley model
    plot_loss(df_biggestRemixMedley, "Remix + Medley model (28 channels, 6 depth)", "biggestRemixMedley_loss.svg")
    plot_nsdr(df_biggestRemixMedley, "Remix + Medley model (28 channels, 6 depth)", "biggestRemixMedley_nsdr.svg")

    dfs = {"remix": df_remix, "medley": df_medley, "remixMedley": df_remixMedley,
           "biggerRemixMedley": df_biggerRemixMedley, "biggestRemixMedley": df_biggestRemixMedley}
    plot_nsdr_together(dfs, "nsdr_comparison.svg")
    plot_valid_loss_together(dfs, "valid_loss_comparison.svg")