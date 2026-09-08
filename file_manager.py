from datetime import datetime
from pathlib import Path
import csv

def obtener_siguiente_csv(folder):
    folder = Path("Conexion larga sin codo")/folder
    folder.mkdir(parents=True, exist_ok=True)

    numeros = []

    for archivo in folder.glob("*.csv"):
        try:
            numeros.append(int(archivo.stem))
        except ValueError:
            # Ignora archivos cuyo nombre no sea un número
            pass

    return folder / f"{max(numeros, default=0) + 1}"


def save_csv(serial_data, i2c_data,mae,rmse,folder=None, name=None):
    
    if folder==0:
        name=obtener_siguiente_csv("Pasan")
        header="SF-A-022"
    elif folder==1:
        name=obtener_siguiente_csv("Fallan")
        header="SF-A-022"

    elif folder==999:
        name=  Path("contrastacion") / datetime.now().strftime("%Y%m%d_%H%M%S")
        header="TSI"

    with open(f'{name}.csv', "w", newline="") as f:

        writer = csv.writer(f, delimiter=';')

        writer.writerow([
            header,
            "Sensirion",
            "RMSE",
            "MAE"
        ])

        for v_serial, v_i2c in zip(serial_data, i2c_data):

            writer.writerow([
                v_serial,
                v_i2c,
                rmse,
                mae
            ])
        