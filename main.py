#from queue import Queue, Empty
import threading
import time
import csv
from I2C_smbus2_flow_reader import i2c_task, init_flowmeter
from Serial_flow_reader import serial_task, calibrate,detect_sensor
from test_runner import run_test, save_csv
from hardware import positive_fan, negative_fan, button, ledB, ledG, ledR


def main():

    init_flowmeter()
    ledG.pulse()
    ledR.pulse()
    ledB.pulse()
    calibrate()
    ledG.off()
    ledR.off()
    ledB.off()
    positive_fan.value = 0.25

    while True:
        ledG.blink()
        ledR.blink()
        while not detect_sensor():
           pass 
        ledG.off()
        ledR.off()  
        ledB.pulse()  
        button.wait_for_press()
        ledB.off()
        rmse, mae= run_test(positive_fan, negative_fan)
        positive_fan.value = 0.25


        if rmse< 4 and mae<4:
            sensor_pasa=True
        else:
            sensor_pasa=False
        
        print(f'RMSE: {rmse}\nMAE:{mae}')
        while detect_sensor():
            if sensor_pasa:
                ledG.on()
            else:
                ledR.on()   
        ledR.off()
        ledG.off()  

if __name__ == "__main__":
    main()