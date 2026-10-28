
from hardware import statusLED, Compressor
from state_machine import Controller
from gpiozero import Button

button = Button(
    pin=25,
    pull_up=True,
    bounce_time=0.1,
    hold_time = 1)   

status_led=statusLED()
compressor= Compressor()
raspi=Controller(status_led, compressor, button)
def main():
    while True:
        raspi.update()

if __name__ == "__main__":
    main()