# Standard Libraries
import socket
import threading
import time
import os

# PyQt5 - GUI Library
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

getIP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
getIP.connect(("8.8.8.8", 80))

SERVER = getIP.getsockname()[0]; getIP.close(); del(getIP)
PORT = 5005
BUFFER = 1024

WIDTH = 300
HEIGHT = 350
selectedFile = None

class MainWindow(QDialog):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("File Transfer")
        self.setWindowIcon(QtGui.QIcon("images/icon.png"))

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(WIDTH, HEIGHT)

        self.Port = QLabel("Port:", self).setObjectName("Port_Label")
        self.Port_Box = QLineEdit(self); self.Port_Box.setObjectName("Port_Box")
        self.Port_Box.setMaxLength(5); self.Port_Box.setText(str(PORT))
        self.onlyInt = QIntValidator(); self.Port_Box.setValidator(self.onlyInt)

        self.IP_Address = QLabel("Server IP:", self).setObjectName("IP_Label")
        self.IP_Box = QLineEdit(self); self.IP_Box.setObjectName("IP_Box")
        self.IP_Box.setMaxLength(15); self.IP_Box.setText(SERVER)

        self.FileButton = QPushButton("Choose File", self); self.FileButton.setObjectName("File_Button")
        self.FileButton.clicked.connect(self.BrowseFile)

        self.OutputBox = QTextEdit(self); self.OutputBox.setObjectName("Output_Box")
        self.OutputBox.setReadOnly(True); self.OutputBox.move(50, 150); self.OutputBox.resize(200, 150)

        self.SendButton = QPushButton("<Send>", self); self.SendButton.setObjectName("Send_Button")
        self.SendButton.move(70, 310); self.SendButton.clicked.connect(self.SendFile)

        self.ReceiveButton = QPushButton("<Receive>", self); self.ReceiveButton.setObjectName("Receive_Button")
        self.ReceiveButton.move(150, 310); self.ReceiveButton.clicked.connect(self.ReceiveFile)

        self.show()

    def BrowseFile(self):
        global selectedFile

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        selectedFile, _ = QFileDialog.getSaveFileName(self, "File Explorer", "", "All Files (*);;Text Files (*.txt)")
        if (selectedFile):
            self.FileButton.setText(selectedFile.split("/")[-1])

    def SendFile(self):
        global PORT
        PORT = int(self.Port_Box.text())

        self.OutputBox.setText(None)

        if (selectedFile == None or len(selectedFile) == 0):
            self.OutputBox.append("No File Selected")
        else:
            self.OutputBox.append(f"File: <span style=color:'darkred'>{selectedFile.split('/')[-1]}</span>")
            self.OutputBox.append("Attempting to Connect to Client...")

            server = ServerThread(window)
            server.daemon = True
            server.start()

            self.RestrictWidgets(False)

    def ReceiveFile(self):
        global SERVER, PORT
        SERVER = self.IP_Box.text()
        PORT = self.Port_Box.text()

        try:
            if (int(PORT) <= 0 or int(PORT) > 65535):
                self.OutputBox.append("Port Requirement: (1 - 65535)")
                return
            
            else: PORT = int(PORT)

        except ValueError:
            self.OutputBox.append(f"Invalid Port : ({PORT})")
            return

        self.OutputBox.setText(None)
        self.OutputBox.append("Attempting to Connect to Server...")

        client = ClientThread(window)
        client.daemon = True
        client.start()

        self.RestrictWidgets(False)

    def RestrictWidgets(self, boolean):
        self.SendButton.setEnabled(boolean)
        self.ReceiveButton.setEnabled(boolean)
        self.FileButton.setEnabled(boolean)
        self.IP_Box.setEnabled(boolean)
        self.Port_Box.setEnabled(boolean)

class ServerThread(threading.Thread):

    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def send(self, conn, data):
        if not (isinstance(data, bytes)):
            conn.send(bytes(data, "utf-8"))
        else:
            conn.send(data)

        time.sleep(0.3)

    def run(self):
        fileSize = str(os.path.getsize(selectedFile))
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        objSocket.bind(("0.0.0.0", PORT))
        objSocket.listen(socket.SOMAXCONN)

        while (True):
            try:
                conn, address = objSocket.accept()

                self.send(conn, selectedFile.split("/")[-1])
                self.send(conn, fileSize)

                with open(selectedFile, "rb") as LocalFile:
                    self.send(conn, LocalFile.read())

                self.window.OutputBox.append(f"\nConnected: {address[0]}\nFile Sent: {selectedFile.split('/')[-1]}\nTotal Size Sent: {fileSize} Bytes")

            except socket.error as e:
                self.window.Message(f"\nError Occured Sending File to Remote Machine ~ ({e})")

            finally:
                self.window.RestrictWidgets(True)
                break

class ClientThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while (True):
            try:
                objSocket.connect((SERVER, PORT))
            except:
                continue
            else:
                break

        data = b""
        fileName = str(objSocket.recv(BUFFER), "utf-8")
        fileSize = int(objSocket.recv(BUFFER))

        with open(fileName, "wb") as RemoteFile:
            while (len(data) < fileSize):
                data += objSocket.recv(fileSize)

            RemoteFile.write(data)

        self.window.OutputBox.append(f"\nFile Received: {fileName}\nTotal Size Received: {fileSize} Bytes")
        self.window.RestrictWidgets(True)

if __name__ == "__main__":
    application = QApplication([])
    application.setStyleSheet("""
        QLabel {
            color: red;
            font-size: 18px;
            margin: 0 auto;
        }
        #IP_Box, #Port_Box {
            background: grey;
            border: 2px solid blue;
        }
        #IP_Label {
            margin-top: 20%;
        }
        #IP_Box {
            color: black;
            font-size: 13px;
            margin-left: 125%;
            margin-top: 23%;
        }
        #Port_Label {
            margin-top: 50%;
        }
        #Port_Box {
            color: black;
            font-size: 13px;
            margin-left: 125%;
            margin-top: 53%;
        }
        #File_Button {
            background: grey;
            color: blue;

            font-size: 12px;
            height: 25%;
            width: 90%;
            margin-left: 50%;
            margin-top: 110%;
        }
        #Output_Box {
            color: black;
            background: grey;
            border: 2px solid blue;
        }
        #Send_Button, #Receive_Button {
            background-color: grey;
            color: blue;

            font-size: 12px;
            height: 20%;
            width: 60%;
        }
    """)
    window = MainWindow()
    exit(application.exec_())
