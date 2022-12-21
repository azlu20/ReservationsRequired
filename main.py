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


# Notes:
# Things I could have done better:
# Make each of these windows there own classes with abstraction for showing and setting
# override widgets in their own classses instead of pushing everything into this one class
# modularize better with cred_bank and open_site
# figure out better error handling and passing parameters between stages

import sys

import os

from getpass import getpass

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QPushButton, QFormLayout, QLineEdit, \
    QCalendarWidget, QComboBox, QGridLayout

from PyQt6.QtGui import QTextCharFormat, QFont

from PyQt6.QtCore import QDate, QTimer, QTime

from datetime import date

from cred_bank import CredentialBank

from open_site import AutoReserveCourt


class Window(QWidget):
    def __init__(self):

        super().__init__()
        self.credBank = CredentialBank()


        self.loginPage = None
        self.loginLayout = None
        self.calendarPage = None
        self.calendar_layout = None
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

        self.timeLabelTimer= None
        self.timerLabelTimer = None
        # self.timeLabel = QLabel(QTime.currentTime().toString())
        # self.timerLabel = QLabel("No configuration selected at the moment")
        self.timer = None
        self.displayCurrentTimer = None
        self.countDown = None
        self.designatedTime = None
        time = QTime().currentTime()
        self.timeLabel = QLabel(time.toString() + "." + str(time.msec()))
        self.eastButtons = []
        self.westButtons = []
        self.first = True

        self.previouslyClicked = None
        self.onTime = False
        self.initializedCalendar = False
        self.initializedLoginScreen = False
        self.initialize()




    def closeEvent(self, a) -> None:
        self.site.driver.quit()

    def reInitialize(self):
        QWidget().setLayout(self.layout())
        self.initialize()

    def updateTimeLabel(self):
        sender = self.sender()
        time = QTime().currentTime()
        self.timeLabel.setText("Current Time " + time.toString() + "." + str(time.msec())) #should use f strings here

    def initialize(self):
        self.atMain = True
        updateLogin = QPushButton("Update Login")
        updateLogin.clicked.connect(self.LoginWindow)

        cred_exists = self.credBank.checkCredentialsExists()
        if cred_exists:
            self.timerLabel = QLabel("Credentials Exist on This PC")
        else:
            self.timerLabel = QLabel("No Credentials! Please update login before continuing!")

        checkLogin = QPushButton("Open Site")
        checkLogin.setObjectName("Open Site")
        checkLogin.clicked.connect(self.initialLogin)

        #uhhhhhhhhh why is there 3 versions of different conventions? I should really read over my code before working on it
        setTime = QPushButton("Set Time")
        setTime.setObjectName("set_time")
        setTime.clicked.connect(self.reserveCourtPage)

        logOut = QPushButton("Logout")
        logOut.setObjectName("Logout")
        logOut.clicked.connect(self.logOut)

        layout = QGridLayout()
        layout.addWidget(updateLogin)
        layout.addWidget(checkLogin)
        layout.addWidget(setTime)
        layout.addWidget(logOut)

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

        self.test_widget = QWidget()
        self.test_widget.setLayout(layout)
        self.test_widget.show()
        # self.setLayout(layout)

        # self.time = "10:00pm"
        # self.duration = "60"
        # todo load in previously saved date/time/location if existed before and change timerlabel accordingly so
        self.startTimeCountdown()
        self.resize(270, 110)

    def SetTimeWindow(self):
        pass

    def LoginWindow(self):
        if self.loginPage is not None:
            self.loginPage.show()
            return

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


        layout.addRow("Username:", self.username)
        layout.addRow("Password", self.password)
        layout.addWidget(self.eventLabel)
        layout.addWidget(submit)
        layout.addWidget(back)

        self.loginPage = QWidget()
        self.loginPage.setLayout(layout)
        self.loginPage.show()
        back.clicked.connect(self.loginPage.hide)
        return

    def submitInfo(self):

        if len(self.username.text()) > 0 and len(self.password.text()) > 0:  # temp check, will do initial real check
            self.credBank.storeCredentials(self.username.text(), self.password.text())
            return self.validateLogin()
        return False

    def validateLogin(self):

        username, password = self.credBank.getCredentials()
        if self.site.checkLogin(username, password):
            self.eventLabel.setText("Login Successful. You can safely close out of this window.")
            self.timerLabel.setText("Login Successful. Can now open site or choose time.")
            return True
        self.eventLabel.setText("Login Failed")
        return False

    def initialLogin(self):
        cred_exists = self.credBank.checkCredentialsExists()
        print(cred_exists)
        if not cred_exists:
            self.timerLabel.setText("Login Failed! Credentials does not exist!")
            return False
        username, password = self.credBank.getCredentials()
        self.loggedIn = self.site.formalLogin(username, password)
        if self.loggedIn:
            self.timerLabel.setText("Logged in! Please select a time now.")
        else:
            self.timerLabel.setText("Failed to login. Please update credentials.")

    def logOut(self):

        cred_exists = self.credBank.checkCredentialsExists()
        if not cred_exists:
            self.timerLabel.setText("Could not delete credentials. It probably does not exist.")
            return

        self.credBank.removeCredentials()
        self.timerLabel.setText("Successfully deleted!")
        self.onPage = False
        self.loggedIn = False
        if self.timer:
            self.timer.stop()
        self.designatedTime = None
        return


    def reserveCourtPage(self):
        if not self.loggedIn:
            self.loggedIn = self.initialLogin()
        if self.loggedIn and not self.onPage:
            self.onPage = self.site.goToReserveCourt()
        if self.loggedIn and self.onPage:
            print("yes thats me")
            self.dateChanged(QDate.currentDate())
        # layout = self.calendarLayout()
        # self.setLayout(layout)

    def calendarLayout(self):
        self.atMain = False
        self.setWindowTitle("CPAC Info")
        outerlayout = QGridLayout()
        layout = QFormLayout()

        outerlayout.addLayout(layout, 0, 0, 1, 2)
        outerlayout.addWidget(QPushButton(), 2, 0)
        outerlayout.addWidget(QPushButton(), 2, 1)
        outerlayout.addWidget(QPushButton(), 3, 0)
        outerlayout.addWidget(QPushButton(), 3, 1)
        outerlayout.addWidget(QPushButton(), 4, 0)
        outerlayout.addWidget(QPushButton(), 4, 1)
        self.calendar = QCalendarWidget()
        self.calendar.setGeometry(50, 10, 400, 250)
        dateFormat = QTextCharFormat()
        dateFormat.setFont(QFont('Times', 15))
        # curDate = date.today().strftime("%m/%d/%Y")
        # curDateList = curDate.split("/")
        # calendarDate = self.selectedQDate
        # self.calendar.setDateTextFormat(calendarDate, dateFormat)
        self.calendar.clicked[QDate].connect(self.dateChanged)

        layout.addWidget(self.calendar)

        # self.dateChanged()
        return outerlayout

    def durationChanged(self, s):
        self.temporaryDuration = s
        self.reserveCourtPage()

    def dateChanged(self, date):
        updateFlag = False
        # if (self.first):  # todo check if this is necessary
        if not self.calendarPage:
            self.calendar_layout = self.calendarLayout()
            updateFlag = True
        else:
            if self.initializedCalendar:
                self.calendarPage.show()

        curDate = date
        print(curDate)
        self.selectedTempQDate = curDate
        self.selectedTempDate = '{0}/{1}/{2}'.format(curDate.month(), curDate.day(), curDate.year())
        if self.loggedIn and self.onPage:
            eastTimes, westTimes = self.site.populateAvailableTimes(self.selectedTempDate, self.temporaryDuration)
        else:
            self.initialLogin()
            if not self.loggedIn:
                not_logged_label = QLabel(
                    "Could not log in! Please go back and check if you have the right credentials!")
                self.calendar_layout.addWidget(not_logged_label)
                return
            else:
                print("this happened!")
                self.onPage = self.site.goToReserveCourt()
                if not self.onPage:
                    not_logged_label = QLabel(
                        "Logged in but could not get on reserve page!")
                    self.calendar_layout.addWidget(not_logged_label)
                    return
                else:
                    eastTimes, westTimes = self.site.populateAvailableTimes(self.selectedTempDate,
                                                                            self.temporaryDuration)
        print(eastTimes)
        print(westTimes)
        if (eastTimes is None and westTimes is None) or len(eastTimes) == 0 and len(westTimes) == 0:
            self.eventLabel = QLabel("No available times")
            self.calendar_layout.addWidget(self.eventLabel)
            # self.setLayout(layout)
            if updateFlag:
                print("created page?")
                self.calendarPage = QWidget()
                self.calendarPage.setLayout(self.calendar_layout)
                self.calendarPage.show()
            return

        start_row_east = 2
        start_row_west = 2
        i = 0
        j = 0
        while i < len(self.eastButtons) and i < len(eastTimes):
            curButton = self.eastButtons[i]
            curButton.show()
            curButton.setText(f"East {eastTimes[i]}")
            curButton.setObjectName(f"East {eastTimes[i]}")
            curButton.clicked.connect(self.updateTime)
            i += 1

        if len(self.eastButtons) >= len(eastTimes):
            while i < len(self.eastButtons):
                curButton = self.eastButtons[i]
                curButton.hide()
                print(f"i value: {i}")
                i += 1
        else:
            while i < len(eastTimes):
                newButton = QPushButton(f"East {eastTimes[i]}")
                newButton.setObjectName(f"East {eastTimes[i]}")
                newButton.clicked.connect(self.updateTime)
                self.eastButtons.append(newButton)
                self.calendar_layout.addWidget(newButton, i + 2, 0)
                i += 1

        while j < len(self.westButtons) and j < len(westTimes):
            curButton = self.westButtons[j]
            curButton.show()
            curButton.setText(f"West {westTimes[j]}")
            curButton.setObjectName(f"West {westTimes[j]}")
            curButton.clicked.connect(self.updateTime)
            j += 1


        if len(self.westButtons) >= len(westTimes):
            while j < len(self.westButtons):
                print("happening!")
                curButton = self.westButtons[j]
                curButton.hide()
                j += 1
        else:
            while j < len(westTimes):
                newButton = QPushButton(f"West {westTimes[j]}")
                newButton.setObjectName(f"West {westTimes[j]}")
                newButton.clicked.connect(self.updateTime)
                self.westButtons.append(newButton)
                self.calendar_layout.addWidget(newButton, j + 2, 1)
                j += 1
        # for ele in eastTimes:
        #     selectTime = QPushButton("East " + ele)
        #     selectTime.setObjectName("East " + ele)
        #     selectTime.clicked.connect(self.updateTime)
        #     #layout.addWidget(selectTime, start_row_east, 0)
        #     #start_row_east += 1
        #
        # for ele in westTimes:
        #     selectTime = QPushButton("West " + ele)
        #     selectTime.setObjectName("West " + ele)
        #     selectTime.clicked.connect(self.updateTime)
        #     #layout.addWidget(selectTime, start_row_west, 1)
        #     #start_row_west += 1


        # if (self.first):
        if updateFlag:
            print("created page?")
            durationLabel = QLabel("Duration")

            duration = QComboBox()
            duration.addItem("30")
            duration.addItem("60")
            duration.addItem("90")
            duration.addItem("120")
            duration.setObjectName("duration")
            duration.currentTextChanged.connect(self.durationChanged)

            confirmationButton = QPushButton("Confirmation")
            confirmationButton.clicked.connect(self.confirmTimeLocation)

            backButton = QPushButton("Back")
            backButton.clicked.connect(self.returnBackHome)

            self.calendar_layout.addWidget(durationLabel, 1, 0)
            self.calendar_layout.addWidget(duration, 1, 1)
            self.calendar_layout.addWidget(backButton)
            self.calendar_layout.addWidget(confirmationButton)

            self.calendarPage = QWidget()
            self.calendarPage.setLayout(self.calendar_layout)
            self.calendarPage.show()
            # self.setLayout(layout)
            # self.first = False

    def returnBackHome(self):
        self.selectedTempQDate = None
        self.selectedTempDate = None
        self.temporaryDuration = "30"
        self.temporaryTime = None
        self.temporaryLocation = None
        self.previouslyClicked = None
        self.calendarPage.hide()
        self.initializedCalendar = True

    def confirmTimeLocation(self):
        if self.temporaryTime and self.temporaryLocation and self.temporaryDuration and self.selectedTempQDate and self.selectedTempDate:
            self.time = self.temporaryTime
            self.location = self.temporaryLocation
            self.duration = self.temporaryDuration
            self.selectedQDate = self.selectedTempQDate
            self.selectedDate = self.selectedTempDate

            if self.timer is not None:
                self.timer.stop()

            self.startTimeCountdown()
        self.returnBackHome()
        # todo possibly pass a flag to timerlabel

    def updateTime(
            self):  # todo add confirmation, then set location to automatically l=6 or l=1. then will exit back to homepage
        sender = self.sender()
        splitName = sender.objectName().split(" ")
        self.temporaryTime = splitName[1]
        self.temporaryLocation = splitName[0]
        if self.previouslyClicked is not None:
            print(self.previouslyClicked)
            self.previouslyClicked.setStyleSheet("background-color:light grey")

        sender.setStyleSheet("background-color:grey")
        self.previouslyClicked = sender

    def startTimeCountdown(self):
        if self.time is None or self.selectedDate is None or (self.duration is None):
            # self.timerLabel.setText(
            #     "There is an issue with the set time, date, or duration. Please try again or select other times.")
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
                m = self.time[3] + self.time[4]
            if h is None or m is None or not h.isnumeric() or not m.isnumeric():
                self.timerLabel.setText("Could not get a time from the selected time.")
                return

            if "pm" in self.time:
                h = int(h) + 12
            m = int(m)

            self.designatedTime = QTime()
            self.designatedTime.setHMS(h-2, m, 0)
            currentTime = QTime.currentTime()
            difference = currentTime.msecsTo(self.designatedTime)
            print(difference)

            if difference > 7200000:  # 7200000: two hours before in milliseconds
                # self.timer.singleShot(self.countDown+150, self.registerForCourt)
                self.countDown = difference - 7182000 #around 20 seconds of buffer to validate page then final timer will begin
                self.timer.singleShot(self.countDown, self.registerForCourt)
            else:
                self.registerForCourt(safe=True) #TODO and check for no invoice!

    def updateTimerLabel(self):
        sender = self.sender()

        currentTime = QTime().currentTime()
        if self.designatedTime:
            millis = int(currentTime.msecsTo(self.designatedTime) + 150)
            seconds = (millis / 1000) % 60
            seconds = int(seconds)
            minutes = (millis / (1000 * 60)) % 60
            minutes = int(minutes)
            hours = (millis / (1000 * 60 * 60)) % 24
            new_millis = int(millis % 1000)
            self.timerLabel.setText(
                f"Timer set in place for {self.location} {self.duration} duration {self.selectedDate} at {self.time}. "
                f"Will activate in {int(hours)}:{minutes}:{seconds}:{new_millis}")

    def registerForCourt(self, safe = False):
        print("worked for now!")
        result = None
        if self.loggedIn:
            if self.onPage:
                self.onTime = self.site.validateCourt(self.selectedDate, self.time, self.duration)

                if self.onTime:
                    if safe:
                        self.site.safeClick()
                    else:
                        self.timer = QTimer()
                        final_countdown = int(QTime.currentTime().msecsTo(self.designatedTime) + 150)
                        self.timer.singleShot(final_countdown, self.fastClick)
        # self.resize(270, 110)
        # date = QDate()
    def slowClick(self):
        result = self.site.safeClick()
        self.time = None
        self.location = None
        self.designatedTime = None
        if result:
            self.timerLabel.setText("Successfully booked court! However, I am unsure if there was a charge. Please "
                                    "verify independently.")
            return
        if result is False:
            self.timerLabel.setText("Unable to reserve the court.")
            return

        if result is None:
            self.timerLabel.setText("An unknown issue occured.")
            return

    def fastClick(self):
        result = self.site.hurryConfirm()
        self.time = None
        self.location = None
        self.designatedTime = None
        if result:
            self.timerLabel.setText("Successfully booked court! However, I am unsure if there was a charge. Please "
                                    "verify independently.")
            return
        if result is False:
            self.timerLabel.setText("Unable to reserve the court.")
            return

        if result is None:
            self.timerLabel.setText("An unknown issue occured.")
            return

    def closeEvent(self, event):
        self.site.driver.quit()
        event.accept()
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


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    sys.exit(app.exec())
