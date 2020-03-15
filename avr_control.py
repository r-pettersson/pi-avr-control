##########################
#Author: Roger Pettersson
#Date: 2020-03-15
##########################

import paho.mqtt.client as mqtt #import the client1
import time
import serial
import binascii

#serial
port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.1)

#array of commands for the strda5800es
#reply is to be used later as a decoding machanism, reply=number of bytes received as a reply
commands = { "avr_on":{"command":"\x02\x04\xa0\x60\x00\x01\xfb", 
                         "reply":11, 
                         },
              "avr_off":{"command":"\x02\x02\xa0\x20\x3e",
                         "reply":11,
                         },
             "avr_vol_up":{"command":"\x02\x06\xA0\x52\x00\x02\x00\x01\x05",
                         "reply":11,
                         },
              "avr_status":{"command":"\x02\x03\xA0\x82\x00\xDB",
                         "reply":11                        
                         }                         
              }
              
              

############
def on_message(client, userdata, message):
    #print "hej"
    bytes_sent = port.write(commands[str(message.payload.decode("utf-8"))]["command"])
    #print commands[str(message.payload.decode("utf-8"))]["command"]
    #print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
########################################
broker_address="192.168.1.87"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","avrSerialIn")
client.subscribe("avrSerialIn")
print("Publishing to topic","avrSerialOut")



bytes_sent = port.write(commands["avr_status"]["command"])

while True:
   #mqtt.receive(avr_command)
   #switch based on "avr_command" received
   #bytes_sent = port.write(avr_command)
   
   #output = port.read(1) #1 byte at a time
   output = port.readline()
   output_hex = binascii.hexlify(output)
   
   # Publish message to MQTT Topic
   if output != "":
    print(binascii.hexlify(output))
    print(output_hex.find("0207"))
    client.publish("avrSerialOut",binascii.hexlify(output))
    #client.publish(serialoutput, binascii.hexlify(output))
    print("Publishing message to topic", binascii.hexlify(output))
    #client.publish("house/bulbs/bulb1","OFF")

#time.sleep(4) # wait
client.loop_stop() #stop the loop