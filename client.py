#Authors: Dimitri van Well
#Date Last Modified: 11/15/2022
#Program Status: Running

from socket import *
import socket
#while True:
HOST = 'localhost' 
PORT = 8889 # Arbitrary non-privileged port

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((HOST, PORT))
while True:
      inputFromKeyboard = input('Enter command: ') # get command from user
      clientSocket.send(inputFromKeyboard.encode()) # send command to server
      if (inputFromKeyboard =='exit'): # If input from user is 'exit', close connection
            break
      print ('waiting for response from server...')
      receivedMessage = clientSocket.recv(1024) #Get reply from server
      print ('server response received: ')
      print (receivedMessage.decode()) # Print the reply on the screen    

clientSocket.close()
