# Standard Libraries
import socket, threading, time, os

# PyQt5 - GUI Library
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# Get Local IP Address
objSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
objSocket.connect(("8.8.8.8", 80))

IP = objSocket.getsockname()[0]
PORT = 10000

objSocket.close(); del(objSocket)

class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Disable Maximize Button and Stretch
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(300, 350)

        self.setWindowTitle("File Transfer")
        self.setWindowIcon(QtGui.QIcon("image.png"))

        self.IP_Address = QLabel("IP Address:", self).setObjectName("IP_Label")
        self.IP_Box = QLineEdit(self); self.IP_Box.setObjectName("IP_Box"); self.IP_Box.setText(IP)

        self.Port = QLabel("Port:", self).setObjectName("Port_Label")
        self.Port_Box = QLineEdit(self); self.Port_Box.setObjectName("Port_Box")
        self.Port_Box.setMaxLength(5); self.Port_Box.setText(str(PORT))

        self.FileButton = QPushButton("<Choose File>", self); self.FileButton.setObjectName("File_Button")
        self.FileButton.clicked.connect(self.BrowseFile)

        self.OutputBox = QTextEdit(self); self.OutputBox.setObjectName("Output_Box")
        self.OutputBox.setReadOnly(True); self.OutputBox.move(50, 150); self.OutputBox.resize(200, 150)

        self.SendButton = QPushButton("<Send>", self); self.SendButton.setObjectName("Send_Button")
        self.SendButton.move(70, 310); self.SendButton.clicked.connect(self.SendFile)

        self.ReceiveButton = QPushButton("<Receive>", self); self.ReceiveButton.setObjectName("Receive_Button")
        self.ReceiveButton.move(150, 310); self.ReceiveButton.clicked.connect(self.ReceiveFile)

        self.show()

    def BrowseFile(self):
        global SelectedFile

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        SelectedFile, _ = QFileDialog.getSaveFileName(self,"File Explorer","","All Files (*);;Text Files (*.txt)", options=options)
        if (SelectedFile):
            SelectedFile = SelectedFile.split("/")[-1]
            self.FileButton.setText(SelectedFile)

    def SendFile(self):
        self.OutputBox.setText(None)

        try:
            if (SelectedFile == ""):
                raise Exception

            self.OutputBox.append("File: " + SelectedFile + "\nAttempting to Connect to Client...")
        except:
            self.OutputBox.append("No File Selected")
            return
        
        server = ServerThread(window)
        server.daemon = True
        server.start()

    def ReceiveFile(self):
        global ServerIP; ServerIP = self.IP_Box.text()

        self.OutputBox.setText(None)
        self.OutputBox.append("Attempting to Connect to Server...")

        client = ClientThread(window)
        client.daemon = True
        client.start()

    def Message(self, message):
        self.OutputBox.append(message)

class ServerThread(threading.Thread):

    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        FileSize = str(os.path.getsize(SelectedFile))

        objSocket.bind(("0.0.0.0", PORT))
        objSocket.listen(socket.SOMAXCONN)
        while (True):
            try:
                conn, address = objSocket.accept()
                self.window.Message("File Sent Sucessfully")
                
                conn.send(bytes(SelectedFile, "utf-8")); time.sleep(0.3); conn.send(bytes(FileSize, "utf-8"))
                with open(SelectedFile, "rb") as file:
                    conn.send(file.read())

            except socket.error:
                self.window.Message("Error Transferring File to Client")

            finally: break

class ClientThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        data = b""

        while (True):
            try:
                objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                objSocket.connect((ServerIP, PORT))
            except:
                continue
            else:
                break
        
        FileName = str(objSocket.recv(1024).decode())
        FileSize = int(objSocket.recv(1024))

        while (len(data) < FileSize):
            data += objSocket.recv(FileSize)

        with open(FileName, "wb") as ReceivedFile:
            ReceivedFile.write(data)

        self.window.Message(f"File Successfully Received\n\nFile Name: {FileName}\nFile Size: {FileSize} Bytes")

if __name__ == "__main__":
    application = QApplication([])
    application.setStyleSheet("""
        QLabel {
            color: red;
            font-size: 18px;
            margin: 0 auto;
            text-decoration: underline;
        }
        QLineEdit {
            color: green;
        }
        #IP_Box, #Port_Box {
            background: lightgrey;
        }
        #IP_Label {
            margin-top: 20%;
        }
        #IP_Box {
            margin-left: 135%;
            margin-top: 23%;
        }
        #Port_Label {
            margin-top: 50%;
        }
        #Port_Box {
            margin-left: 135%;
            margin-top: 53%;
        }
        #File_Button {
            background: grey;
            color: blue;

            font-size: 12px;
            height: 25%;
            width: 90%;
            margin: 0 auto;
            margin-top: 100%;
        }
        #Output_Box {
            background: grey;
            border: 2px solid blue;
        }
        #Send_Button, #Receive_Button {
            background: grey;
            color: blue;

            font-size: 12px;
            height: 20%;
            width: 60%;
        }
    """)
    window = MainWindow()
    exit(application.exec_())