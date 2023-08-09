from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from get_driver import get_driver


def wait_for_cookies(driver, timeout, url):
    try:
        cookie_button_present = expected_conditions.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
        WebDriverWait(driver, timeout).until(cookie_button_present)
        cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        cookie_button.click()
        WebDriverWait(driver, timeout).until_not(cookie_button_present)
    except TimeoutException as ex:
        # cookies already accepted
        print(f'Error clicking cookies button {url} - {ex}')


def initialize_episode_list(prev_page, page_no):
    return {
        'prev_page': prev_page,
        'page_no': page_no,
        'episode_list': [],
        'next_page': ''
    }


def list_episodes(driver=None, start_url='', prev_page='', page_no=1, use_proxy=False):
    # if not base_url or not current_url or not driver:
    if use_proxy:
        return list_episodes_via_proxy(driver, start_url, prev_page)
    if not start_url:
        return None
    episodes_in_page = initialize_episode_list(prev_page, page_no)
    timeout = 5
    driver.get(start_url)
    wait_for_cookies(driver, timeout, start_url)
    try:
        next_page_present = expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple"))
        WebDriverWait(driver, timeout).until(next_page_present)
        all_titles_p = driver.find_elements(By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple")
        all_description_buttons = driver.find_elements(By.CLASS_NAME, "btn.btn-link.info")
        for i, (title, button, short_description) in enumerate(zip(all_titles_p, all_description_buttons)):
            link = title.find_element(By.TAG_NAME, 'a').get_attribute('href')
            button.click()
            element_present = expected_conditions.presence_of_element_located((By.CLASS_NAME, "popover-content"))
            WebDriverWait(driver, timeout).until(element_present)
            description = driver.find_element(By.CLASS_NAME, "popover-content").text
            button.click()
            WebDriverWait(driver, timeout).until_not(element_present)
            episodes_in_page['episode_list'].append({'url': link, 'desc': description})
        next_page_button = driver.find_elements(By.LINK_TEXT, '»')
        episodes_in_page['next_page'] = next_page_button[0].get_attribute('href') if next_page_button else ''
    except TimeoutException as ex:
        print('Error accessing {}: Timeout: {}'.format(driver.current_url, str(ex)))
    return episodes_in_page


def click_link_and_extract_original_url(driver, title):
    timeout = 10
    title.find_element(By.TAG_NAME, 'a').click()
    link_text = ''
    try:
        download_button = expected_conditions.presence_of_element_located((By.ID, "lnk_download"))
        WebDriverWait(driver, timeout).until(download_button)
        input_box = driver.find_elements(By.CLASS_NAME, 'url-input')
        link_text = input_box[0].get_attribute('value') if input_box else ''
    except TimeoutException as ex:
        print('Error accessing {}: Timeout: {}'.format(driver.current_url, str(ex)))
    try:
        driver.execute_script("window.history.go(-1)")
        elemento_lista = expected_conditions.presence_of_element_located((By.CLASS_NAME, "ficha-podcast"))
        WebDriverWait(driver, timeout).until(elemento_lista)
    except TimeoutException as ex:
        print('Error accessing {}: Timeout: {}'.format(driver.current_url, str(ex)))
    return link_text


def click_next_page_button(driver):
    next_page_button = driver.find_elements(By.LINK_TEXT, '»')
    link_text = ''
    timeout = 10
    if next_page_button:
        try:
            next_page_button[0].click()
            download_button = expected_conditions.presence_of_element_located((By.CLASS_NAME, "ficha-podcast"))
            WebDriverWait(driver, timeout).until(download_button)
            input_box = driver.find_elements(By.CLASS_NAME, 'url-input')
            link_text = input_box[0].get_attribute('value') if input_box else ''
        except TimeoutException as ex:
            print('Error accessing {}: Timeout: {}'.format(driver.current_url, str(ex)))
        # i don't need to go back
    return link_text


def list_episodes_via_proxy(driver=None, start_url='', prev_page='', page_no=1):
    if not start_url:
        return None
    episodes_in_page = initialize_episode_list(prev_page, page_no)
    timeout = 5
    proxy_server_option = 'eu15'
    driver.get(f'https://{proxy_server_option}.proxysite.com')
    input_text = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[1]/div/div[3]/form/div[2]/input')
    input_text.send_keys(start_url)
    input_text.send_keys(Keys.RETURN)
    wait_for_cookies(driver=driver, timeout=1, url=start_url)
    try:
        next_page_present = expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple"))
        WebDriverWait(driver, timeout).until(next_page_present)
        all_titles_p = driver.find_elements(By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple")
        all_short_descriptions = driver.find_elements(By.CLASS_NAME, "audio-description")
        number_of_episodes = len(all_titles_p)
        for i in range(number_of_episodes):
            description = all_short_descriptions[i].text
            link = click_link_and_extract_original_url(driver, all_titles_p[i])
            episodes_in_page['episode_list'].append(
                {
                    'url': link,
                    'desc': description
                })
            print(f'{link} - {description}')
            # i need to refresh this because click_link_and_extract_original_url goes to a new url and back again
            # see: StaleElementReferenceException
            all_titles_p = driver.find_elements(By.CLASS_NAME, "title-wrapper.text-ellipsis-multiple")
            all_short_descriptions = driver.find_elements(By.CLASS_NAME, "audio-description")
        episodes_in_page['next_page'] = click_next_page_button(driver)
    except TimeoutException as ex:
        print('Error accessing {}: Timeout: {}'.format(driver.current_url, str(ex)))
    return episodes_in_page


if __name__ == '__main__':
    use_proxy = True
    links = [
        'https://www.ivoox.com/podcast-todo-tranquilo-dunwich_sq_f1281218_1.html'
             ]
    driver = get_driver()
    for link in links:
        episodes_in_page = list_episodes(driver=driver, start_url=link, prev_page='', page_no=1, use_proxy=use_proxy)
    pass
