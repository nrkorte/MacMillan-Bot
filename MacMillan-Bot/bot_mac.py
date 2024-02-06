#!/usr/bin/env python

# Author: Github - nrkorte
#
# Hi there!
# 
# You are welcome to look through my code to see what is going on underneath the hood and improve it if you'd like
# This program is not the most efficient (time-wise or storage-wise) but it gets the job done much faster than a human can
# The main hub that sends requests for completing questions is in mcbegin()
# From there each question type, prompt, and answer is parsed, completed, and stored through individual function calls
#
# Happy hunting!

import sys
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
import json


class mcbot:

    def set_window_position_safely(self, x, y):
        try:
            self.driver.set_window_position(x, y)
        except Exception as e:
            print(f"An error occurred while setting window position: {e}")

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.google.com/")
        self.set_window_position_safely(2000, 0)
        self.driver.maximize_window()
    
    def mcstart(self, user, passw, link):
        time.sleep(3)
        self.driver.get(link)
        WebDriverWait( self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'https://colostate.instructure.com/login/saml')]"))).click()
        WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user)
        WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(passw)
        WebDriverWait( self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@type, 'submit')]"))).click()
        self.driver.get(self.driver.current_url)
        WebDriverWait( self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div[2]/div[3]/div[1]/div/div[3]/form/div/div[1]/div/button"))).click()
        time.sleep(3)

    def mcbegin(self):
        get_into_questions(self)
        time.sleep(2)

        json_file_path = './questions.json'
        count = 0
        while True:
            count += 1
            tmp = parse_prompt(WebDriverWait (self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h2[contains(@data-test-id, 'activityQuestion')]"))).text)
            solve_multiple_choice_question(self, json_file_path, tmp, count)


def solve_multiple_choice_question(self, json_file_path, prompt_in_question, num_question):
    questions_dict = load_questions(json_file_path)

    if prompt_in_question in questions_dict:
        # print(f"{num_question}: Found a question we've seen before!")
        try:
            answer_text = questions_dict[prompt_in_question]
            print (answer_text)
            answer_element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{answer_text}')]"))
            )
            
            self.driver.execute_script("arguments[0].scrollIntoView();", answer_element)
            time.sleep(0.5)

            answer_element.click()

            WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-test-id, 'submitAnswerBtn')]"))).click()
            time.sleep(0.5)
            click_element(self.driver, "//button[contains(@data-test-id, 'nextQuestionBtn')]")
            
        except TimeoutException:
            print("Duplicate Prompt Found")
            del questions_dict[prompt_in_question]
            save_questions(json_file_path, questions_dict)
        except ElementClickInterceptedException:
            print("Click intercepted")
            # print(end="")
        except StaleElementReferenceException:
            print("Stale element encountered. Retrying...")
            # print(end="")

    if prompt_in_question not in questions_dict:
        choices_elements = WebDriverWait(self.driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'MultipleChoice__answerText__ruHtC')]"))
        )

        for index, choice_element in enumerate(choices_elements, start=1):
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                choice_element.click()

                click_element(self.driver, "//button[contains(@data-test-id, 'submitAnswerBtn')]")
                time.sleep(0.5)

                click_element(self.driver, "//button[contains(@data-test-id, 'slowDownModalOkBtn')]")

                try:
                    correct_answer_xpath = "//h2[contains(@data-test-id, 'correctAnswerSuccessModal')]"
                    answer = WebDriverWait(self.driver, .5).until(EC.element_to_be_clickable((By.XPATH, correct_answer_xpath))).text
                    questions_dict[prompt_in_question] = answer
                    save_questions(json_file_path, questions_dict)
                except TimeoutException:
                    # print('Could not find answer')
                    print(end="")

                click_element(self.driver, "//button[contains(@data-test-id, 'nextQuestionBtn')]")

            except TimeoutException:
                # print(f"Could not click one of the answers")
                print(end="")
            except ElementClickInterceptedException:
                # print ('click intercepted')
                print(end="")
            except StaleElementReferenceException:
                # print('Stale element encountered. Retrying...')
                print(end="")
                
                choices_elements = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'MultipleChoice__answerText__ruHtC')]"))
                )

                index -= 1

def click_element(driver, xpath):
    try:
        element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return True
    except TimeoutException:
        print(f"Could not find or click the element: {xpath}")
        # print(end="")
        return False

def load_questions(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_questions(file_path, questions_dict):
    with open(file_path, 'w') as file:
        json.dump(questions_dict, file, indent=2)

def get_into_questions(self):
    time.sleep(3)
    try:
        self.driver.switch_to.window(self.driver.window_handles[1])
    except:
        print ("You recieved an error because the software attempted to switch to a new window handle without one present. Please restart your program and try again.")
    try:
        WebDriverWait( self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-test-id, 'beginActivityBtn')]"))).click()
    except TimeoutException:
        try:
            WebDriverWait( self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-test-id, 'beginActivityBtn')]"))).click()
        except:
            print(end='Could not find Begin button')
        print(end="Failed to find Resume button")
        

# def get_around_forced_learning(self, prompt_in_question):
#     try:
#         WebDriverWait( self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'review a resource')]"))).click()
#         WebDriverWait( self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Read About the Concept')]"))).click()
#         WebDriverWait( self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'To Questions')]"))).click()
#     except TimeoutException:
#         print(end="")

def parse_prompt(prompt_unsplit):
    prompt = prompt_unsplit.split("\n")
    for var in prompt:
        if "Blank" in var or "prompt_array" in var:
            prompt.remove(var)
    ret_str = ""
    for f in prompt:
        ret_str += f
    ret_str = re.sub(r'[\W_]', '', ret_str)
    return ret_str

def parse_answer(answer):
    while answer.find("Blank") != -1:
        start = answer.find("Blank")
        inner = 0
        while inner < 9:
            inner += 1
            answer = answer[:start] + answer[start + 1:]
        if answer.find(",") != -1:
            answer = answer[:answer.find(",")]
        if answer.find(" or") != -1:
            answer = answer[:answer.find(" or")]
    return answer

# def parse_mc_choice_answer(ans):
#     return re.sub(r'[\W_]', '', ans)

if __name__ == "__main__":
# arguments in order : username, password, link to hw
    # print("Python version: ", sys.version)
    if (len(sys.argv) != 4):
        raise Exception("Wrong number of program arguments: found ", len(sys.argv) ," needed 3 additional. Exiting now...")
    bot = mcbot()
    bot.mcstart(sys.argv[1], sys.argv[2], sys.argv[3])
    bot.mcbegin()