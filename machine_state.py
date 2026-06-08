from enum import Enum, auto
from test_runner import run_test
from I2C_smbus2_flow_reader import init_flowmeter
from Serial_flow_reader import calibrate, detect_sensor

class State(Enum):
    IDLE = auto()
    INIT=auto()
    CALIBRATION = auto()
    WAITING_4_SENSOR= auto()
    READY_TO_START= auto()
    TEST = auto()
    FINISH=auto()
    ERROR = auto()

class Controller:
    def __init__(self, status_led, compressor, button):
        self.state = State.INIT
        self.status_led = status_led
        self.compressor = compressor
        self.button=button
        self.error=None

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


    def _init(self):

        try:
            init_flowmeter()
            self.set_state(State.CALIBRATION)
            self.status_led.calibration()
        except OSError as er:
            print(f"Error de flujimetro: {er}")
            self.error=er
            self.set_state(State.ERROR)
            

        #init compresores, soplan y medir con sensirion pos y negativo
        #init puerto serie

    def _calibration(self):
        
        calibrate() # despues de 5 intentos
        self.set_state(State.WAITING_4_SENSOR)
        self.status_led.waiting4sensor()

    def _waiting_4_sensor(self):
        self.compressor.idle()
        if detect_sensor():
            self.set_state(State.READY_TO_START)
            self.status_led.redyToStart()


    def _ready_to_start(self):
        if not detect_sensor():
            self.set_state(State.WAITING_4_SENSOR)
            self.status_led.waiting4sensor()

        elif self.button.is_pressed:
            self.set_state(State.TEST)
            self.status_led.measuring()

    def _test(self):
        self.rmse, self.mae= run_test(self.compressor.positive_fan, self.compressor.negative_fan)
        self.compressor.idle()
        if self.rmse <3 and self.mae<3:
            self.status_led.testOk()
        else:
            self.status_led.testFail()
        self.set_state(State.FINISH)

    def _finish(self):
        if not detect_sensor():
            self.status_led.waiting4sensor()
            self.set_state(State.WAITING_4_SENSOR)
        
    def _error(self):
        if self.error==OSError:
            self.status_led.I2C_error()
        if self.button.is_held:
            self.set_state(State.INIT)
    
    def set_state(self, new_state):
        print(f"{self.state.name} -> {new_state.name}")
        self.state = new_state

    