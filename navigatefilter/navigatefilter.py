from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
import time

path = r"/Users/reidrelatores/PycharmProjects/farmers/chromedriver"
logging.basicConfig(level=logging.INFO)

def initialize_filter():
    driver = start_chrome()
    navigate(driver)
    driver.quit()

def start_chrome():
    # Initialize Selenium
    options = webdriver.ChromeOptions()
    #options.add_experimental_option("detach", True)
    #options.add_argument('--incognito')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--log-level=3")
    options.add_argument('--ignore-ssl-errors')
    chrome_driver_path = path
    driver = webdriver.Chrome(chrome_driver_path, options=options)
    driver.get("https://www.zillow.com/homes/")
    return driver

def navigate(driver):
    actions = {
        "for_sale": "okta-signin-submit",
    }

    for action, val in actions.items():
        time.sleep(.5)
        logging.info(action)
        if action == 'for_sale':
            driver.find_element(By.ID, "listing-type").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[1]/button").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[2]/div[1]/ul/li[3]/div/div/input").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[2]/div[1]/ul/li[4]/div/div/input").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[2]/div[1]/ul/li[5]/div/div/input").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[2]/div[1]/ul/li[6]/div/div/input").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[2]/div[3]/ul/li[1]/div/div/input").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/section/div[2]/div/div[1]/div/div/form/fieldset/div[1]/div[2]/div[3]/ul/li[2]/div/div/input").click()
            driver.find_element(By.ID, "more").click()
            driver.find_element(By.ID, "doz").click()
            driver.find_element(By.ID, "doz").click()
            driver.find_element(By.XPATH, "//*[@id='doz']/option[2]").click()
            driver.find_element(By.ID, "more").click()
