from gpiozero import PWMOutputDevice
import time


POSITIVE_FAN_PWM_PIN = 18
NEGATIVE_FAN_PWM_PIN = 13

positive_fan = PWMOutputDevice(POSITIVE_FAN_PWM_PIN, frequency=1000)
while True:
    positive_fan.value = 0.8
    for i in range(8):
        positive_fan.value -= 0.05
        time.sleep(0.5)

    for i in range(8):
        positive_fan.value += 0.05
        time.sleep(0.5)


positive_fan.off()