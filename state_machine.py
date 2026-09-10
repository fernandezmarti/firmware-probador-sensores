from enum import Enum, auto
from test_runner import run_test, init_fan
from I2C_smbus2_flow_reader import init_flowmeter
from Serial_flow_reader import calibrate, detect_sensor
from serial.serialutil import SerialException
import time
from TSI import TSIDevice

class ErrorCode(Enum):
    I2C = auto()
    SERIAL = auto()
    FAN = auto()

class State(Enum):
    IDLE = auto()
    INIT=auto()
    CALIBRATION = auto()
    WAITING_4_SENSOR= auto()
    READY_TO_START= auto()
    TEST = auto()
    FINISH=auto()
    ERROR = auto()
    CONTRAST = auto()

class Controller:
    def __init__(self, status_led, compressor, button):
        self.state = State.INIT
        self.status_led = status_led
        self.compressor = compressor
        self.button=button
        self.error=None

        self.tsi=TSIDevice(
            port="/dev/ttyUSB1",
            series=4000,
            block_size=500,
        )

    def update(self):
        match self.state:
            case State.INIT:
                self._init()

            case State.CALIBRATION:
                self._calibration()

            case State.WAITING_4_SENSOR:
                self._waiting_4_sensor()

            case State.READY_TO_START:
                self._ready_to_start()

            case State.TEST:
                self._test()
            
            case State.FINISH:
                self._finish()

            case State.ERROR:
                self._error()

            case State.CONTRAST:
                self._contrast()


    def _init(self):

        try:
            if self.tsi.open():
                self.tsi.set_sample_period(4) #250Hz
                self.status_led.contrast()
                self.set_state(State.CONTRAST)
                return
    

            detect_sensor()
            
            
            init_flowmeter()


        except SerialException as er:
            print(f'Error al abrir el puerto serie: {er}')
            self.error= ErrorCode.SERIAL
            self.set_state(State.ERROR)
            return

        except OSError as er:
            print(f"Error de flujimetro: {er}")
            self.error=ErrorCode.I2C
            self.set_state(State.ERROR)
            return
        
        if not init_fan(self.compressor.positive_fan, self.compressor.negative_fan):
            self.error=ErrorCode.FAN
            self.set_state(State.ERROR)
            return
            
        self.set_state(State.CALIBRATION)
        self.status_led.calibration()

    def _calibration(self):
        
        calibrate() # despues de 5 intentos
        self.set_state(State.WAITING_4_SENSOR)
        self.status_led.waiting4sensor()
    def _contrast(self):
        if self.button.is_pressed:
            run_test(self.compressor.positive_fan, self.compressor.negative_fan, tsi=self.tsi, folder=0, init=False, csv=False, contrast=True)


    def _waiting_4_sensor(self):
        self.compressor.idle()

        if self.button.is_held:
            if self.tsi.ser is not None:
                run_test(self.compressor.positive_fan, self.compressor.negative_fan, tsi=self.tsi, folder=0, init=False, csv=False, contrast=True)
            else:
                print("ERROR en serial TSI")


        if detect_sensor():
            self.set_state(State.READY_TO_START)
            self.status_led.redyToStart()


    def _ready_to_start(self):

        if self.button.is_pressed:
            self.set_state(State.TEST)
            self.status_led.measuring()
            return
        
        elif not detect_sensor(n=64, threshold=3):
            self.set_state(State.WAITING_4_SENSOR)
            self.status_led.waiting4sensor()

        

    def _test(self):
        self.rmse, self.mae= run_test(self.compressor.positive_fan, self.compressor.negative_fan, folder=0, init=False, csv=True)
        self.compressor.idle()
        if self.rmse <3 and self.mae<3:
            self.status_led.testOk()
        else:
            self.status_led.testFail()
        time.sleep(0.2)
        self.set_state(State.FINISH)

    def _finish(self):
        if not detect_sensor(threshold=2,n=64):
            self.status_led.waiting4sensor()
            self.set_state(State.WAITING_4_SENSOR)
        
    def _error(self):
        match self.error:
            case ErrorCode.I2C:
                self.status_led.error(2)

            case ErrorCode.SERIAL:
                self.status_led.error(3)

            case ErrorCode.FAN:
                self.status_led.error(4)
        if self.button.is_held:
            self.status_led.off()
            self.set_state(State.INIT)
            time.sleep(1)
    
    def set_state(self, new_state):
        print(f"{self.state.name} -> {new_state.name}")
        self.state = new_state

    