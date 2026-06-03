from gpiozero import PWMOutputDevice, Button, PWMLED, LED

POSITIVE_FAN_PWM_PIN = 12
NEGATIVE_FAN_PWM_PIN = 13

positive_fan = PWMOutputDevice(
    POSITIVE_FAN_PWM_PIN,
    frequency=1000
)

negative_fan = PWMOutputDevice(
    NEGATIVE_FAN_PWM_PIN,
    frequency=1000
)

button = Button(
    pin=27,
    pull_up=True,
    bounce_time=0.1
)

ledR=PWMLED(24)
ledG=PWMLED(23)
ledB=PWMLED(18)

class ledRGB():
    def __init__(self, redpin=24, greenpin=23, bluepin=18):
        self.red=PWMLED(redpin)
        self.green=PWMLED(greenpin)
        self.blue=PWMLED(bluepin)
    
    def off(self):
        self.red.off()
        self.green.off()
        self.blue.off()