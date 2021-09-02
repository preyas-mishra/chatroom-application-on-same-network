from PyQt5 import QtCore, QtWidgets
import register2
import chat
#from server import *
import sys
import socket
import random


class ReceiveThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, client_socket):
        super(ReceiveThread, self).__init__()
        self.client_socket = client_socket

    def run(self):
        while True:
            self.receive_message()

    def receive_message(self):
        message = self.client_socket.recv(1024)
        message = message.decode()

        print(message)
        self.signal.emit(message)

class Client(object):
    def __init__(self):
        self.messages = []

        self.mainWindow = QtWidgets.QMainWindow()
        self.connectWidget = QtWidgets.QWidget(self.mainWindow)
        self.chatWidget = QtWidgets.QWidget(self.mainWindow)

        self.chatWidget.setHidden(True)

        self.chat_ui = chat.Ui_MainWindow()
        self.chat_ui.setupUi(self.chatWidget)
        self.chat_ui.pushButton.clicked.connect(self.send_message)

        self.connect_ui = register2.Ui_MainWindow()
        self.connect_ui.setupUi(self.connectWidget)
        self.connect_ui.pushButton.clicked.connect(self.btn_connect_clicked)

        # MainWindow.setCentralWidget(self.centralwidget)
        # self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 904, 9))
        # self.menubar.setObjectName("menubar")
        # MainWindow.setMenuBar(self.menubar)
        # self.statusbar = QtWidgets.QStatusBar(MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)


        self.mainWindow.setGeometry(QtCore.QRect(200, 200, 930, 780))    #200 200 930 780
        self.mainWindow.show()

        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def btn_connect_clicked(self):
        host = self.connect_ui.lineEdit.text()
        port = self.connect_ui.lineEdit_2.text()
        name = self.connect_ui.lineEdit_3.text()
        #id = self.connect_ui.lineEdit_4.text()

        if len(host) == 0:
            host = "localhost"

        if len(port) == 0:
            port = 5555
        else:
            try:
                port = int(port)
            except Exception as e:
                error = "Invalid port number \n'{}'".format(str(e))
                print("[INFO]", error)
                self.show_error("Port Number Error", error)

        if len(name) < 1:
            name = socket.gethostname()

        name = name + "_" + str(random.randint(1, port))

        if self.connect(host, port, name):
            self.connectWidget.setHidden(True)
            self.chatWidget.setVisible(True)

            self.recv_thread = ReceiveThread(self.tcp_client)
            self.recv_thread.signal.connect(self.show_message)
            self.recv_thread.start()
            print("[INFO] recv thread started")
            #print(len(clients))
            #self.chat_ui.textBrowser_2.append(server.totalClients())
    def show_message(self, message):
        self.chat_ui.textBrowser.append(message)


    def connect(self, host, port, name):

        try:
            self.tcp_client.connect((host, port))
            self.tcp_client.send(name.encode())

            print("[INFO] Connected to server")

            return True
        except Exception as e:
            error = "Unable to connect to server \n'{}'".format(str(e))
            print("[INFO]", error)
            self.show_error("Connection Error", error)
            self.connect_ui.lineEdit.clear()
            self.connect_ui.lineEdit_2.clear()

            return False


    def send_message(self):
        message = self.chat_ui.lineEdit.text()
        self.chat_ui.textBrowser.append("Me: " + message)

        print("sent: " + message)

        try:
            self.tcp_client.send(message.encode())
        except Exception as e:
            error = "Unable to send message '{}'".format(str(e))
            print("[INFO]", error)
            self.show_error("Server Error", error)
        self.chat_ui.lineEdit.clear()


    def show_error(self, error_type, message):
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setText(message)
        errorDialog.setWindowTitle(error_type)
        errorDialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        errorDialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    c = Client()
    sys.exit(app.exec())
