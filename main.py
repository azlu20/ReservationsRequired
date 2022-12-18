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

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QPushButton, QFormLayout, QLineEdit, QCalendarWidget, QComboBox, QGridLayout

from PyQt6.QtGui import QTextCharFormat, QFont

from PyQt6.QtCore import QDate, QTimer, QTime

from datetime import date

from cred_bank import CredentialBank

from open_site import AutoReserveCourt


class Window(QWidget):
    def __init__(self):

        super().__init__()
        self.credBank = CredentialBank()

        self.site = AutoReserveCourt()
        self.loggedIn = False
        self.onPage = False
        self.selectedDate = date.today().strftime("%m/%d/%y")
        self.duration = "30"
        self.selectedQDate = QDate.currentDate()
        self.time = None
        self.location = None
        self.selectedTempQDate = None
        self.selectedTempDate = None
        self.temporaryDuration = "30"
        self.temporaryTime = None
        self.temporaryLocation = None
        # self.timeLabel = QLabel(QTime.currentTime().toString())
        # self.timerLabel = QLabel("No configuration selected at the moment")
        self.timer = None
        self.displayCurrentTimer = None
        self.countDown = None
        self.designatedTime = None
        time = QTime().currentTime()
        self.timeLabel = QLabel(time.toString() + "." + str(time.msec()))

        self.first = True
        self.initialize()
    def closeEvent(self, a) -> None:
        self.site.driver.quit()

    def reInitialize(self):
        QWidget().setLayout(self.layout())
        self.initialize()

    def updateTimeLabel(self):
        sender = self.sender()
        time = QTime().currentTime()
        if(self.timeLabel is not None and self.atMain):
            self.timeLabel.setText(time.toString() + "." + str(time.msec()))
        else:
            sender.stop()

    def initialize(self):
        self.atMain = True
        updateLogin = QPushButton("Update Login")
        updateLogin.clicked.connect(self.LoginWindow)

        self.timerLabel = QLabel("No configuration selected at the moment")

        checkLogin = QPushButton("Open Site")
        checkLogin.setObjectName("Open Site")
        checkLogin.clicked.connect(self.initialLogin)

        setTime = QPushButton("Set Time")
        setTime.setObjectName("set_time")
        setTime.clicked.connect(self.reserveCourtPage)

        layout = QGridLayout()
        layout.addWidget(updateLogin)
        layout.addWidget(checkLogin)
        layout.addWidget(setTime)
        layout.addWidget(QPushButton("Logout"))

        timeLabelTimer = QTimer(self)
        timeLabelTimer.start(1)
        timeLabelTimer.timeout.connect(self.updateTimeLabel)
        layout.addWidget(self.timeLabel)


        timerLabelTimer = QTimer(self)
        timerLabelTimer.start(1)
        timerLabelTimer.timeout.connect(self.updateTimerLabel)
        layout.addWidget(self.timerLabel)

        self.eventLabel = QLabel()
        self.eventLabel.setObjectName("eventLabel")



        self.setLayout(layout)

        # self.time = "10:00pm"
        # self.duration = "60"
        #todo load in previously saved date/time/location if existed before and change timerlabel accordingly so
        self.startTimeCountdown()
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
        self.dateChanged(QDate.currentDate())
        # layout = self.calendarLayout()
        # self.setLayout(layout)

    def calendarLayout(self):
        self.atMain = False
        self.setWindowTitle("CPAC Info")
        layout = QFormLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setGeometry(50, 10, 400, 250)
        dateFormat = QTextCharFormat()
        dateFormat.setFont(QFont('Times', 15))
        # curDate = date.today().strftime("%m/%d/%Y")
        # curDateList = curDate.split("/")
        # calendarDate = self.selectedQDate
        # self.calendar.setDateTextFormat(calendarDate, dateFormat)
        self.calendar.clicked[QDate].connect(self.dateChanged)
        duration = QComboBox()
        duration.addItem("30")
        duration.addItem("60")
        duration.addItem("90")
        duration.addItem("120")
        duration.setObjectName("duration")
        duration.currentTextChanged.connect(self.durationChanged)

        layout.addWidget(self.calendar)

        layout.addWidget(duration)
        # self.dateChanged()
        return layout

    def durationChanged(self, s):
        self.temporaryDuration = s

    def dateChanged(self, date):
        if(self.first):
            QWidget().setLayout(self.layout())
        layout = self.calendarLayout()
        curDate = date
        print(curDate)
        self.selectedTempQDate = curDate
        self.selectedTempDate = '{0}/{1}/{2}'.format(curDate.month(), curDate.day(), curDate.year())
        eastTimes, westTimes = self.site.populateAvailableTimes(self.selectedTempDate, self.temporaryDuration)
        print(eastTimes)
        print(westTimes)
        if (eastTimes is None and westTimes is None) or len(eastTimes) == 0 and len(westTimes)==0:
            self.eventLabel = QLabel("No available times")
            layout.addWidget(self.eventLabel)
            self.setLayout(layout)
            return

        # for ele in eastTimes:
        #     selectTime = QPushButton("East " + ele)
        #     selectTime.setObjectName("East " + ele)
        #     selectTime.clicked.connect(self.updateTime)
        #     layout.addWidget(selectTime)
        # for ele in westTimes:
        #     selectTime = QPushButton("West " + ele)
        #     selectTime.setObjectName("West "+ ele)
        #     selectTime.clicked.connect(self.updateTime)
        #     layout.addWidget(selectTime)

        confirmationButton = QPushButton("Confirmation")
        confirmationButton.clicked.connect(self.confirmTimeLocation)
        layout.addWidget(confirmationButton)
        if(self.first):
            self.setLayout(layout)
            self.first = False

    def confirmTimeLocation(self):
        if self.temporaryTime and self.temporaryLocation and self.temporaryDuration and self.selectedTempQDate and self.selectedTempDate:
            self.time = self.temporaryTime
            self.location = self.temporaryLocation
            self.duration = self.temporaryDuration
            self.selectedQDate = self.selectedTempQDate
            self.selectedDate = self.selectedTempQDate

        #todo possibly pass a flag to timerlabel

    def updateTime(self): #todo add confirmation, then set location to automatically l=6 or l=1. then will exit back to homepage
        splitName = self.sender().objectName().split(" ")
        self.temporaryTime = splitName[1]
        self.temporaryLocation = splitName[0]

    def startTimeCountdown(self):
        if self.time is None or self.selectedDate is None or (self.duration is None):
            self.timerLabel.setText(
                "There is an issue with the set time, date, or duration. Please try again or select other times.")
            return
        if self.selectedQDate == QDate().currentDate():
            self.timer = QTimer()
            h = None
            m = None
            minuteFlag = -1
            i = 0
            if self.time[1] == ":":
                h = self.time[0]
                m = self.time[2] + self.time[3]
            else:
                h = self.time[0] + self.time[1]
                m = self.time[3]+self.time[4]
            if h is None or m is None or not h.isnumeric() or not m.isnumeric():
                self.timerLabel.setText("Could not get a time from the selected time.")
                return

            if "pm" in self.time:
                h = int(h) + 12
            m = int(m)

            self.designatedTime = QTime()
            self.designatedTime.setHMS(h, m, 0)
            currentTime = QTime.currentTime()
            self.countDown = currentTime.msecsTo(self.designatedTime)
            print(self.countDown)
            if self.countDown < 0:
                self.timerLabel.setText("Designated time is after current time. Please select a new time.")
            else:
                if self.countDown > 1000: # 7200000: two hours before in milliseconds
                    #self.timer.singleShot(self.countDown+150, self.registerForCourt)

                    self.timer.singleShot(1000, self.registerForCourt)

    def updateTimerLabel(self):
        sender = self.sender()
        if self.countDown is not None and self.countDown > 0 and self.designatedTime is not None and self.atMain:
            currentTime = QTime().currentTime()
            print("should be changing")
            self.timerLabel.setText("Timer set in place. Will activate in " + str(currentTime.msecsTo(self.designatedTime) + 150)) #Todo add msecs conversion back to h:m:s
        else:
            sender.stop()
    def registerForCourt(self):
        print("worked for now!")
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