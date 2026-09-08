
from hardware import button, statusLED, Compressor
from state_machine import Controller

status_led=statusLED()
compressor= Compressor()
raspi=Controller(status_led, compressor, button)
def main():
    while True:
        raspi.update()

if __name__ == "__main__":
    main()