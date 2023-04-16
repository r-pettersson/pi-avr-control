##########################
#Author: Roger Pettersson
#Date: 2020-03-15
#Date modified: 2023-04-16
#Adapted for XW5000ES projector
##########################

import paho.mqtt.client as mqtt #import the client1
import time
import serial
import binascii

#valid responses
validResponses = {
					                b'\x02\x07':{
					                        b'\xa8\x82':{   #Video
					                                    b'\x10':'Video 1',
					                                    b'\x11':'Video 2',					                              
					                                    b'\x12':'Video 3'
					                                    },			                        
					                        b'\xa8\x83':{    # Zone 1
					                                    b'\x02\x10':'Video 1',
					                                    b'\x02\x11':'Video 2'					                           
					                                    }
					                       
					                        }
					           
                }

#serial
port = serial.Serial("/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0", baudrate=38400, timeout=0.1)
#port = serial.Serial("/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0", baudrate=9600, timeout=0.1)

#array of commands for the xw5000es
#reply is to be used later as a decoding machanism, reply=number of bytes received as a reply
commands = { "proj_on":{"command":b'\xA9\x17\x2E\x00\x00\x00\x3F\x9A', 
                         "reply":11, 
                         },
               "proj_off":{"command":b'\xA9\x17\x2F\x00\x00\x00\x3F\x9A', 
                         "reply":11, 
                         },                        
              "proj_status":{"command":b'\xA9\x01\x02\x01\x00\x03\x03\x9A', 
                         "reply":11, 
                         },
              "proj_timer":{"command":b'\xA9\x01\x13\x01\x00\x00\x13\x9A',
                         "reply":11,
                         },
             "avr_vol_up":{"command":b'\x02\x06\xA0\x52\x00\x02\x00\x01\x05',
                         "reply":11,
                         },
              "avr_status":{"command":b'\x02\x03\xA0\x82\x00\xDB',
                         "reply":11                        
                         }
                         
              }
        
#              
#A9 01 02 01 00 03 03 9A
#power on \xA9\x17\x2E\x00\x00\x00\x3F\x9A
#off \xA9\x17\x2F\x00\x00\x00\x3F\x9A



#{"POWR OFF", {0xA9, 0x17, 0x2F, 0x00, 0x00, 0x00, 0x3F, 0x9A}},


#lamptimer
#\xA9\x01\x13\x01\x00\x00\x13\x9A


############
def on_message(client, userdata, message):
    bytes_sent = port.write(commands[str(message.payload.decode("utf-8"))]["command"])
    #print commands[str(message.payload.decode("utf-8"))]["command"]
    #print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
########################################
broker_address=""
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("projector") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","projSerialIn")
client.subscribe("projSerialIn")
print("Publishing to topic","projSerialOut")

#bytes_sent = port.write(commands["avr_status"]["command"])

POLL_RATE = 4

while port.isOpen():
        bytesWaiting = port.inWaiting()
        if(bytesWaiting != 0):
            output = port.readline()
            
            output_hex = binascii.hexlify(output)
            
            if output_hex:
                print(bytesWaiting)
                print(output[0:2])
                if output[0:1] == b'\xfd':
                    print("ACK")
                    print(output[0:2])
                    print(output[1:2])
                    print(output[2:3])
                    #print(validResponses[output[1:2]][output[2:4]][b'\x10'])
                
                if output[0:1] == b'\xfe':
                    print("NACK")
                    
                if output[0:2] == b'\x02\x07':
                    print("STATUS")
                    #print(output[0:2])
                    #print(output[2:4])
                    #print(output[5:6])
                    print(output[4:5])
                    print(validResponses[output[0:2]][output[2:4]][output[5:6]])
                
                if output[0:2] == b'\xa9\x01': 
                    print("proj lamp timer");
                    print(int.from_bytes(output[4:6], "big"))
                    
                
                client.publish("projSerialOut",output_hex)
                client.publish("proj_timer", int.from_bytes(output[4:6], "big"))
