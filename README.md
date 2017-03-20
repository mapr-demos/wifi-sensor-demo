
# MapR Demo Application with ESP8266-based Sensors

This is an example application showing an data pipeline with IoT-enabled
devices sending data to MapR Streams over WiFi.  To make for a visual
display, the demo allows for up to 10 ESP8266 devices to be connected
simultaneously. The incoming data from an attached SW-420 vibration
sensor will be displayed on a live dashboard with instantaneous updates.

The dashboard shows live sensor data on the left, and the right side
shows the current [t-digest](https://github.com/tdunning/t-digest)
0.5 percentile value is displayed for all connected sensors.

## Quickstart

Getting the end-to-end demo running requires these steps, which will be
covered in detail here:
* Build the sensor with the hardware list in the next section
* Flash the ESP8266 device with nodemcu
* Connect to the ESP8266 over USB and load the lua script into it
* On the cluster side, ensuring the MapR streams proxy is running on one of your MapR nodes
* Configuring the stream
* Building and starting the streaming web application
* Watch your new streaming application in action! :)

### Prerequisites

You will need the following components to get this demo running in its entirety:
* At least one node running MapR
* At least one sensor as described in the next section
* A wifi network
* Java Development Kit 8
* Maven 3.3 or later
* A client machine with a web browser to access the dashboard

### Building the Sensor

The sensor consists of the following parts:

* ESP8266 ESP-12E WiFi module (datasheet [here](https://mintbox.in/media/esp-12e.pdf), available
on Amazon [here](https://www.amazon.com/Alloet-NodeMcu-ESP8266-ESP-12E-Development/dp/B01MEGE60L))
* SW-420 vibration sensor 
(specs [here](https://www.elecrow.com/vibration-sensor-module-sw420-p-525.html),
available on Amazon [here](https://www.amazon.com/Solu-SW-420-Motion-Vibration-Arduino/dp/B00YZXB9VW))
* Breadboard or soldering skills
* Power supply, for 
example [a 3x 1.5V AAA battery holder](https://www.amazon.com/gp/product/B01K9KYNNA)

The sensor can then be assembled by making the following connections from the 3 pins of the SW-420 module to the ESP8266:

* Connect GND of the SW-420 to GND on the ESP8266
* Connect Vcc of the SW-420 to Vcc on the ESP8266
* Connect DO of the SW-420 to D5 of the ESP8266

If you use a small breadboard and the exact parts above, the pins on the
SW-420 line up against this particular ESP-12E module nicely, as shown
below, eliminating the need for additional wires.

### Updating Nodemcu on the Sensor

The ESP-12E module seems to be inconsistently loaded at the factory.  Some of the modules I've recieved have software already on them, some don't.  The easiest
way to ensure that you have the correct software is to load the flash yourself.

Download the [nodemcu-flasher](https://github.com/nodemcu/nodemcu-flasher) tool for your platform (for Windows users, there are Windows binaries in win64/Release and win32/Release).

Connect the device with the onboard micro-USB port and run EESP8266Flasher.

After this step you should be able to see the device boot normally, using your serial communication software of choice.  The default baud rate is 9600.
Here are a few examples for how to connect over serial:

* In linux, use 'screen':  

```
screen /dev/ttyUSB0 9600
```

* In Windows, use [PuTTY](http://www.putty.org/) and [follow the instructions](https://the.earth.li/~sgtatham/putty/0.68/htmldoc/Chapter3.html#using-serial) 
for connecting to a serial port.  Use the Device Manager to see what port the device is using; it is probably something like COM5.

Upon opening the serial port you will see the message:
 ```
 init.lua not found.
```
This is normal because we haven't loaded anything onto the board yet.

### Loading the Lua Files

First, edit the file lua/config.lua and configure it to match your
environment.  At a minimum you will need to edit the WiFi network and
password, and the endpoint IP of the cluster node you will be using to
receive the streaming data).

I highly recommend the [luatool](https://github.com/4refr0nt/luatool)
utility as an easy method for loading lua files onto the ESP8266.
When ready to load, disconnect any existing serial session first (this
is important) and load the files from this repo (in the lua/ directory)
as follows:

```
sudo ./luatool.py --port /dev/ttyUSB0 --src lua/main.lua --dest main.lua --baud 9600
sudo ./luatool.py --port /dev/ttyUSB0 --src lua/init.lua --dest init.lua --baud 9600
sudo ./luatool.py --port /dev/ttyUSB0 --src lua/config.lua --dest config.lua --baud 9600
```

Now reset the module, either by reconnecting to serial and typing
```
node.restart()
```
or by pressing the rest button on the board. 

Reconnect to the serial console.  You should now see messages indicating it is connecting to a WiFi network.

### Configuring MapR to Receive the Sensor Data

This section assumes that you have a MapR cluster running, if not, [get one now for free](http://mapr.com/download).

On one of your cluster nodes, ensure that the Kafka-REST API gateway
(which can communicate with either Kafka or MapR Streams) is running.
Consult the following pages:

(http://maprdocs.mapr.com/home/Kafka/kafkaREST.html)

To install the package on a node, run:

```
sudo apt-get install mapr-kafka-rest
```

Now create the stream and topic to which we'll be producing the sensor data:

```
$ maprcli stream create -path /apps/iot_stream -produceperm p -consumeperm p -topicperm p
$ maprcli stream topic create -path /apps/iot_stream -topic sensor-json
```

In our case we want to the dashboard as responsive as possible.  To do so we need to reduce buffering of messages.  This can be done
by adding a configuration entry in the kafka-rest configuration file:

```
sudo echo 'streams.buffer.max.time.ms=10' >> /opt/mapr/kafka-rest/kafka-rest-20.0.1/config/kafka-rest.properties
sudo service mapr-warden restart
```

### Customizing, Building and Running the Application

The application uses the MAC address of the sensors to determine a time-series data set
and corresponding chart color for that sensor.

The MAC address will be printed on boot of the device (via the serial console) after you've
loaded the above Lua code.  Once you have the address(es) of up to 10 sensors, edit the following file:

```
src/main/resources/webroot/index.html
```

starting at this line of code:

```
      switch (entry.mac) {
```

change the addresses shown there to match yours.

Next, build the application.

```
mvn clean package
```

Now run the application (assuming you are using the
```
mapr
```
 user:

```
java -jar ./target/mapr-streams-vertx-dashboard-1.0-SNAPSHOT-fat.jar web 9090 /apps/iot-stream:sensor-json
```

This creates a web server on port 9090 and listens to the topic we configured in the previous step.

Turn on your sensor and (optionally) verify that it's connected to the wifi network.

You should now be able to connect to this host in any browser via the address http://host:9090 and view the 
dashboard and corresponding statistic.  It should look like the below screenshot.

![dashboard image](https://github.com/mapr-demos/wifi-sensor-demo/raw/master/src/common/images/dashboard.PNG "dashboard")

## Credits

The web application heavily borrows code from the following sources:
* Tug G.'s,
[mapr-streams-vertx-dashboard](https://github.com/namato/mapr-streams-vertx-dashboard) example.
* [sw420-mqtt](https://github.com/Wifsimster/sw420-mqtt) for talking to the SW-420 board in Lua.
* [tdigest](https://github.com/welch/tdigest) for the Javascript implementation of Ted Dunning's T-Digest algorithm.
