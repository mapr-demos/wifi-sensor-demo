import machine
import time
import sys
import network
import ubinascii
import socket

WIFINETWORK = 'maprdemo'
WIFIPASSWD = 'maprdemo'
POST_IP = '192.168.12.1'
POST_PORT = 8082

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

def http_post(host, port, data):
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes(data, 'utf8'))
    s.close()

def main():
    sensor = SW40(machine.Pin(14, machine.Pin.IN))
    ledpin = machine.Pin(2, machine.Pin.OUT)
    macaddr = ubinascii.hexlify(network.WLAN().config('mac'),'-').decode()
    print("my macaddr: %s" % macaddr)
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
            data = "{\"records\":[{\"value\": {\"mac\" :" "\"" + \
                macaddr + "\"" ", " "\"amplitude\" :" + str(sensor.count) + "}  }]}"
            dlen = len(data)
            msg = "/topics/%2Fapps%2Fiot-stream%3Asensor-json HTTP/1.1\r\n" \
                    "User-Agent: curl/7.38.0\r\n" \
                    "Host: localhost:8082\r\n" \
                    "Accept: */*\r\n" \
                    "Content-Type: application/vnd.kafka.json.v1+json\r\n" \
                    "Content-Length: " + str(dlen) + "\r\n\r\n" + str(data)
            #print("sleep amt is %d, persec %d" % (sleepamt, persec))
            print("posting %s" % msg)
            http_post(POST_IP, POST_PORT, msg)
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
