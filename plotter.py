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


def plot_N_tests(fig, folder,integrar_err_abs=False,err_abs=False,dif_vs_t=False, ddt=False,dif=False,param=False,vol=False, min=1,flux=False, sensirion=False, max=None, all=None, show=True, color='red'):
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

        error= flow_serial - flow_i2c
        error_abs= np.abs(error)
        integral_error_abs=  np.concatenate(([0], np.cumsum((error_abs[:-1] + error_abs[1:]) /(2*256))))

        alpha=0.3
        if flux==True:
            plt.plot(flow_serial, color=color,label=num, alpha=alpha)
        if sensirion==True:
            plt.plot(flow_i2c, color='blue', alpha=alpha)
        if param==True:
            plt.plot(flow_serial, flow_i2c, color='blue', alpha=alpha)
        if dif==True:
            plt.plot(flow_i2c, flow_serial - flow_i2c, color=color, alpha=alpha)
        if dif_vs_t==True:
            plt.plot(flow_serial - flow_i2c, color=color, alpha=alpha)

        if vol==True:
            plt.plot(vol_flux , color=color, alpha=alpha)
            plt.plot(vol_sensirion , color='blue', alpha=alpha)

        if err_abs==True:
            plt.plot(error_abs, color=color, alpha=alpha)

        if integrar_err_abs==True:
            plt.plot(integral_error_abs, color=color, alpha=alpha)

        if ddt==True:
            plt.plot(derivada_flux, color= color, alpha=alpha)
            plt.plot(derivada_sensirion, color= 'blue', alpha=alpha)



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
#plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/prueba 1 nueva matriz", sensirion=True,flux=True,all=True,color='red', show=False)
plot_N_tests(fig,"Conexion larga sin codo/Validacion adaptador TPE/CON ADAPTADOR", sensirion=True,flux=True,all=True, color='green',show=False)
#plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20", sensirion=True,flux=True,all=True, color='brown',show=False)
#plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/sensor procesado de mas", sensirion=True,flux=True,all=True, color='yellow',show=False)
plot_N_tests(fig,"Conexion larga sin codo/Validacion adaptador TPE/SIN ADAPTADOR", sensirion=True,flux=True,all=True, color='red',show=False)
plt.grid(True)
plt.show()
"""
fig= plt.figure()
plt.title("dif vs flow")
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/prueba 1 nueva matriz",dif=True,all=True,color='red', show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/29",dif=True,all=True, color='green',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20",dif=True,all=True, color='brown',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/sensor procesado de mas",dif=True,all=True, color='yellow',show=False)
plt.grid(True)

fig= plt.figure()
plt.title("dif vs samples")
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/prueba 1 nueva matriz",dif_vs_t=True,all=True,color='red', show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/29",dif_vs_t=True,all=True, color='green',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20",dif_vs_t=True,all=True, color='brown',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/sensor procesado de mas",dif_vs_t=True,all=True, color='yellow',show=False)

deltaP = [-80170, -72895, -64970, -58774, -51975, -45659, -39656, -34647, -28734, -24702, -20183, -16764, -12908, -9966, -7243, -5007, -4056, -3120, -2437, -1786, -1250, -797, -437, -395, -327, -273, -237, -195, -166, -122, -97, -68, -51, -33, -17, -8, -3, 0, 2, 7, 22, 38, 58, 77, 100, 119, 145, 190, 246, 306, 361, 425, 485, 900, 1460, 2153, 3019, 4166, 5208, 6569, 10040, 13215, 17237, 21031, 25382, 30356, 36208, 43102, 49103, 56099, 63261, 71358, 81000, 89000, 98686, 102941, 111580, 123723, 123724, 123725, 123726, 123727, 123728, 123729, 123730, 123731, 123732, 123733, 123734, 123735, 123736, 123737, 123738, 123739, 123740, 123741, 123742, 123743, 123744, 123745, 123746, 123747, 123748, 123749, 123750, 123751, 123752, 123753, 123754, 123755, 123756, 123757, 123758, 123759, 123760, 123761, 123762, 123763, 123764, 123765, 123766, 123767, 123768, 123769, 123770, 123771, 123772, 123773, 123774, 123775, 123776, 123777, 123778, 123779, 123780, 123781, 123782, 123783, 123784, 123785, 123786, 123787, 123788, 123789, 123790, 123791, 123792, 123793, 123794, 123795, 123796, 123797, 123798, 123799, 123800, 123801, 123802, 123803, 123804, 123805, 123806, 123807, 123808, 123809, 123810, 123811, 123812, 123813, 123814, 123815, 123816, 123817, 123818, 123819, 123820, 123821, 123822, 123823, 123824, 123825, 123826, 123827, 123828, 123829, 123830, 123831, 123832, 123833, 123834, 123835, 123836, 123837, 123838, 123839, 123840, 123841, 123842, 123843, 123844, 123845, 123846, 123847, 123848, 123849, 123850, 123851, 123852, 123853, 123854, 123855, 123856, 123857, 123858, 123859, 123860, 123861, 123862, 123863, 123864, 123865, 123866, 123867, 123868, 123869, 123870, 123871, 123872, 123873, 123874, 123875, 123876, 123877, 123878, 123879, 123880, 123881, 123882, 123883, 123884, 123885, 123886, 123887, 123888, 123889, 123890, 123891, 123892, 123893, 123894, 123895, 123896, 123897, 123898, 123899, 123900, 123901]
flow = np.array([-3200, -3040, -2880, -2720, -2560, -2400, -2240, -2080, -1920, -1760, -1600, -1440, -1280, -1120, -960, -800, -720, -640, -560, -480, -400, -320, -240, -224, -208, -192, -176, -160, -144, -128, -112, -96, -80, -64, -48, 0, 0, 0, 0, 0, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 320, 400, 480, 560, 640, 720, 800, 960, 1120, 1280, 1440, 1600, 1760, 1920, 2080, 2240, 2400, 2560, 2720, 2880, 3040, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200, 3200])/16
#plt.scatter(deltaP, flow)
plt.grid(True)

fig= plt.figure()
plt.title("Abs error vs samples")
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/prueba 1 nueva matriz",err_abs=True,all=True,color='red', show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/29",err_abs=True,all=True, color='green',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20",err_abs=True,all=True, color='brown',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/sensor procesado de mas",err_abs=True,all=True, color='yellow',show=False)
plt.grid(True)

fig= plt.figure()
plt.title("integral Abs error vs samples")
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/prueba 1 nueva matriz",integrar_err_abs=True,all=True,color='red', show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/29",integrar_err_abs=True,all=True, color='green',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/F20",integrar_err_abs=True,all=True, color='brown',show=False)
plot_N_tests(fig,"AAV1_T_a_SS_a_A22MM_SF_C/sensor procesado de mas",integrar_err_abs=True,all=True, color='yellow',show=False)
plt.grid(True)


plt.show()

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

