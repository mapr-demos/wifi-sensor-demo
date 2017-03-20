require('config')
local pulse1 = 0
local connected = 0
local connout = nil
local entries = {}

function sendit(sock)
	if #entries > 0 then
		print("Sending...")
		connout:send(table.remove(entries, 1))
	else
		print("Nothing to send...")
	end
end


function postit(amplitude)
        if connected == 0 then
            print("not connected yet")
            return
        end
        data = "{\"records\":[{\"value\": {\"mac\" :" .. "\"" .. wifi.sta.getmac() .. "\"" .. ", " .. "\"amplitude\" :" .. amplitude .. "}  }]}"
        dlen = string.len(data) 
        msg = "POST /topics/%2Fapps%2Fiot-stream%3Asensor-json HTTP/1.1\r\n" 
                 .. "User-Agent: curl/7.38.0\r\n"
                 .. "Host: localhost:8082\r\n"
                 .. "Accept: */*\r\n"
                 .. "Content-Type: application/vnd.kafka.json.v1+json\r\n"
                 .. "Content-Length: " .. dlen .. "\r\n\r\n"
                 .. data
	oldsz = #entries
	entries[#entries + 1] = msg
        print("posting 1 message to queue")
	if oldsz == 0 then
		sendit(conn)
		connout:on("sent", sendit)
	end
	collectgarbage()
end


local function pulsein(level)
    local pulse2 = tmr.now()
    amplitude = pulse2 - pulse1
    print(level, amplitude)
    postit(amplitude)
    pulse1 = pulse2
    gpio.trig(DATA_PIN, level == gpio.HIGH  and "down" or "up")
end

print ("creating Connection...")
connout = net.createConnection(net.TCP, 0)
 
connout:on("connection", function(connout, payloadout)
        print ("Connected...")
        connected = 1
end)
 
connout:on("disconnection", function(connout, payloadout)
        connout:close()
        collectgarbage()
        connout = nil
        connected = 0
        node.restart()
end)
print ("initiating connection to host...")
connout:connect(PROXY_PORT, PROXY_IP)

gpio.mode(DATA_PIN, gpio.INT)
gpio.trig(DATA_PIN, "down", pulsein)
