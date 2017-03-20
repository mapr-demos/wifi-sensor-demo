-- set this to the WiFi network and password
AP = "maprdemo"
PWD = "mapr999!"

-- set this to the IP of the node running the MapR streams proxy
PROXY_IP = "192.168.1.212"
PROXY_PORT = 8082
CLIENT_ID = "ESP8266-"..node.chipid()
REFRESH_RATE = 3000 -- ms

-- which GPIO pin to use, these are numbered a little funkily
DATA_PIN = 5 -- GPIO_5
