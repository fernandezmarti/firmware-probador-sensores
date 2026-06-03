from enum import Enum, auto
from hardware import Compressor
from test_runner import run_test
from I2C_smbus2_flow_reader import init_flowmeter
from Serial_flow_reader import calibrate, detect_sensor
from metrics import rmse, mae


class State(Enum):
    IDLE = auto()
    INIT=auto()
    CALIBRATION = auto()
    WAITING_4_SENSOR= auto()
    READY_TO_START= auto()
    MEASUREMENT = auto()
    FINISH=auto()
    ERROR = auto()

class Controller:
    def __init__(self, status_led, compressor, button):
        self.state = State.INIT
        self.status_led = status_led
        self.compressor = compressor
        self.button=button

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


    def _init(self):

        init_flowmeter()
        #init compresores, soplan y medir con sensirion pos y negativo
        #init puerto serie 
        self.set_state(State.CALIBRATION)

    def _calibration(self):

        self.status_led.calibration()
        calibrate() # despues de 5 intentos
        self.set_state=(State.WAITING_4_SENSOR)

    def _waiting_4_sensor(self):
        self.status_led.waiting4sensor()
        self.compressor.idle()
        if detect_sensor():
            self.set_state(State.READY_TO_START)

    def _ready_to_start(self):
        self.status_led.redyToStart()
        if not detect_sensor():
            self.set_state(State.WAITING_4_SENSOR)
        elif self.button.is_pressed:
            self.set_state(State.TEST)
       
    def _test(self):
        self.status_led.measuring()
        self.rmse, self.mae= run_test(self.compressor.positive_fan, self.compressor.negative_fan)
        self.set_state(State.FINISH)

    def _finish(self):
        if self.rmse <3 and self.mae<3:
            self.status_led.testOk()
        else:
            self.status_led.testFail()
        if not detect_sensor():
            self.set_state(State.WAITING_4_SENSOR)
    
    def set_state(self, new_state):
        print(f"{self.state.name} -> {new_state.name}")
        self.state = new_state