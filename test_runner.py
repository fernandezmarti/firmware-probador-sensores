import threading
from I2C_smbus2_flow_reader import i2c_task
from Serial_flow_reader import serial_task
import time
import csv
from gpiozero import PWMOutputDevice
import metrics
import numpy as np


def run_test(positive_fan, negative_fan, steps=14, csv=True):
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

    run_fan_profile(negative_fan, positive_fan, steps)

    stop_event.set()

    i2c_thread.join()
    serial_thread.join()

    if csv:
        save_csv(serial_data, i2c_data)
    i2c_array=np.array(i2c_data)
    serial_array=np.array(serial_data)
    rmse=metrics.rmse(i2c_array, serial_array)
    mae=metrics.mae(i2c_array, serial_array)

    return rmse, mae, np.mean(i2c_data)



def run_fan_profile(negative_fan, positive_fan, steps):
    positive_fan.off() if positive_fan is not None else None

    if negative_fan is not None:
        negative_fan.value= 1
        for i in range(steps):
            negative_fan.value -=0.05
            time.sleep(0.15)
        negative_fan.off()
    if positive_fan is not None:
        positive_fan.value= 0.4
        for i in range(steps):
            positive_fan.value +=0.05
            time.sleep(0.15)
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

def init_fan(positive_fan, negative_fan, steps=7): 
    _,_,positive_mean = run_test(positive_fan, None, steps, csv=False)
    time.sleep(0.5)
    _,_,negative_mean = run_test(None, negative_fan, steps, csv=False)

    if positive_mean > 10 and negative_mean < -10:
        return True
    else:
        return False
