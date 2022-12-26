from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cred_bank import CredentialBank


class AutoReserveCourt:
    def __init__(self):
        self.driver = webdriver.Chrome()
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
            # self.driver.quit()
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
                reserveWait = WebDriverWait(self.driver, 3).until(
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
        self.driver.refresh() #important to fix the race condition getting stale elements (grabs old times-to-reserve)
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
                print("should return none")
                return None, None

            allTimes = timeTableWait.find_elements(By.TAG_NAME, "a")
            eastTimes = []
            westTimes = []
            print("did not fail yet")
            for ele in allTimes:
                attributePosition = ele.get_attribute("l")
                if int(attributePosition) == 1:
                    eastVal = ele.get_attribute("innerHTML")
                    if isinstance(eastVal, str):
                        eastTimes.append(''.join(eastVal.split()))
                else:
                    westVal = ele.get_attribute("innerHTML")
                    if isinstance(westVal, str):
                        westTimes.append(''.join(westVal.split()))
            print("is returning")
        return eastTimes, westTimes

    def hurryConfirm(self):
        confirmButton = self.driver.find_element(By.ID, "confirm")

        if confirmButton:
            confirmButton.click()
            return True

        return False
    def safeClick(self):
        invoiceLocator = self.driver.find_element(By.CLASS_NAME, "userbox")
        invoices = invoiceLocator.find_elements(By.CLASS_NAME, "label")

        for label in invoices:
            if label.get_attribute("innerHTML") != "No Fee":
                return False

        confirmButton = self.driver.find_element(By.ID, "confirm")

        if confirmButton:
            confirmButton.click()
            return True
        return False

    def validateCourt(self, date, time, duration):
        attempts = 0
        # while attempts < self.maxAttempts:
        dateSelector = self.driver.find_element(By.ID, "date")
        dateSelector.clear()
        dateSelector.send_keys(date)
        dateSelector.click()
        durationSelector = None
        try:
            interval = "interval-" + duration
            durationSelector = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.ID, interval)))

        except:
            pass

        finally:
            print(durationSelector)

        self.driver.implicitly_wait(1)
        randomElement = self.driver.find_element(By.CLASS_NAME, "r-line")
        randomElement.click()  # just to get off calendar page
        print("off search")
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
            print("found time!")
            searchWait.click()
        return True
    def login(self, username, password):
        self.driver.get('https://cpac.clubautomation.com/')
        usernameField = self.driver.find_element(By.ID, "login")
        passwordField = self.driver.find_element(By.ID, "password")
        loginButton = self.driver.find_element(By.ID, "loginButton")
        usernameField.send_keys(username)
        passwordField.send_keys(password)
        loginButton.click()

