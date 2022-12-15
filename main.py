# import sys
# import os
#
# from PyQt6.QtGui import QGuiApplication
# from PyQt6.QtQml import QQmlApplicationEngine
# from PyQt6.QtQuick import QQuickWindow
#
# QQuickWindow.setSceneGraphBackend('software')
#
# app = QGuiApplication(sys.argv)
#
#
# engine = QQmlApplicationEngine()
# engine.quit.connect(app.quit)
# engine.load("C:\\Users\\lualb\\Desktop\\court_reservation\\main.qml")
#
# sys.exit(app.exec())
#


#Notes:
#Things I could have done better:
#Make each of these windows there own classes with abstraction for showing and setting
#override widgets in their own classses instead of pushing everything into this one class
#modularize better with cred_bank and open_site
#figure out better error handling and passing parameters between stages

import sys

import os


from getpass import getpass

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QPushButton, QFormLayout, QLineEdit, QCalendarWidget, QComboBox

from PyQt6.QtGui import QTextCharFormat, QFont

from PyQt6.QtCore import QDate

from datetime import date

from cred_bank import CredentialBank

from open_site import AutoReserveCourt


class Window(QWidget):
    def __init__(self):

        super().__init__()
        self.credBank = CredentialBank()
        self.initialize()
        self.site = AutoReserveCourt()
        self.loggedIn = False
        self.onPage = False
        self.selectedDate = date.today().strftime("%m/%d/%y")
        self.duration = "30"
        self.selectedQDate = QDate.currentDate()
        self.time = None
        self.location = None

    def closeEvent(self, a) -> None:
        self.site.driver.quit()

    def reInitialize(self):
        QWidget().setLayout(self.layout())
        self.initialize()

    def initialize(self):
        updateLogin = QPushButton("Update Login")
        updateLogin.clicked.connect(self.LoginWindow)

        checkLogin = QPushButton("Open Site")
        checkLogin.setObjectName("Open Site")
        checkLogin.clicked.connect(self.initialLogin)

        setTime = QPushButton("Set Time")
        setTime.setObjectName("set_time")
        setTime.clicked.connect(self.reserveCourtPage)

        layout = QHBoxLayout()
        layout.addWidget(updateLogin)
        layout.addWidget(checkLogin)
        layout.addWidget(setTime)
        layout.addWidget(QPushButton("Logout"))

        self.eventLabel = QLabel()
        self.eventLabel.setObjectName("eventLabel")

        self.setLayout(layout)

        self.resize(270, 110)

    def SetTimeWindow(self):
        pass

    def LoginWindow(self):
        QWidget().setLayout(self.layout())
        self.setWindowTitle("CPAC Info")
        layout = QFormLayout()

        self.eventLabel = QLabel()
        self.eventLabel.setObjectName("eventLabel")

        # Add widgets to the layout
        self.username = QLineEdit()
        self.username.setObjectName("username")

        self.password = QLineEdit()
        self.password.setObjectName("password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        submit = QPushButton("Submit")
        submit.setObjectName("submit")
        submit.clicked.connect(self.submitInfo)

        back = QPushButton("Back")
        back.setObjectName("back")
        back.clicked.connect(self.reInitialize)

        layout.addRow("Username:", self.username)
        layout.addRow("Password", self.password)
        layout.addWidget(self.eventLabel)
        layout.addWidget(submit)
        layout.addWidget(back)

        self.setLayout(layout)
        self.resize(270, 110)


    def submitInfo(self):

        if len(self.username.text()) > 0 and len(self.password.text()) > 0: #temp check, will do initial real check
            self.credBank.storeCredentials(self.username.text(), self.password.text())
            return self.validateLogin()
        return False

    def validateLogin(self):
        username, password = self.credBank.getCredentials()
        if self.site.checkLogin(username, password):
            self.eventLabel.setText("Login Successful")
            return True
        self.eventLabel.setText("Login Failed")
        return False

    def initialLogin(self):
        username, password = self.credBank.getCredentials()
        self.loggedIn = self.site.formalLogin(username, password)
        if self.loggedIn:
            self.eventLabel = "Logged In!"
        else:
            self.eventLabel = "Could not log on. Try updating login Info"
    def reserveCourtPage(self):
        if not self.loggedIn:
            self.loggedIn = self.initialLogin()

        self.onPage = self.site.goToReserveCourt()
        layout = self.calendarLayout()
        self.setLayout(layout)

    def calendarLayout(self):
        QWidget().setLayout(self.layout())
        self.setWindowTitle("CPAC Info")
        layout = QFormLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setGeometry(50, 10, 400, 250)
        dateFormat = QTextCharFormat()
        dateFormat.setFont(QFont('Times', 15))
        # curDate = date.today().strftime("%m/%d/%Y")
        # curDateList = curDate.split("/")
        calendarDate = self.selectedQDate
        self.calendar.setDateTextFormat(calendarDate, dateFormat)
        self.calendar.clicked.connect(self.dateChanged)

        duration = QComboBox()
        duration.addItem("30")
        duration.addItem("60")
        duration.addItem("90")
        duration.addItem("120")
        duration.setObjectName("duration")
        duration.currentTextChanged.connect(self.durationChanged)

        layout.addWidget(self.calendar)
        layout.addWidget(duration)
        return layout

    def durationChanged(self, s):
        self.duration = s

    def dateChanged(self):
        curDate = self.calendar.selectedDate()
        self.selectedQDate = curDate
        self.selectedDate = '{0}/{1}/{2}'.format(curDate.month(), curDate.day(), curDate.year())
        eastTimes, westTimes = self.site.populateAvailableTimes(self.selectedDate, self.duration)
        layout = self.calendarLayout()
        if len(eastTimes) == 0 and len(westTimes)==0:
            self.eventLabel = QLabel("No available times")
            layout.addWidget(self.eventLabel)
            return

        for ele in eastTimes:
            selectTime = QPushButton("East " + ele)
            selectTime.setObjectName("East " + ele)
            selectTime.clicked.connect(self.updateTime)
            layout.addWidget(selectTime)
        for ele in westTimes:
            selectTime = QPushButton("West " + ele)
            selectTime.setObjectName("West "+ ele)
            selectTime.clicked.connect(self.updateTime)
            layout.addWidget(selectTime)
        self.setLayout(layout)

    def updateTime(self):
        splitName = self.sender().objectName().split(" ")
        self.time =  splitName[1]
        self.location = splitName[0]
        # self.resize(270, 110)
        # date = QDate()
# class LoginWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("CPAC Info")
#         layout = QFormLayout()
#
#         self.eventLabel = QLabel()
#         self.eventLabel.setObjectName("eventLabel")
#
#         # Add widgets to the layout
#         self.username = QLineEdit()
#         self.username.setObjectName("username")
#
#         self.password = QLineEdit()
#         self.password.setEchoMode(QLineEdit.EchoMode.Password)
#         self.password.setObjectName("password")
#
#
#         submit = QPushButton("Submit")
#         submit.setObjectName("submit")
#         submit.clicked.connect(self.submitInfo)
#
#         layout.addRow("Username:", self.username)
#         layout.addRow("Password", self.password)
#         layout.addWidget(self.eventLabel)
#         layout.addWidget(submit)
#
#         self.setLayout(layout)
#         self.resize(270, 110)
#
#     def submitInfo(self):
#         if len(self.username.text()) > 0 and len(self.password.text()) > 0: #temp check, will do initial real check
#             print(self.username.text())
#             self.eventLabel.setText("Login Successful")
#         else:
#             self.eventLabel.setText("Login Faild")
#         # Set the layout on the application's window
#


app = QApplication([])
window = Window()
window.setWindowTitle("PyQt App")
window.setGeometry(100, 100, 280, 80)
window.show()
sys.exit(app.exec())