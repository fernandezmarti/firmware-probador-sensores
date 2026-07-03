import threading
from I2C_smbus2_flow_reader import i2c_task
from Serial_flow_reader import serial_task
from file_manager import save_csv
import time
import metrics
import numpy as np



def run_test(positive_fan, negative_fan,folder=None,name=None, steps=14, csv=True, init=False):
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
    positive_fan.off() if positive_fan is not None else None
    negative_fan.off() if negative_fan is not None else None

    time.sleep(1)

    i2c_thread.start()
    serial_thread.start()

    run_fan_profile(negative_fan, positive_fan, init, steps)

    stop_event.set()

    i2c_thread.join()
    serial_thread.join()
    print(len(i2c_data), len(serial_data))

    i2c_array=np.array(i2c_data)
    serial_array=np.array(serial_data)
    if negative_fan is not None and positive_fan is not None:
        rmse=metrics.rmse(i2c_array, serial_array)
        mae=metrics.mae(i2c_array, serial_array)
        if csv:
            save_csv(serial_data, i2c_data, mae, rmse, folder)
        return rmse, mae
    else:
        return np.mean(i2c_data)
        



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

