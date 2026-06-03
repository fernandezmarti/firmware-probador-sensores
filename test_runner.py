import threading
from I2C_smbus2_flow_reader import i2c_task
from Serial_flow_reader import serial_task
import time
import csv
from gpiozero import PWMOutputDevice
import metrics
import numpy as np


def run_test(positive_fan, negative_fan):
    i2c_data = []
    serial_data = []

    stop_event = threading.Event()

    i2c_thread = threading.Thread(
        target=i2c_task,
        args=(i2c_data, stop_event)
    )

    serial_thread = threading.Thread(
        target=serial_task,
        args=(serial_data, stop_event)
    )


    i2c_thread.start()
    serial_thread.start()

    run_fan_profile(negative_fan, positive_fan)

    stop_event.set()

    i2c_thread.join()
    serial_thread.join()

    print(len(i2c_data))
    print(len(serial_data))

    save_csv(serial_data, i2c_data)
    i2c_array=np.array(i2c_data)
    serial_array=np.array(serial_data)
    rmse=metrics.rmse(i2c_array, serial_array)
    mae=metrics.mae(i2c_array, serial_array)

    return rmse, mae



def run_fan_profile(negative_fan, positive_fan):
    positive_fan.off()
    negative_fan.value= 0.8
    for i in range(8):
        negative_fan.value -=0.05
        time.sleep(0.2)
    negative_fan.off()

    positive_fan.value= 0.4
    for i in range(8):
        positive_fan.value +=0.05
        time.sleep(0.2)
    positive_fan.off()



def save_csv(serial_data, i2c_data):
    with open("test.csv", "w", newline="") as f:

        writer = csv.writer(f, delimiter=';')

        writer.writerow([
            "Serial",
            "I2C"
        ])

        for v_serial, v_i2c in zip(serial_data, i2c_data):

            writer.writerow([
                v_serial,
                v_i2c
            ])