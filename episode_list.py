from curses.ascii import isdigit

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def wait_for_cookies(driver, timeout):
    cookie_button_present = EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
    WebDriverWait(driver, timeout).until(cookie_button_present)
    cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
    cookie_button.click()
    WebDriverWait(driver, timeout).until_not(cookie_button_present)


def list_episodes(driver=None, base_url='', current_url='', prev_page='', page_no=1):
    if not base_url or not current_url or not driver:
        return None
    episodes_in_page = {
        'prev_page': prev_page,
        'page_no': page_no,
        'episode_list': [],
        'next_page': ''
    }
    timeout = 100
    try:
        driver.get(f'{base_url}/{current_url}')
        wait_for_cookies(driver, timeout)
        next_page_present = EC.presence_of_element_located((By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple"))
        WebDriverWait(driver, timeout).until(next_page_present)
        # didomi-notice-agree-button
        all_titles_p = driver.find_elements(By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple")
        all_description_buttons = driver.find_elements(By.CLASS_NAME, "btn.btn-link.info")
        # all_descriptions = driver.find_elements(By.CLASS_NAME, "popover-content")
        for i, (title, button) in enumerate(zip(all_titles_p, all_description_buttons)):
            link = title.find_element(By.TAG_NAME, 'a').get_attribute('href')
            button.click()
            element_present = EC.presence_of_element_located((By.CLASS_NAME, "popover-content"))
            description = driver.find_element(By.CLASS_NAME, "popover-content").text
            WebDriverWait(driver, timeout).until(element_present)
            episodes_in_page['episode_list'].append(
                {
                    'url': link,
                    'desc': description
                })
            button.click()
            WebDriverWait(driver, timeout).until_not(element_present)
        next_page_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[4]/div/nav/ul/li[6]/a')
        episodes_in_page['next_page'] = next_page_button.get_attribute('href') if next_page_button else ''
    except TimeoutException as ex:
        print('Error accessing {}: Timeout: {}'.format(current_url, str(ex)))
    finally:
        pass
    return episodes_in_page
