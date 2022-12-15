from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cred_bank import CredentialBank


class AutoReserveCourt:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.maxAttempts = 3
        self.durationIndexMap = {"30": 0, "60": 1, "90": 2, "120":3}
    def checkLogin(self, username, password):
        self.login(username, password)
        element = None
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "profile"))
            )

        finally:
            self.driver.quit()
            if element is None:
                return False

            return True

    def formalLogin(self, username, password):
        attempts = 0
        flag = False
        element = None
        while attempts < self.maxAttempts:
            self.login(username, password)
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "profile"))
                )
            except:
                self.driver.quit()
                return False
            finally:
                if element is None:
                    self.driver.quit()
                else:
                    flag = True
                    break
            attempts += 1
        return flag

    def goToReserveCourt(self):
        attempts = 0
        while attempts < self.maxAttempts:
            reserveCourt = self.driver.find_element(By.ID, "menu_reserve_a_court")
            reserveCourt.click()
            reserveWait = None
            try:
                reserveWait = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "reserve-court-new"))
                )
            except:
                self.driver.quit()
                return False
            finally:
                if reserveWait is not None:
                    return True
                    break

            attempts += 1
        return False

    def populateAvailableTimes(self, date, duration):
        dateSelector = self.driver.find_element(By.ID, "date")
        dateSelector.clear()
        dateSelector.send_keys(date)
        dateSelector.click()
        timeTableWait = None
        if (duration != "60"):
            durationSelector = self.driver.find_element(By.CLASS_NAME, "l-block")
            durationSpans = durationSelector.find_elements(By.TAG_NAME, "span")
            durationSpans[self.durationIndexMap[duration]].click()

        randomElement = self.driver.find_element(By.CLASS_NAME, "r-line")
        randomElement.click()  # just to get off calendar page

        self.driver.implicitly_wait(1)
        searchButton = self.driver.find_element(By.ID, "reserve-court-search")
        searchButton.click()
        try:
            timeTableWait = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "times-to-reserve"))
            )
        except:
            return None
        finally:
            if timeTableWait is None:
                return None

            allTimes = timeTableWait.find_elements(By.TAG_NAME, "a")
            eastTimes = []
            westTimes = []
            for ele in allTimes:
                if int(ele.get_attribute("l")) == 6:
                    eastTimes.append(''.join(ele.get_attribute("innerHTML").split()))
                else:
                    westTimes.append(''.join(ele.get_attribute("innerHTML").split()))
        return eastTimes, westTimes

    def validateCourt(self, date, time, duration):
        attempts = 0
        # while attempts < self.maxAttempts:
        dateSelector = self.driver.find_element(By.ID, "date")
        dateSelector.clear()
        dateSelector.send_keys("12/15/2022")
        dateSelector.click()

        if (duration != "60"):
            interval = "interval-" + duration
            durationSelector = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, interval)))
            durationSelector.click()

        self.driver.implicitly_wait(1)
        randomElement = self.driver.find_element(By.CLASS_NAME, "r-line")
        randomElement.click()  # just to get off calendar page

        searchButton = self.driver.find_element(By.ID, "reserve-court-search")
        searchButton.click()
        searchWait = None
        try:
            searchWait = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, time))
            )
        except:
            return False
        finally:
            if (searchWait is None):
                return False

            searchWait.click()

    def login(self, username, password):
        self.driver.get('https://cpac.clubautomation.com/event/reserve-court-new')
        usernameField = self.driver.find_element(By.ID, "login")
        passwordField = self.driver.find_element(By.ID, "password")
        loginButton = self.driver.find_element(By.ID, "loginButton")
        usernameField.send_keys(username)
        passwordField.send_keys(password)
        loginButton.click()

