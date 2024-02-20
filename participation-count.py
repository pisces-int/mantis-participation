import csv
import copy
import time
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def login(driver, username, password, base_url):
    driver.get(f'{base_url}/login_page.php')
    time.sleep(2)

    username_input = driver.find_element(By.NAME, "username")
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)
    time.sleep(2)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(2)

def fetch_data(days, base_url, driver):
    url = f'{base_url}/my_view_page.php?days={days}&all=1'
    driver.get(url)
    time.sleep(2)

    html_content = driver.page_source
    return html_content

def read_settings():
    with open('settings.yaml', 'r') as yamlfile:
        settings = yaml.safe_load(yamlfile)
        return settings

def main():
    settings = read_settings()
    input_csv = settings['input_csv']
    output_csv = settings['output_csv']
    base_url = settings['base_url']
    login_credentials = settings['login_credentials']
    weeks = settings["weeks"]

    driver = webdriver.Chrome()

    login(driver, login_credentials['username'], login_credentials['password'], base_url)

    with open(input_csv, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        usernames = {}
        for username_row in reader:
            usernames[username_row[0]] = 0

        with open(output_csv, 'w', newline='') as outputfile:
            writer = csv.writer(outputfile)
            writer.writerow(header + ['count'])

            for days in range(0, 7*weeks, 7):
                html_content = fetch_data(days, base_url, driver)
                soup = BeautifulSoup(html_content, 'html.parser')
                text_without_tags = soup.get_text()

                for username in usernames:
                    patterns = [
                        "created issue"
                        f"{username} created issue",
                        f"{username} commented on issue",
                    ]

                    # Loop through each string in the HTML and count occurrences
                    for pattern in patterns:
                        usernames[username] += text_without_tags.count(pattern)
            
            for username in usernames:
                writer.writerow([username,usernames.get(username, 0)/weeks])

    driver.quit()

if __name__ == "__main__":
    main()
