##########################
#Author: Roger Pettersson
#Date: 2020-03-15
#Date modified: 2023-04-16
#Adapted for XW5000ES projector
# calculate checksum for response
# check why bytes gets ascii coded like 21=!
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
#port = serial.Serial("/dev/ttyUSB1", baudrate=9600, timeout=0.1)
port = serial.Serial("/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0", baudrate=9600, timeout=0.1)


#array of commands for the strda5800es
#reply is to be used later as a decoding machanism, reply=number of bytes received as a reply
commands = { "avr_on":{"command":b'\x02\x04\xa0\x60\x00\x01\xfb', 
                         "reply":11, 
                         },
             "avr_off":{"command":b'\x02\x04\xA0\x60\x00\x00\xFC',
                         "reply":11,
                         },
             "avr_vol_up":{"command":b'\x02\x06\xA0\x52\x00\x02\x00\x01\x05',
                         "reply":11,
                         },
              "avr_vol_down":{"command":b'\x02\x06\xA0\x52\x00\x02\xFF\xFF\x08',
                         "reply":11,
                         },
              "avr_vol_status":{"command":b'\x02\x04\xA0\x92\x00\x01\xC9',
                         "reply":11,
                         },
              "avr_vol_set":{"command":b'\x02\x06\xa0\x52\x00\x02\x00\x01\x05',
                         "reply":11,
                         },                             
              "avr_status":{"command":b'\x02\x03\xA0\x82\x00\xDB',
                         "reply":11                        
                         }                         
              }
              
 

#Signed
def int_to_bytes(number: int) -> bytes:
    return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)

#unsigned    
def int_to_bytes_unsigned(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def vol(vol):
  #print(vol)
  if(vol % 1 != 0):
   vol = vol+.5
   print(vol)
   lowbit_new = b'80'
  else :
   lowbit_new = b'00'
  
  vol = int(vol)

  stx = b'02'
  bc = b'06'
  pdc = b'A0'
  cmd = b'52'
  zone = b'00'
  bc = b'06'
  attribute = b'01'
  highbit = b'00'
  
  lowbit = b'00'  
  lowbit = lowbit_new

  cs_sum = (vol+(int(cmd,16))+(int(pdc,16))+(int(bc,16))+(int(zone,16))+(int(attribute,16))+(int(lowbit,16)))
  

  #modulo 256
  cs = (256-cs_sum)%256
  
  #convert checksum to bytes
  csh = int_to_bytes_unsigned(cs);
   
  stx = b'\x02'
  bc = b'\x06'
  pdc = b'\xA0'
  cmd = b'\x52'
  zone = b'\x00'
  bc = b'\x06'
  attribute = b'\x01'
  highbit = b'\x00'
  lowbit = b'\x00'  
  highbit = int_to_bytes(vol)
  lowbit = b'\x00'
  
  lowbit = binascii.unhexlify(lowbit_new)
 
  
  b = (binascii.hexlify(stx)+binascii.hexlify(bc)+binascii.hexlify(pdc)+binascii.hexlify(cmd)+binascii.hexlify(zone)+binascii.hexlify(attribute)+binascii.hexlify(highbit)+binascii.hexlify(lowbit)+binascii.hexlify(csh))
  
  return binascii.unhexlify(b)
 

############
def on_message(client, userdata, message):
    print("hej")
    #print(commands[str(message.payload.decode("utf-8"))]["command"])
    
    
    if (message.topic == "avrVolume"):
        print("Volume to be set: " + message.payload.decode("utf-8"))
        print(vol(float(message.payload.decode("utf-8"))))
        bytes_sent = port.write(vol(float(message.payload.decode("utf-8"))))
    else :
        print("hit")
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
client = mqtt.Client("avr") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","avrSerialIn")
client.subscribe("avrSerialIn")
client.subscribe("avrVolume")
print("Publishing to topic","avrSerialOut")




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
                print(output_hex)
                print(output)
                
                if output[0:1] == b'\xfe':
                    print("NACK")
                
                if output[0:1] == b'\xfd' or output[0:2] == b'\x02\x07':
                    print("ACK")
                    print(output[0:2])
                    print(output[1:2])
                    print(output[2:3])
                    #print(validResponses[output[1:2]][output[2:4]][b'\x10'])
                    
                    if output_hex[16:18] == b'21':
                       print("On")
                       client.publish("avrSerialOut","On")
                    elif output_hex[16:18] == b'20':
                       print("Off")
                       client.publish("avrSerialOut","Off")
                
                
                    
                if output[0:2] == b'\x02\x07':
                    print("STATUS")
                    #print(output)
                    #print(output[0:2])
                    #print(output[2:4])
                    #print(output[5:6])
                    print(output_hex[14:16])
                    #print(validResponses[output[0:2]][output[2:4]][output[5:6]])
                    if output_hex[14:16] == b'21':
                       print("On")
                       client.publish("avrSerialOut","On")
                    elif output_hex[14:16] == b'20':
                       print("Off")
                       client.publish("avrSerialOut","Off")
                print(output[1:3])       
                if (output[0:1] == b'\xfd' and output[1:3] == b'\x02\x06') or output[0:2] == b'\x02\x06':
                    print("VOL")
                    print(output)
                    #print(output[0:2])
                    #print(output[2:4])
                    #print(output[5:6])
                    #print(output_hex[14:16])
                    #print(validResponses[output[0:2]][output[2:4]][output[5:6]])
                    if output[0:1] == b'\xfd':
                       print(output[7:8])
                       int_val = 256-int.from_bytes(output[7:8], "little")
                       if output[8:9] == b'\x80':
                         print("nej")
                         int_val = (256-int.from_bytes(output[7:8], "little"))+.5
            
                       # printing int object
                       print(float(int_val))
                       
                       #todo implement volstatus
                       client.publish("avrVolumeStatus",-(int_val))
                    elif output[0:2] == b'\x02\x06':
                       print("remote controlled")
                       print(output[6:7])
                       int_val = (256-int.from_bytes(output[6:7], "little"))
                       
                       if output[7:8] == b'\x80':
                         print("nej2")
                         int_val = int_val-.5
                       
                       #todo implement vol status
                       print(float(int_val))
                       client.publish("avrVolumeStatus",-(int_val))
                       
                      
                                
                client.publish("avrSerialOut",output_hex)








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
