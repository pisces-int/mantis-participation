import csv
import time
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def get_div_count(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div', class_='action')
    return len(divs)

def login(driver, username, password, base_url):
    driver.get(f'{base_url}/login_page.php')  # Replace "your_login_page_url" with the actual URL
    time.sleep(2)

    # Enter username and click login
    username_input = driver.find_element(By.NAME, "username")  # Replace "username" with the actual name attribute
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # Enter password and click login
    password_input = driver.find_element(By.NAME, "password")  # Replace "password" with the actual name attribute
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(2)

def fetch_data(username, days, base_url, driver):
    url = f'{base_url}/view_user_page.php?username={username}&days={days}'
    driver.get(url)
    time.sleep(2)  # Sleep for 2 seconds to allow the page to load

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

    driver = webdriver.Chrome()  # Update this line with the appropriate webdriver for your browser

    # Log in
    login(driver, login_credentials['username'], login_credentials['password'], base_url)

    with open(input_csv, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        with open(output_csv, 'w', newline='') as outputfile:
            writer = csv.writer(outputfile)
            writer.writerow(header + ['div_count'])

            for row in reader:
                username = row[0]

                total_div_count = 0
                for days in range(0, 70, 7):  # 10 weeks before, shifting by a week each time
                    html_content = fetch_data(username, days, base_url, driver)
                    if html_content is not None:
                        div_count = get_div_count(html_content)
                        total_div_count += div_count

                writer.writerow(row + [total_div_count])

    driver.quit()

if __name__ == "__main__":
    main()
