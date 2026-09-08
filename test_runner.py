from TSI import tsi_acquisition_task
from I2C_smbus2_flow_reader import i2c_task
from Serial_flow_reader import serial_task
from file_manager import save_csv
import time
import metrics
import numpy as np
import threading
import queue

import matplotlib.pyplot as plt


def run_test(positive_fan, negative_fan,tsi,folder=None,name=None, steps=14, csv=True, init=False, contrast=False):
    sensirion_data = []
    flux_data = []
    tsi_data = []
    tsi_queue = queue.Queue()

    stop_event = threading.Event()

    sensirion_thread = threading.Thread(
        target=i2c_task,
        args=(sensirion_data, stop_event, contrast)
    )

    flux_thread = threading.Thread(
        target=serial_task,
        args=(flux_data, stop_event)
    )


    tsi_thread = threading.Thread(
        target=tsi_acquisition_task,
        args=(tsi, tsi_queue, stop_event)
    )

    positive_fan.off() if positive_fan is not None else None
    negative_fan.off() if negative_fan is not None else None

    time.sleep(1)

    sensirion_thread.start()
    flux_thread.start() if not contrast else tsi_thread.start()

    run_fan_profile(negative_fan, positive_fan, init, steps)

    stop_event.set()

    sensirion_thread.join()
    flux_thread.join() if not contrast else tsi_thread.join()
    
    print(f"sensirion data: {len(sensirion_data)} samples")

    if contrast:
        while not tsi_queue.empty():
            block = tsi_queue.get()
            tsi_data.extend(block)
        print(f"tsi data: {len(tsi_data)} samples")
    else:
        print(f"flux data: {len(flux_data)} samples")


    sensirion_array=np.array(sensirion_data)
    if contrast:
        tsi_array = np.array(tsi_data)
        rmse=metrics.rmse(sensirion_array, tsi_array)
        mae=metrics.mae(sensirion_array, tsi_array)
        save_csv(tsi_data, sensirion_data, mae, rmse, folder=999)
        
    else:
        flux_array=np.array(flux_data)
    if negative_fan is not None and positive_fan is not None and not contrast:
        rmse=metrics.rmse(sensirion_array, flux_array)
        mae=metrics.mae(sensirion_array, flux_array)
        if csv:
            save_csv(flux_data, sensirion_data, mae, rmse, folder)
        return rmse, mae
    else:
        return np.mean(sensirion_data)
        



def run_fan_profile(negative_fan, positive_fan, init, steps):
    
    if init==False:
        Trelax=5
    else:
        Trelax=1

    # if negative_fan is not None:
    #     negative_fan.value= 0.3
    #     for i in range(steps):
    #         negative_fan.value +=0.05
    #         time.sleep(0.15)
    #     negative_fan.off()
    #     time.sleep(5)
    # if positive_fan is not None:
    #     positive_fan.value= 0.3
    #     for i in range(steps):
    #         positive_fan.value +=0.05
    #         time.sleep(0.15)
    #     positive_fan.off()

    if negative_fan is not None:
        negative_fan.value= 1
        time.sleep(1.5)
        negative_fan.off()
        time.sleep(Trelax)
    if positive_fan is not None:
        positive_fan.value= 1 #0.8 y 1.5s va bien
        time.sleep(1.5)
        positive_fan.off()
        time.sleep(Trelax)


def init_fan(positive_fan, negative_fan, steps=7): 
    positive_mean = run_test(positive_fan, None,None,None, steps, csv=False, init=True)
    time.sleep(1)
    negative_mean = run_test(None, negative_fan, steps, csv=False, init=True)

    if positive_mean > 5 and negative_mean < -5:
        return True
    else:
        print(positive_mean, negative_mean)
        return False

