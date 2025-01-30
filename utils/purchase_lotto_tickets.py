#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""

__author__ = '__L1n__w@tch'

import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display
from utils.common import logger

lotto_user = os.getenv("LOTTO_USER")
lotto_password = os.getenv("LOTTO_PASSWORD")

chromedriver_path = "/usr/bin/chromedriver"  # Chromium WebDriver path
binary_location = "/usr/bin/chromium-browser"  # Chromium browser binary

XPATH_MAP = {
    "policy": "/html/body/div[1]/div/div/div/div/div/div[3]/button[2]",
    "login": "/html/body/header/header[2]/section[1]/div/div/div/a[1]",
    "username": "/html/body/main/section/div/div/div/div/div/form/div[1]/div/div/div/input",
    "next": "/html/body/main/section/div/div/div/div/div/form/div[2]/button",
    "password": "/html/body/main/section/div/div/div/form/div[1]/div/div[2]/div/input",
    "submit_login": "/html/body/main/section/div/div/div/form/div[2]/button",
    "login_option": "/html/body/main/section/div/div/div/div/form[2]/button",
    "buy_ticket": "/html/body/div[2]/div[2]/section/div[2]/div[2]/div[2]/div[1]/div/section/form/section/ul/li[1]/a",
    "choose_number": "/html/body/div[2]/div[2]/div/section[3]/form/section[11]/div/div/div/div/div/button[1]",
    "finish_choose_number": "/html/body/div[2]/div[2]/div/section[3]/form/section[11]/div/div/div/div[2]/div[2]/button[2]",
    "no_extra": "/html/body/div[2]/div[2]/div/section[3]/form/aside/section[1]/div/div[3]/span/select/option[2]",
    "buying_confirm": "/html/body/div[2]/div[2]/div/section[3]/form/aside/section[5]/button",
    "order": "/html/body/div[2]/div[2]/div/section[3]/form/aside/section[6]/button",
    "upcoming_draw": "/html/body/div[2]/div[2]/div/section[3]/a[2]",
    "see_my_ticket": "/html/body/div[2]/div[2]/div/section[3]/section[3]/div[2]/a/span",
    "ticket_number": "/html/body/div[2]/div[2]/div/section[3]/section[1]/div/div[3]/div/div/div[6]/div[2]/div/span"
}

for i in range(1, 50):
    XPATH_MAP[
        str(i)] = f"/html/body/div[2]/div[2]/div/section[3]/form/section[11]/div/div/div/div[2]/div[3]/span/span[{i}]"


def wait_and_click(driver, xpath, button_name="", error_ignore=False):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        logger.info(f"[{button_name}] button found!")
        button.click()
        logger.info(f"[{button_name}] button clicked!")
    except Exception as e:
        if not error_ignore:
            raise e


def wait_and_input(driver, xpath, input_text, button_name=""):
    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    logger.info(f"[{button_name}] input box found!")
    input_box.send_keys(input_text)
    logger.info(f"[{button_name}] input box input: {input_text}!")


def wait_and_read(driver, xpath, button_name=""):
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    logger.info(f"[{button_name}] button found!")
    return button.text


def do_buying(number):
    """
    :param number: str, like "01,02,03,04,05,06"
    :return:
    """
    global lotto_user, lotto_password, XPATH_MAP, chromedriver_path, binary_location
    logger.info(f"Start to buy lotto: {number}")

    # Start a virtual display
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    # Set Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = binary_location  # Use Chromium binary

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.get("https://portail.lotoquebec.com/en/home")

    logger.info(f"Google Chrome Open Website-Title: {driver.title}")
    try:
        wait_and_click(driver, XPATH_MAP["policy"], "Policy", error_ignore=True)
        wait_and_click(driver, XPATH_MAP["login"], "Login")
        wait_and_input(driver, XPATH_MAP["username"], lotto_user, "username")
        wait_and_click(driver, XPATH_MAP["next"], "next")
        wait_and_input(driver, XPATH_MAP["password"], lotto_password, "password")
        wait_and_click(driver, XPATH_MAP["submit_login"], "submit_login")
        wait_and_click(driver, XPATH_MAP["login_option"], "login_option")
        driver.get("https://loteries.espacejeux.com/en/lotteries/lotto-6-49")
        wait_and_click(driver, XPATH_MAP["buy_ticket"], "buy_ticket")
        wait_and_click(driver, XPATH_MAP["choose_number"], "choose_number")
        for each_number in number.split("-"):
            wait_and_click(driver, XPATH_MAP[each_number], each_number)
        wait_and_click(driver, XPATH_MAP["finish_choose_number"], "finish_choose_number")
        wait_and_click(driver, XPATH_MAP["no_extra"], "no_extra")
        # wait_and_click(driver, XPATH_MAP["buying_confirm"], "buying_confirm") #TODO: wait for next week
        # wait_and_click(driver, XPATH_MAP["order"], "order") #TODO: wait for next week
        driver.get("https://loteries.espacejeux.com/lel/en/my-purchases")
        wait_and_click(driver, XPATH_MAP["upcoming_draw"], "upcoming_draw")
        time.sleep(10)  # sleep 10s
        wait_and_click(driver, XPATH_MAP["see_my_ticket"], "see_my_ticket")
        ticket_number = wait_and_read(driver, XPATH_MAP["ticket_number"], "ticket_number")
        logger.info(f"Ticket number: {ticket_number}")
        driver.save_screenshot("ticket.png")
    except Exception as e:
        logger.error(traceback.format_exc())
        driver.save_screenshot("temp.png")

    # Close everything
    driver.quit()
    display.stop()


if __name__ == "__main__":
    do_buying("12-15-21-28-37-44")
