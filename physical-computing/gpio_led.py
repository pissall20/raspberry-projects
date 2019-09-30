from gpiozero import LED
from time import sleep
import sys

# Long leg of LED on GP17 pin, and short leg on GND pin
led = LED(17)

def blink(secs=1):
    while True:
        led.on()
        sleep(secs)
        led.off()
        sleep(secs)

if __name__ == "__main__":
    try:
        if len(sys.argv) > 2:
            raise ValueError
        if len(sys.argv) == 2:
            secs = float(sys.argv[1])
            blink(secs)
        else:
            blink()
    except KeyboardInterrupt:
        print("Exiting program")
