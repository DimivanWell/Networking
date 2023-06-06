#Authors: Peter Matti, Dimitri van Well, Audy Saidi
#Date Last Modified: 11/15/2022
#Program Status: Running
#IMPORTANT: Any photo files attempting to be uploaded/inserted has to be in the server and client files directory

from socket import *
import socket
import os
import time

from _thread import*
import threading

connVAL = 1



#nextCustomerID = 0
mutex_lock = threading.Lock()

customerNum = 0

#Threading class: Will act as the multi connection receive and send for the client side
class cliThread(threading.Thread):
        def __init__(self,cliAddr,cliSCKT): #initialize the threading functions
                threading.Thread.__init__(self)
                self.cliSKT = cliSCKT
                print('New Connection made: ', cliAddr) #Display the connected IP and port
        def run(self): #function that will run per client thread.
                while True:
                        message = self.cliSKT.recv(1024)   #server recieves message from client
                        usrCMD = message.decode()
                        parseCMD = ''
                        parseCMD = usrCMD.split(' ') #Parse the client received message
                        parseCMD[0] = parseCMD[0].lower()
                        try:
                                if(not parseCMD[0] == "picdownload"): #removes any spaces that could cause error and fill data space
                                        parseCMD.remove('')
                        except ValueError:
                                        m = 0
                        if(parseCMD[0] == 'showall'):       #command to show entire stored database
                                try:
                                        parseCMD.remove('')
                                except ValueError:
                                        m = 0
                                if (len(parseCMD) > 1): #ERROR: check point, this command only needs a certain amount of command fields
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                msgPass,i = cDB.showAll()
                               
                                if(i>0):
                                        rtrnMSG = ''
                                        for elem in msgPass:
                                                rtrnMSG += (str(elem) + '\n')
                                        self.cliSKT.sendall(rtrnMSG.encode()) #SEND: Server -> Client
                                else:
                                         self.cliSKT.sendall(msgPass.encode()) #SEND: Server -> Client
                        elif(parseCMD[0] == 'show'):        #command to show customer based on ID specified and other datatype will not return
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 2)): #ERROR: check point for specified data fields for this command to succesfully execute
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        custID = int(parseCMD[1])
                                        msgPass = cDB.shows(custID)
                                        self.cliSKT.sendall(msgPass.encode()) #SEND: server -> client
                        elif(parseCMD[0] == "insert"):      #command to insert new customer with *AT MINIMUM* First Name, Last Name, Phone *ADDITIONALLY* Address, picture file
                                n = 0
                                try:
                                        parseCMD.remove('')
                                except ValueError:
                                        m = 0
                                
                                for element in parseCMD:
                                        parseCMD[n]=element.strip(' ') #strips command fields of any white space
                                        n+=1

                                if((len(parseCMD)) <= 3): #ERROR: check point for uneccesary command data fields
                                        errMsg = ('ERROR: Incorrect Data for %s command, make sure there is a First Name, Last Name, and Phone Number'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        global customerNum #This Global will control the tick count for customers being entered into the database
                                        picFile = ['.jpg','.png','.jpeg'] #picture file parse array
                                        hasAddr = 0
                                        hasPic = 0
                                        customerNum += 1
                                        nextCustomerID = customerNum
                                        i = 0
                                        Addr = ''
                                        for element in parseCMD:
                                                if ((picFile[0] in element) or (picFile[1] in element) or (picFile[2] in element)):
                                                        try:
                                                                element = element.strip('')
                                                                element = element.strip(' ')
                                                                open(element, 'r')       #tries to open a filename matching the one speicifed in the user input
                                                        except FileNotFoundError:
                                                                errMSG = 'ERROR: File was not inserted to database, does not exist'     #input validation for invalid filename
                                                                hasPic = 2
                                                                break
                                                        else:
                                                                cDB.insertFILE(element) #function call to pass any found file in command line to the picture data array
                                                                hasPic = 1
                                                if(i==4):
                                                        Addr += (str(element) + ' ')
                                                        hasAddr = 1
                                                else:
                                                        i += 1
                                        if ((hasAddr == 1) or (hasPic == 1)):
                                                customerAddr = Addr
                                                customerAddr,custPic = cDB.picInput(customerAddr) #function call to parse out any customer picture to command line 
                                        else:
                                                customerAddr = "\0"
                                        if(hasPic == 0):
                                                custPic = "\0"  
                                        msgPass = cDB.inserts(nextCustomerID, parseCMD[1], parseCMD[2], parseCMD[3], customerAddr, custPic) #function call for inserting customer to data base
                                        if(hasPic == 2):
                                                msgPass = msgPass + ' ' + errMSG   
                                        self.cliSKT.sendall(msgPass.encode())  #SEND: Server -> Client
                        elif(parseCMD[0] == "remove"):      #command to remove customer from DB based on ID value
                                try:
                                        parseCMD.remove('')
                                except ValueError:
                                        m = 0

                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 2)): #ERROR: Check point for inwanted data fields
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        custID = int(parseCMD[1])
                                        msgPass = cDB.removes(custID)
                                        self.cliSKT.sendall(msgPass.encode()) #SEND: Server -> client
                        elif(parseCMD[0] == "search"):      #command to seach for customer based last name
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 2)): #unwanted data fields error
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        if(type(parseCMD[1]) == int or type(parseCMD[1]) == float): #non customer last name error datatype check
                                                errMSG = 'The value being searched can not be a number'
                                                self.cliSKT.sendall(errMSG.encode())
                                        else:
                                                lastName = parseCMD[1]
                                                msgPass = cDB.searchs(lastName)
                                                self.cliSKT.sendall(msgPass.encode()) #SEND: server -> client
                        elif(parseCMD[0] == "exit"):        #command to exit
                                break
                        elif(parseCMD[0] == "manual"):      #command to pull up a reference manual
                                msgPass = cDB.manual()
                                self.cliSKT.sendall(msgPass.encode())
                        elif(parseCMD[0] == "dbdownload"):  #command to download entire database
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 2)):
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        filName = parseCMD[1]
                                        msgPass = cDB.download(filName) #call for download function to parse data in DB and download onto text file 
                                        self.cliSKT.sendall(msgPass.encode())
                        elif(parseCMD[0] == "dbupload"):    #command to upload a text file that has database customers on it
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 2)):
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        filName = parseCMD[1]
                                        msgPass = cDB.upload(filName) #function call for the upload data parse function
                                        self.cliSKT.sendall(msgPass.encode())
                        elif(parseCMD[0] == "change"):      #command to change a customers information
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 5)):
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        custID = int(parseCMD[1])
                                        msgPass = cDB.change(custID, parseCMD[2], parseCMD[3], parseCMD[4])
                                        self.cliSKT.sendall(msgPass.encode()) 
                        elif(parseCMD[0] == "picupload"):   #command to upload a picture to a customer
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 4)):
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                else:
                                        fName = str(parseCMD[1])
                                        lName = str(parseCMD[2])
                                        file = parseCMD[3]
                                        msgPass = cDB.picUpload(fName,lName, file) #finction call for data parsing to correctly upload to the customer
                                        self.cliSKT.sendall(msgPass.encode())
                        elif(parseCMD[0] == "picdownload"): #command to download a specific picture from the customers DB location
                                if ((not len(parseCMD) > 1) or (len(parseCMD) > 4)):
                                        errMsg = ('ERROR: Incorrect Data for %s command'%parseCMD[0])
                                        self.cliSKT.sendall(errMsg.encode())
                                elif(len(parseCMD) == 3):
                                        file = ('default_filename_%s.jpg'%parseCMD[1]) #if no new file name is found a default new name is set
                                        fName = str(parseCMD[1])
                                        lName = str(parseCMD[2])
                                        newFile = file
                                        msgPass = cDB.picDownloadDisplay(fName,lName,newFile)
                                        self.cliSKT.sendall(msgPass.encode()) 
                                else:
                                        fName = str(parseCMD[1])
                                        lName = str(parseCMD[2])
                                        newFile = parseCMD[3]
                                        msgPass = cDB.picDownloadDisplay(fName,lName,newFile) #function call
                                        self.cliSKT.sendall(msgPass.encode())
                        else:  #NON VALID COMMAND INPUT
                                usrCMD = "ERROR: The operation is not supported!"
                                connectionSocket.sendall(usrCMD.encode())
                

class Node: # Customer Record Class

    def __init__(self,customerID, customerFirstName, customerLastName, customerPhone, customerPicture, customerAddress):  #definition of structure for customer ID
            self.id = customerID
            self.first = customerFirstName
            self.last = customerLastName
            self.phone = customerPhone
            self.pic = customerPicture
            self.addre = customerAddress

    def display(self):  # display record
            return 'Customer record: ' + str(self.id) + ' ; ' + self.first + ' ; ' +    self.last + ' ; ' + self.phone       

    

class customerDB: # Customer Database Class
        def __init__(self):
                self.db = [] #customers data base
                self.picData = [] #picture data base for both file name and the pictures pixel data

        def insertFILE(self,file): #if picture is found during the insert command, this fuction puts the file (if found) in the picture data base
                with open(file,'rb') as dat:
                        fData = dat.read()
                custPicDat = [file,fData]
                self.picData.append(custPicDat)
                dat.close()

        def showAll(self): # display all records
                rtrnARY = []
                i = 0

                for record in self.db:
                        #Command displays all customers by going through each element at each available node and sending it back to the client
                        showallCMD = str(record[0]) + ' ' + str(record[1]) + ' ' + str(record[2]) + ' ' + str(record[3]) + ' ' + str(record[4]) + ' ' + str(record[5]) + '\n'  
                        rtrnARY.append(showallCMD)
                        i +=1       
                
                if (i == 0):
                        errMSG = 'Database is empty!'
                        return errMSG,i
                else:
                        return rtrnARY,i

    #Fill in start                                                              
    # Many lines of code to fill in here for other functions

        def shows(self,customerID):        #defintion of show function
                hasAddr = 0
                custFND = 0
                for element in self.db: #list parsing for specific value based on passed in data to funciton 
                        for val in element:
                                if (customerID == val):
                                        custFND = 1
                                        break
                        if(custFND == 1):
                                break

                if (custFND == 0):           #input validation checks to see if value is higher than actual amount of customers in database at execution time
                        shwERROR = 'No customers have this ID'
                        return shwERROR
                elif(custFND == 1):
                        for list in self.db:        #if given customer ID is valid, then starts displaying all available attributes to customer with specified ID
                                for value in list:
                                        if(customerID == value):
                                                if (len(list) == 5):
                                                        hasAddr = 1
                                                break
                                if(hasAddr == 1):
                                        break
                        if(hasAddr == 1):
                                showCMD = str(list[0]) + ' ' + str(list[1]) + ' ' + str(list[2]) + ' ' + str(list[3]) + ' ' + str(list[4])
                        else:
                                showCMD = str(list[0]) + ' ' + str(list[1]) + ' ' + str(list[2]) + ' ' + str(list[3])                  
                        return showCMD 

        def inserts(self, customerID, customerFirstName, customerLastName, customerPhone, customerAddress, customerPicture):  #definition of insert function
                self.id = customerID        #this section organizes attributes relating to the customer to be inserted
                self.first = str(customerFirstName)
                self.last = str(customerLastName)
                self.phone = customerPhone
                self.addre = customerAddress
                self.pic = customerPicture
                self.dbENTRY = [self.id, self.first, self.last, self.phone, self.addre, self.pic]    #after attributes are categorized, they are inputted into the database

                i = 0
                positiveOUT = 0
                for subList in self.db: 
                        for element in subList: 
                                if (customerFirstName == subList[1] and customerLastName == subList[2]):
                                        positiveOUT = 1
                                        errMSG = 'ERROR: Record already exists'
                                        return errMSG
                                        break
                        i += 1
                if (positiveOUT == 0):
                        self.db.append(self.dbENTRY)
                        posMSG = 'Operation was completed successfully'
                        return posMSG
                
        def removes(self, customerID):     #definition of remove function
                i = 0
                err = 1
                for custom in self.db: 
                        for custoID in custom: 
                                if (customerID == custoID):
                                        err = 0
                                        del(self.db[i])      #simple delete commmand to remove all attributes at given customer id
                                        posMSG = 'Operation was completed successful'
                                        return posMSG
                                        break
                        i += 1
                if (err == 1):       #input validation if invalid customer id was provided for removeal
                        errMSG = 'ERROR: No match was found!'
                        return errMSG
                                        
        def searchs(self, lastName):       #definition for search function
                error = 1
                i = 0
                for customList in self.db: #actual seach algorithm looks for through all entries for a matching last name
                        for custoLAST in customList:
                                str(customList[i])
                                if (lastName == custoLAST):
                                        error = 0
                                        #if it finds it it displays it
                                        searchCMD = str(customList[0]) + ' ' + str(customList[1]) + ' ' + str(customList[2]) + ' ' + str(customList[3]) + '\n' 
                                        return searchCMD
                        i += 1
                if (error == 1):     #input validation if invalid last name was inputted into the search
                        errMSG = 'ERROR: No match was found!'
                        return errMSG

        def manual(self):    #Extra manual function for debugging and feature tracking purposes, left in for it's usefulness to the end user

                manu = (
                        '''
                        Available commands and their inputs: (-syntax | *function)
                        -  showall                                                  *Show full database
                        -  show customerID                                          *Show customer based on ID
                        -  insert customerFirstName customerLastName customerPhone  *Insert new custome, space oriented
                        -  remove customerID                                        *Remove customer based on ID
                        -  search lastName                                          *Search customer bases on Last Name
                        -  dbdownload fileName                                      *Download customer database
                        -  dbupload filename'.txt'                                  *Upload saved datase file
                        -  change custID newFirst newLast newPhone                  *change the information of cust
                        -  exit                                                     *Exit connection
                        -  picupload firstName lastName picFile'.jpg'               *upload pic based on first and last
                        -  picdownload firstName lastName newPicFile'.jpg'          *download pic based on first and last
                        '''
                )
                return manu 

        def download(self, filename):      #definition for download function
                picFile = ['.jpg','.png','.jpeg']
                filename = 'dbDownload_{}.txt'.format(filename)  #sets filename of file to be created
                f = open(filename, 'w')            #opens and creates the file
                for customers in self.db:          #function gathers up all info for all customers in the database
                        for element in customers:
                                element = str(element)
                                if ((picFile[0] in element) or (picFile[1] in element) or (picFile[2] in element)):
                                        fileFND = element.strip('')
                                        fileFND = fileFND.strip(' ')
                                        cDB.dbpicdown(fileFND,customers[1])
                                input = element + ' '
                                f.write(input)       #all attributes of each and every customer is written to the file that was just created
                        f.write('\n')               #new line for each customer
                f.close()                          #file is closed after all data has been added
                size = os.path.getsize(filename)   #gets file size of the file
                posMSG = 'Operation was completed successfully at size ' + str(size) + ' bytes!'    #the filesize is communicated to the client
                return posMSG 
                
        def upload(self, filename):        #defintion for the upload function
                picFile = ['.jpg','.png','.jpeg']
                try:
                        upFile = open(filename, 'r')       #tries to open a filename matching the one speicifed in the user input
                except FileNotFoundError:
                        errMSG = 'ERROR: File does not exist'     #input validation for invalid filename
                        #connectionSocket.sendall(errMSG.encode())
                        return errMSG
                else: 
                        upFile = open(filename, 'r')       #if filename is valid, the file is opened
                        self.db = []
                        for line in upFile:
                                uploadList = line.split()
                                for element in uploadList:
                                        try:
                                                uploadList.remove('')
                                        except ValueError:
                                                m = 0
                                        element = element.strip('')
                                        element = element.strip(' ')
                                #The following for loop will parse through the files lines and differ between pic file and address
                                i = 0
                                lineElements = ''
                                for item in uploadList:
                                        if(i > 3):
                                                lineElements += item + ' '
                                        if ((picFile[0] in item) or (picFile[1] in item) or (picFile[2] in item)):
                                                customerPic = item
                                                lineElements = lineElements.replace(item,'')
                                                customerPic = customerPic.strip('')
                                                customerPic = customerPic.strip(' ')
                                                try:
                                                        open(customerPic, 'r')    #if pic in line is found the file will be stored to pic data array
                                                except FileNotFoundError:
                                                        errMSG = 'ERROR: Picture File not Found upload failed'     
                                                        return errMSG
                                                else: 
                                                        fileName = customerPic
                                                        fileName = str(fileName)
                                                        fileName = fileName.strip()
                                                        with open(fileName,'rb') as dat:
                                                                fData = dat.read()
                                                        custPicDat = [fileName,fData]
                                                        self.picData.append(custPicDat)
                                                        dat.close()
                                        else:
                                                customerPic = ''
                                        i+=1
                                customerID = uploadList[0]
                                customerFirst = uploadList[1]
                                customerLast = uploadList[2]
                                customerPhone = uploadList[3]
                                customerAddre = lineElements
                                
                                self.id = int(customerID)
                                self.first = str(customerFirst)
                                self.last = str(customerLast)
                                self.phone = str(customerPhone)
                                self.addre = str(customerAddre)
                                self.pic = str(customerPic)
                                upDB = [self.id, self.first, self.last, self.phone, self.addre, self.pic]
                                self.db.append(upDB)        #After allocating parsed data to its fields the entire customer element will be set in the DB
                        global customerNum
                        customerNum = int(customerID)
                        upFile.close()
                        size = os.path.getsize(filename)   #file size is gathered, like in the download
                        posMSG = 'Operation was completed successfully at size ' + str(size) + ' bytes!'    #A successful file upload communicates the size of the file uploaded back to the client 
                        return posMSG 

        def change(self, custID, customerFirstName, customerLastName, customerPhone):       #definition for the change fucntion
                self.id = custID     #then the new customer info is put into at the id specified within the change function
                self.first = str(customerFirstName)
                self.last = str(customerLastName)
                self.phone = customerPhone
                self.dbENTRY = [self.id, self.first, self.last, self.phone]       
                
                i = 0
                positiveOUT = 0
                for subList in self.db: 
                        for element in subList: 
                                if (customerFirstName == subList[1] and customerLastName == subList[2]):
                                        positiveOUT = 1
                                        errMSG = 'ERROR: Record already exists'
                                        return errMSG
                                        break
                        i += 1
                i = 0
                if (positiveOUT == 0):
                        for customer in self.db:
                                for element in customer:
                                        if (custID == element):
                                                customer[1] = self.first
                                                customer[2] = self.last
                                                customer[3] = self.phone
                                i += 1

                        posMSG = 'Operation was completed successfully'
                        return posMSG

        def picInput(self, msgPass): #if pic in insert is found this will add its data to the pic data base
                picFile = ['.jpg','.png','.jpeg']
                msgWords = msgPass.split(' ')
                custAddre = ''
                i = 0
                noPic = False
                for word in msgWords:
                        if ((picFile[0] in word) or (picFile[1] in word) or (picFile[2] in word)):
                                picFile = word
                                with open(word,'rb') as dat:
                                        fData = dat.read()
                                custPicDat = [word,fData]
                                self.picData.append(custPicDat)
                                dat.close()
                                msgWords[i] = ''
                                noPic = True
                                for element in msgWords:
                                        custAddre += (str(element) + ' ')
                                break
                        i += 1
                
                if(noPic == False):
                        custAddre = msgPass
                        picFile = ''
                #return custAddre, picFile
                return custAddre, picFile

        def picfuncData(self, custID, fileData): #additional data function for any pictures in data base
                self.picData = []
                customerPIC = []
                custPIC = 0
                picFile = ['.jpg','.png','.jpeg']
                i = 0
                for list in self.db:
                        for element in list:
                                if(custID == element):
                                        for file in list:
                                                if ((picFile[0] in file) or (picFile[1] in file) or (picFile[2] in file)):
                                                        with open(fileData, 'rb') as dat:
                                                                customerPIC[custID] = dat.read()
                                                        self.picData[i] = customerPIC[custID]
                                                        custPIC = 1
                                                        break
                                                else:
                                                        customerPIC[custID] = ''
                                                        self.picData[i] = customerPIC[custID]
                                                        break
                                if(custPIC == 1):
                                        break
                        i += 1
                        if(custPIC == 1):
                                break

        def picUpload(self, customerFirst, customerLast, fileName): #upload picture file to specific customer
                try:
                        upFile = open(fileName, 'r')       #tries to open a filename matching the one speicifed in the user input
                except FileNotFoundError:
                        errMSG = 'ERROR: File does not exist'     #input validation for invalid filename
                        return errMSG
                else: 
                        self.pic = fileName
                        i = 0
                        pos = 1
                        for customList in self.db:
                                for element in customList:
                                        if(customerFirst == customList[1] and customerLast == customList[2]):
                                                putFil = (' %s'%fileName)
                                                customList[5] = putFil
                                                fileName = str(fileName)
                                                fileName = fileName.strip()
                                                with open(fileName,'rb') as dat: #insert picture data to pic database
                                                        fData = dat.read()
                                                custPicDat = [fileName,fData]
                                                self.picData.append(custPicDat)
                                                dat.close()
                                                pos = 0
                                                break
                                        i += 1
                                if(pos == 0):
                                        break
                        if(pos == 1):
                                errMsg = 'ERROR: No Customer Found'
                                return errMsg
                        else:
                                upFile = open(fileName, 'r')       #if filename is valid, the file is opened
                                upFile.close()
                                size = os.path.getsize(fileName)   #file size is gathered, like in the download
                                posMSG = 'Operation was completed successfully picture size: ' + str(size) + ' bytes!'    #A successful file upload communicates the size of the file uploaded back to the client
                                return posMSG

        def dbpicdown(self,fileIN,custName): #when DB is download this will be called to extract picture file data from cutomers who have a picture
                picFile = ['.jpg','.png','.jpeg']
                picFND = 0
                datCol = 0
                cusFND = 0
                for custList in self.db:
                        for element in custList:
                                element = str(element)
                                if (((picFile[0] in element) or (picFile[1] in element) or (picFile[2] in element)) and (element == fileIN)):
                                        picFND = 1
                                        element = element.strip()
                                        for dict in self.picData:
                                                for filNam in dict:
                                                        if(fileIN == filNam):
                                                                pictureFile = dict[0]
                                                                picDat = dict[1]
                                                                datCol = 1
                                                                fileName = ('downloaded_filename_%s.jpg'%custName)
                                                                break
                                                if(datCol == 1):
                                                        break
                                if(datCol == 1):
                                        break
                        if(datCol == 1):
                                break


                if(picFND == 1):
                        with open(fileName,'wb') as dat:
                                dat.write(picDat)
                        dat.close()

        def picDownloadDisplay(self, cusFName, cusLName, newFileName): #download picture from specific customer
                picFile = ['.jpg','.png','.jpeg']
                picFND = 0
                datCol = 0
                cusFND = 0

                #The following nested for loops will parse both customer DB and Pic DB to find any pictures from specific customer
                for custList in self.db:
                        if ((cusFName == custList[1]) and (cusLName == custList[2])):
                                cusFND = 1
                                for element in custList:
                                        element = str(element)
                                        if ((picFile[0] in element) or (picFile[1] in element) or (picFile[2] in element)):
                                                picFND = 1
                                                element = element.strip()
                                                for dict in self.picData:
                                                        for filNam in dict:
                                                                if(element == filNam):
                                                                        picFile = dict[0]
                                                                        picDat = dict[1]
                                                                        datCol = 1
                                                                        break
                                                        if(datCol == 1):
                                                                break
                                        if(datCol == 1):
                                                break
                                if(datCol == 1):
                                        break
                        if(datCol == 1):
                                break


                if(picFND == 1):
                        with open(newFileName,'wb') as dat:
                                dat.write(picDat)
                        size = os.path.getsize(newFileName)   #gets file size of the file
                        posMSG = 'Operation was completed successfully at size ' + str(size) + ' bytes!'    #the filesize is communicated to the client
                        dat.close()
                        #connectionSocket.sendall(posMSG.encode())
                        return posMSG
                elif(picFND == 0):
                        errMsg = 'ERROR: No Picture for this Customer'
                        return errMsg
                elif(cusFND == 0):
                        errMSG = 'ERROR: No customer found'
                        return errMSG
        
        #Fill in end  


cDB = customerDB() 


# create customer database
#Fill in start  
# 
# __________________________________MAIN ()________________________________________________     
PORT = 8889    #set server port
serverSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM) #set socket variables
serverSocket.bind(('', PORT))
print ('The server is ready to receive...')
while True:
        serverSocket.listen(1)
        connectionSocket, addr = serverSocket.accept()
        newThread = cliThread(addr, connectionSocket) #set thread pass variables
        newThread.start() #start new thread
# Many lines of code to fill in here
#Fill in end
