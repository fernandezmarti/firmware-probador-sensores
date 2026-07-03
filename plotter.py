import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot(folder, num):

    df = pd.read_csv(
        f'{folder}/{str(num)}.csv',
        sep=';'
    )


    flow_serial = df["SF-A-022"]
    flow_i2c = df["Sensirion"]
    rmse=df['RMSE'].iloc[0]
    mae=df['MAE'].iloc[0]


    plt.title(f'Sensirion - flux N{num}: MAE = {mae:.2f} - RMSE = {rmse:.2f}')
    plt.plot(flow_serial, label='flux')
    plt.plot(flow_i2c, label='sensirion')
    plt.grid(True)
    plt.legend()
    plt.show()


def plot_N_tests(folder, min=1,flux=False, sensirion=False, max=None, all=None):
    if all:
        max = sum(1 for f in Path(folder).iterdir() if f.is_file())

    for num in range(min,max+1):
        if num==18:
            continue
        df = pd.read_csv(
            f'{folder}/{str(num)}.csv',
            sep=';'
        )

        if flux==True:
            flow_serial = df["SF-A-022"]
            plt.plot(flow_serial, label=num)
        if sensirion==True:
            flow_i2c = df["Sensirion"]
            plt.plot(flow_i2c, label=num)
            
    #flow_i2c = df["Sensirion"]
    #plt.plot(flow_i2c, label=num)

    plt.grid(True)
    plt.legend()
    plt.show()

plot_N_tests("Fallan", sensirion=True,flux=True,all=True)