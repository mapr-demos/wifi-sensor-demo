import machine
import time
import sys
import network

WIFINETWORK = 'woojers'
WIFIPASSWD = 'calamatos'

class SW40(object):
    def __init__(self, pin):
        self.pin = pin
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=self.callback)
        self.count = 0

    def callback(self , pin):
        self.count += 1

def wifi_setup():
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    return (nic)

def wifi_connect(nic):
    nic.connect(WIFINETWORK, WIFIPASSWD)

def wifi_is_connected(nic):
    return nic.isconnected()

def main():
    sensor = SW40(machine.Pin(14, machine.Pin.IN))
    ledpin = machine.Pin(2, machine.Pin.OUT)
    nic = wifi_setup()
    try:
        while True:
            while (wifi_is_connected(nic) == False):
                print("connecting to wifi...")
                wifi_connect(nic)
                time.sleep(1)

            #print("count %d" % sensor.count)
            perhalfsec = ((sensor.count + 10) / 10)
            sleepamt = int(500 / perhalfsec)
            sensor.count = 0
            #print("sleep amt is %d, persec %d" % (sleepamt, persec))
            for i in range(0, perhalfsec):
                time.sleep_ms(sleepamt)
                ledpin.low()
                time.sleep_ms(sleepamt)
                ledpin.high()

    except KeyboardInterrupt:
        print("exiting...")
        sys.exit(0)
if __name__ == '__main__':
    main()
