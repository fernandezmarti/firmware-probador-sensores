import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np


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


def plot_N_tests(fig, folder,ddt=False,dif=False,param=False,vol=False, min=1,flux=False, sensirion=False, max=None, all=None, show=True, color='red'):
    if all:
        max = sum(1 for f in Path(folder).iterdir() if f.is_file())

    for num in range(min,max+1):

        if (num==2 or num==6) and folder=='Pasan':
            continue
        if num==18 and folder=='Fallan':
            continue
        df = pd.read_csv(
            f'{folder}/{str(num)}.csv',
            sep=';'
        )
        flow_i2c = df["Sensirion"]
        flow_serial = df["SF-A-022"]

        #cero_sens=np.argmin(np.abs(flow_i2c[0:200]))
        #cero_flux=np.argmin(np.abs(flow_serial[0:200]))

        #flow_i2c = flow_i2c [cero_sens:].reset_index(drop=True)
        #flow_serial = flow_serial [cero_flux:].reset_index(drop=True)

        vol_flux = np.concatenate(([0], np.cumsum((flow_serial[:-1] + flow_serial[1:]) /(2*256))))*1000/60
        vol_sensirion = np.concatenate(([0], np.cumsum((flow_i2c[:-1] + flow_i2c[1:])  /(2*256))))*1000/60

        derivada_flux=np.gradient(flow_serial, 1)
        derivada_sensirion=np.gradient(flow_i2c, 1)
        alpha=0.5
        if flux==True:
            plt.plot(flow_serial, color=color,label=num, alpha=alpha)
        if sensirion==True:
            plt.plot(flow_i2c, color='blue', alpha=alpha)
        if param==True:
            plt.plot(flow_serial, flow_i2c, color='blue', alpha=alpha)
        if dif==True:
            plt.plot(flow_i2c, flow_i2c - flow_serial , color='blue', alpha=alpha)
        if vol==True:
            plt.plot(vol_flux , color=color, alpha=alpha)
            plt.plot(vol_sensirion , color='blue', alpha=alpha)
    if ddt==True:
        plt.plot(derivada_flux, color= color, alpha=alpha)
        plt.plot(derivada_sensirion, color= 'blue', alpha=alpha)



            
    #flow_i2c = df["Sensirion"]
    #plt.plot(flow_i2c, label=num)


    plt.grid(True)
    plt.legend()
    plt.show() if show else None


def plot_metrics(ax,folder, color, marker, show=True):
    max = sum(1 for f in Path(folder).iterdir() if f.is_file())
    for num in range(1,max):
        if (num==2 or num==6) and folder=='Pasan':
            continue
        if num==18 and folder=='Fallan':
            continue

        df = pd.read_csv(
        f'{folder}/{str(num)}.csv',
        sep=';'
        )
        rmse=df['RMSE'].iloc[0]
        mae=df['MAE'].iloc[0]

        ax[0].scatter(num,rmse, color=color, marker=marker)
        ax[1].scatter(num,mae,  color=color, marker=marker)

    plt.show() if show else None


def boxplot_metrics(ax,folder, position):
    rmse_array= []
    mae_array= []
    max = sum(1 for f in Path(folder).iterdir() if f.is_file())
    for num in range(1,max):
        if (num==2 or num==6) and folder=='Pasan':
            continue
        if num==18 and folder=='Fallan':
            continue

        df = pd.read_csv(
        f'{folder}/{str(num)}.csv',
        sep=';'
        )
        rmse=df['RMSE'].iloc[0]
        mae=df['MAE'].iloc[0]
        rmse_array.append(rmse)
        mae_array.append(mae)
    
    ax[0].boxplot(rmse_array, positions=[position], widths=0.5)
    ax[1].boxplot(mae_array, positions=[position], widths=0.5)

    
fig = plt.figure()
plt.title("Flujo vs tiempo")
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/29", sensirion=True,flux=True,all=True,color='green', show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20", sensirion=True,flux=True,all=True, color='red',show=False)

fig= plt.figure()
plt.title("Vol vs tiempo")
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20", vol=True,all=True, color='red',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/29", vol=True,all=True, color='green',show=False)

plt.show()
"""
fig= plt.figure()
#plot_N_tests(fig,"Fallan", ddt=True,all=True, color='red',show=False)
plot_N_tests(fig,"Conexion larga sin codo/Pasan", ddt=True,all=True, color='green',show=False)

plt.show()

fig, ax= plt.subplots(2,1, sharex=True)
ax[0].set_title("RMSE")
ax[1].set_title("MAE")
boxplot_metrics(ax,"Fallan",0)
boxplot_metrics(ax,"Pasan", 0.75)
ax[1].set_xticklabels(["", "Fallan","","Pasan"])
ax[0].grid()
ax[1].grid()
plt.show()

fig, ax= plt.subplots(2,1)
ax[0].set_title("RMSE")
ax[1].set_title("MAE")
plot_metrics(ax,"Fallan", color= 'red' , marker='x',show=False)
plot_metrics(ax,"Pasan", color='green', marker='o', show=False)
"""

