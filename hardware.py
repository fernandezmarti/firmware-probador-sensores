from gpiozero import PWMOutputDevice, Button, PWMLED, LED
import time
POSITIVE_FAN_PWM_PIN = 12
NEGATIVE_FAN_PWM_PIN = 13


PATTERN_1 = [
    (1, 0.25),
    (0, 1.00),
]

PATTERN_2 = [
    (1, 0.25),
    (0, 0.25),
    (1, 0.25),
    (0, 1.00),
]

PATTERN_3 = [
    (1, 0.25),
    (0, 0.25),
    (1, 0.25),
    (0, 0.25),
    (1, 0.25),
    (0, 1.00),
]

button = Button(
    pin=27,
    pull_up=True,
    bounce_time=0.1
)
button.hold_time = 3

class statusLED():
    def __init__(self, r=24, g=23, b=18):
        self.red=PWMLED(r)
        self.green=PWMLED(g)
        self.blue=PWMLED(b)
    
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
    
    def I2C_error(self):
        self.off()
        for state, duration in PATTERN_3:
            if state:
                self.red.on()
            else:
                self.red.off()

            time.sleep(duration)

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
        self.negative_fan.off()
        self.positive_fan.value=0.3

