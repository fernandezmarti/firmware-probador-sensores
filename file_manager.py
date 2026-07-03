from pathlib import Path
import csv

def obtener_siguiente_csv(carpeta):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    numeros = []

    for archivo in carpeta.glob("*.csv"):
        try:
            numeros.append(int(archivo.stem))
        except ValueError:
            # Ignora archivos cuyo nombre no sea un número
            pass

    return carpeta / f"{max(numeros, default=0) + 1}"


def save_csv(serial_data, i2c_data,mae,rmse,folder=None, name=None):
    
    if folder==0:
        name=obtener_siguiente_csv("Pasan")
    elif folder==1:
        name=obtener_siguiente_csv("Fallan")

    with open(f'{name}.csv', "w", newline="") as f:

        writer = csv.writer(f, delimiter=';')

        writer.writerow([
            "SF-A-022",
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
        