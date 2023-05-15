import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager as CM

load_dotenv()


# login bot===================================================================================================


def youtube_login(email, password):
    op = webdriver.ChromeOptions()
    op.add_argument('--disable-dev-shm-usage')
    op.add_argument('--disable-gpu')
    op.add_argument("--disable-infobars")
    op.add_argument("--log-level=3")
    op.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=op, executable_path=CM().install())
    driver.execute_script("document.body.style.zoom='80%'")
    driver.get(
        'https://accounts.google.com/signin/v2/identifier?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
    print("Login successful")

    # finding email field and putting our email on it
    email_field = driver.find_element(By.XPATH, '//*[@id="identifierId"]')
    email_field.send_keys(email)
    driver.find_element(By.ID, "identifierNext").click()
    time.sleep(5)
    print("email - done")

    # finding pass field and putting our pass on it
    find_pass_field = (By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located(find_pass_field))
    pass_field = driver.find_element(*find_pass_field)
    WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable(find_pass_field))
    pass_field.send_keys(password)
    driver.find_element(By.ID, "passwordNext").click()
    time.sleep(5)
    print("password - done")
    WebDriverWait(driver, 200).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "ytd-masthead button#avatar-btn")))
    print("Successfully login")

    return driver


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False

    return True


# running bot------------------------------------------------------------------------------------
if __name__ == '__main__':

    email = os.getenv("USER_EMAIL")
    password = os.getenv("USER_EMAIL_PASSWORD")

    # LOGIN
    driver = youtube_login(email, password)  # checking if we have links or not
    print(driver.current_url)
    time.sleep(2)

    # HEADLINE CHIPS
    chips = driver.find_elements(By.ID, "chips")
    time.sleep(2)
    headlines = [chip.text for chip in chips]

    # ACTUAL RESPONSE DATA
    response_data = {'headlines': headlines,
                     "videos": [],
                     "user_history": [],
                     "subscribed_channels": []}

    # CONTENT DATA
    contents = driver.find_elements(By.ID, "contents")

    for content in contents:
        sub_contents = content.find_elements(By.ID, "contents")

        for data in sub_contents:
            meta_data = data.find_elements(By.ID, "meta")
            for about_data in meta_data:
                data = about_data.text.splitlines()

                try:
                    title = data[0]
                except:
                    title = 'No title'

                try:
                    author_by = data[1]
                except:
                    author_by = 'No author'

                try:
                    views = data[2]
                except:
                    views = 'Views data not found'

                try:
                    time_ago = data[3]
                except:
                    time_ago = 'time data not found'

                # VIDEO DETAILS
                video_data = {
                    'title': title,
                    'author_by': author_by,
                    'views': views,
                    'time_ago': time_ago
                }
                response_data["videos"].append(video_data)

    # CLICK ON GUIDE BUTTON (3 LINES) ---> ID = guide-button
    guide_button_cursor = driver.find_element(By.ID, "guide-button")
    guide_button_cursor.click()
    time.sleep(2)

    # FETCH ALL GUIDE LIST DATA
    guide_list = driver.find_elements(By.CLASS_NAME, "title")
    for sub_guide in guide_list:
        # FIND FOR HISTORY TAG
        if sub_guide.text == "History":
            sub_guide.click()
            time.sleep(2)

            # FOR REASSURANCE THAT WE ARE IN WATCH HISTORY PAGE
            if "Watch history" in driver.page_source:
                print("YESSSSS")
            else:
                print("NOOOOOO")

            # DIVS REGARDING ALL VIDEOS
            video_history = driver.find_elements(By.CLASS_NAME, "style-scope ytd-video-renderer")
            time.sleep(2)
            for video in video_history:
                # FETCH VIDEO TITLE
                video_title = video.find_elements(By.ID, "video-title")
                data = {'title': title.text for title in video_title}

                # FETCH VIDEO'S CHANNEL NAME
                channel_name = video.find_elements(By.ID, "channel-name")
                data["channel_name"] = channel_name[0].text

                # FETCH VIDEO'S DESCRIPTION
                video_description = video.find_elements(By.ID, "description-text")
                data["video_description"] = video_description[0].text

                response_data["user_history"].append(data)


    # print("this is o/p", response_data)

    # SAVE RESPONSE AS OUTPUT DICTIONARY IN JSON FILE
    import datetime

    today_date = datetime.datetime.now()
    filename = f'{today_date}_youtube_data.json'
    import json
    import os

    if os.path.isfile(filename):
        with open(filename, 'wr') as f:
            try:
                json_data = json.load(f)
            except ValueError:
                json_data = []
    else:
        json_data = []

    json_data.append(response_data)

    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=4)
