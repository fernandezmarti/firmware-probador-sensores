from gpiozero import PWMOutputDevice, Button, PWMLED, LED
import time
from enum import Enum, auto


POSITIVE_FAN_PWM_PIN = 12
NEGATIVE_FAN_PWM_PIN = 13

button = Button(
    pin=27,
    pull_up=True,
    bounce_time=0.1
)
button.hold_time = 1


class LedState(Enum):
    PULSE_ON = auto()
    PULSE_OFF = auto()
    PAUSE = auto()


class statusLED():
    def __init__(self, r=24, g=23, b=18):
        self.red=PWMLED(r)
        self.green=PWMLED(g)
        self.blue=PWMLED(b)
       
        self.state = LedState.PAUSE
        self.last_change = time.monotonic()

        self.n_pulses = 0
        self.pulse_counter = 0

        self.interval = 0.25      
        self.pause_time = 1.0     
    
    def off(self):
        self.red.off()
        self.green.off()
        self.blue.off()
    
    def init(self):
        pass
    
    def calibration(self):
        self.off()
        self.green.pulse()
        self.red.pulse()
        self.blue.pulse()

    def waiting4sensor(self):
        self.off()
        self.red.blink()
        self.green.blink()

    def redyToStart(self):
        self.off()
        self.blue.pulse()

    def measuring(self):
        self.off()
        self.blue.pulse()
        self.green.pulse()
    
    def testOk(self):
        self.off()
        self.green.on()

    def testFail(self):
        self.off()
        self.red.on()
    
    def error(self, n_pulses):

        # Solo reiniciar si cambió el patrón
        if self.n_pulses != n_pulses:
            self.n_pulses = n_pulses
            self.pulse_counter = 0
            self.state = LedState.PULSE_ON
            self.last_change = time.monotonic()

        now = time.monotonic()

        match self.state:

            case LedState.PULSE_ON:

                self.red.on()

                if now - self.last_change >= self.interval:
                    self.last_change = now
                    self.state = LedState.PULSE_OFF

            case LedState.PULSE_OFF:

                self.red.off()

                if now - self.last_change >= self.interval:
                    self.last_change = now

                    self.pulse_counter += 1

                    if self.pulse_counter >= self.n_pulses:
                        self.state = LedState.PAUSE
                    else:
                        self.state = LedState.PULSE_ON

            case LedState.PAUSE:

                self.red.off()

                if now - self.last_change >= self.pause_time:
                    self.last_change = now
                    self.pulse_counter = 0
                    self.state = LedState.PULSE_ON



class Compressor():
    def __init__(self):
        self.positive_fan =  PWMOutputDevice(
        POSITIVE_FAN_PWM_PIN,
        frequency=1000
        )

        self.negative_fan = PWMOutputDevice(
        NEGATIVE_FAN_PWM_PIN,
        frequency=1000
        )

    def idle(self):
        self.positive_fan.off()
        self.negative_fan.value=0.3







    