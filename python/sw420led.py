import machine
import time
import sys

class SW40(object):
    def __init__(self, pin):
        self.pin = pin
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=self.callback)
        self.count = 0

    def callback(self , pin):
        self.count += 1

def main():
    sensor = SW40(machine.Pin(14, machine.Pin.IN))
    ledpin = machine.Pin(2, machine.Pin.OUT)
    try:
        while True:
            #print("count %d" % sensor.count)
            persec = ((sensor.count + 10) / 10)
            sleepamt = int(1000 / persec)
            sensor.count = 0
            #print("sleep amt is %d, persec %d" % (sleepamt, persec))
            for i in range(0, persec):
                time.sleep_ms(sleepamt)
                ledpin.low()
                time.sleep_ms(sleepamt)
                ledpin.high()

    except KeyboardInterrupt:
        print("exiting...")
        sys.exit(0)
if __name__ == '__main__':
    main()
