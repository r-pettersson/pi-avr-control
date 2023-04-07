##########################
#Author: Roger Pettersson
#Date: 2020-03-15
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
port = serial.Serial("/dev/ttyUSB1", baudrate=38400, timeout=0.1)

#array of commands for the strda5800es
#reply is to be used later as a decoding machanism, reply=number of bytes received as a reply
commands = { "proj_status":{"command":b'\xA9\x01\x02\x01\x00\x03\x03\x9A', 
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
              
              
#A9 01 02 01 00 03 03 9A
#lamptimer
#\xA9\x01\x13\x01\x00\x00\x13\x9A


############
def on_message(client, userdata, message):
    print("hej")
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








 # result = output
                    # startCode=bytes(output[0:2])
                    # print(startCode)
                    # PdcCmd = bytes(result[2:4])
                    # print(PdcCmd)
                    # Data = bytes(result[4:6])
                    # print(Data)   
                    # itemAck = bytes(result[1:3])
                    # #replyType = bytes([result[3]])
                    # rcvData = bytes(result[4:6])
                    # #checksum = bytes([result[6]])
                    # #endCode= bytes([result[7]])
                    # #print(validResponses[startCode][PdcCmd][Data])
                    # print(validResponses[b'\x02\x07'][b'\xa8\x82'][b'\x10'])



   # out = ''
    #while port.inWaiting() > 0:
     #    print("reading")
      #   out += port.read(1)
    #if out == '':
     # print("2")
     # continue
    # time.sleep(POLL_RATE)
    # print(out)  
    # client.publish("avrSerialOut","hej")
    
    # time.sleep(POLL_RATE)
   #   
   #print "port closed"
   #ser.close()
