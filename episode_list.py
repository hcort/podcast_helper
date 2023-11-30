"""
    List episode from the home page of a podcast

"""
# from selenium.common import TimeoutException
# from selenium.webdriver import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from get_driver import get_driver


def wait_for_cookies(webdriver_waiting_for_cookies, timeout, url):
    try:
        cookie_button_present = expected_conditions.presence_of_element_located((By.ID, 'didomi-notice-agree-button'))
        WebDriverWait(webdriver_waiting_for_cookies, timeout).until(cookie_button_present)
        cookie_button = webdriver_waiting_for_cookies.find_element(By.ID, 'didomi-notice-agree-button')
        cookie_button.click()
        WebDriverWait(webdriver_waiting_for_cookies, timeout).until_not(cookie_button_present)
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


def list_episodes(webdriver=None, start_url=None, prev_page='', page_no=1, use_web_proxy=False):
    if (not webdriver) or (not start_url):
        return None
    # if not base_url or not current_url or not webdriver:
    if use_web_proxy:
        return list_episodes_via_proxy(webdriver, start_url, prev_page)
    if not start_url:
        return None
    episodes_in_page = initialize_episode_list(prev_page, page_no)
    timeout = 5
    webdriver.get(start_url)
    wait_for_cookies(webdriver, timeout, start_url)
    try:
        next_page_present = expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, 'title-wrapper.text-ellipsis-multiple'))
        WebDriverWait(webdriver, timeout).until(next_page_present)
        all_titles_p = webdriver.find_elements(By.CLASS_NAME, 'title-wrapper.text-ellipsis-multiple')
        all_description_buttons = webdriver.find_elements(By.CLASS_NAME, 'btn.btn-link.info')
        for (title, button) in zip(all_titles_p, all_description_buttons):
            episode_url = title.find_element(By.TAG_NAME, 'a').get_attribute('href')
            button.click()
            element_present = expected_conditions.presence_of_element_located((By.CLASS_NAME, 'popover-content'))
            WebDriverWait(webdriver, timeout).until(element_present)
            description = webdriver.find_element(By.CLASS_NAME, 'popover-content').text
            button.click()
            WebDriverWait(webdriver, timeout).until_not(element_present)
            episodes_in_page['episode_list'].append({'url': episode_url, 'desc': description})
        next_page_button = webdriver.find_elements(By.LINK_TEXT, '»')
        episodes_in_page['next_page'] = next_page_button[0].get_attribute('href') if next_page_button else ''
    except TimeoutException as ex:
        print(f'Error accessing {webdriver.current_url}: Timeout: {str(ex)}')
    return episodes_in_page


def click_link_and_extract_original_url(webdriver, title):
    timeout = 10
    title.find_element(By.TAG_NAME, 'a').click()
    link_text = ''
    try:
        download_button = expected_conditions.presence_of_element_located((By.ID, 'lnk_download'))
        WebDriverWait(webdriver, timeout).until(download_button)
        input_box = webdriver.find_elements(By.CLASS_NAME, 'url-input')
        link_text = input_box[0].get_attribute('value') if input_box else ''
    except TimeoutException as ex:
        print(f'Error accessing {webdriver.current_url}: Timeout: {str(ex)}')
    try:
        webdriver.execute_script('window.history.go(-1)')
        elemento_lista = expected_conditions.presence_of_element_located((By.CLASS_NAME, 'ficha-podcast'))
        WebDriverWait(webdriver, timeout).until(elemento_lista)
    except TimeoutException as ex:
        print(f'Error accessing {webdriver.current_url}: Timeout: {str(ex)}')
    return link_text


def click_next_page_button(webdriver):
    next_page_button = webdriver.find_elements(By.LINK_TEXT, '»')
    link_text = ''
    timeout = 10
    if next_page_button:
        try:
            next_page_button[0].click()
            download_button = expected_conditions.presence_of_element_located((By.CLASS_NAME, 'ficha-podcast'))
            WebDriverWait(webdriver, timeout).until(download_button)
            input_box = webdriver.find_elements(By.CLASS_NAME, 'url-input')
            link_text = input_box[0].get_attribute('value') if input_box else ''
        except TimeoutException as ex:
            print(f'Error accessing {webdriver.current_url}: Timeout: {str(ex)}')
        # i don't need to go back
    return link_text


def list_episodes_via_proxy(webdriver=None, start_url='', prev_page='', page_no=1):
    if not start_url:
        return None
    episodes_in_page = initialize_episode_list(prev_page, page_no)
    timeout = 5
    proxy_server_option = 'eu15'
    webdriver.get(f'https://{proxy_server_option}.proxysite.com')
    input_text = webdriver.find_element(By.XPATH, '/html/body/div[2]/main/div[1]/div/div[3]/form/div[2]/input')
    input_text.send_keys(start_url)
    input_text.send_keys(Keys.RETURN)
    wait_for_cookies(webdriver_waiting_for_cookies=webdriver, timeout=1, url=start_url)
    try:
        next_page_present = expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, 'title-wrapper.text-ellipsis-multiple'))
        WebDriverWait(webdriver, timeout).until(next_page_present)
        all_titles_p = webdriver.find_elements(By.CLASS_NAME, 'title-wrapper.text-ellipsis-multiple')
        all_short_descriptions = webdriver.find_elements(By.CLASS_NAME, 'audio-description')
        number_of_episodes = len(all_titles_p)
        for i in range(number_of_episodes):
            description = all_short_descriptions[i].text
            episode_url = click_link_and_extract_original_url(webdriver, all_titles_p[i])
            episodes_in_page['episode_list'].append(
                {
                    'url': episode_url,
                    'desc': description
                })
            print(f'{episode_url} - {description}')
            # i need to refresh this because click_link_and_extract_original_url goes to a new url and back again
            # see: StaleElementReferenceException
            all_titles_p = webdriver.find_elements(By.CLASS_NAME, 'title-wrapper.text-ellipsis-multiple')
            all_short_descriptions = webdriver.find_elements(By.CLASS_NAME, 'audio-description')
        episodes_in_page['next_page'] = click_next_page_button(webdriver)
    except TimeoutException as ex:
        print(f'Error accessing {webdriver.current_url}: Timeout: {str(ex)}')
    return episodes_in_page


def get_ivoox_episode_list(recycled_driver, podcast_url, use_web_proxy=False):
    webdriver = recycled_driver if recycled_driver else get_driver()
    episodes_in_page = list_episodes(webdriver=webdriver,
                                     start_url=podcast_url, prev_page='', page_no=1, use_web_proxy=use_web_proxy)
    if not recycled_driver:
        webdriver.close()
    return episodes_in_page


if __name__ == '__main__':
    use_proxy = False
    links = [
        'https://www.ivoox.com/podcast-enano-blanco-30_sq_f11879935_1.html'
             ]
    episode_list_driver = get_driver()
    for link in links:
        episodes_found = list_episodes(
            webdriver=episode_list_driver, start_url=link, prev_page='', page_no=1, use_web_proxy=use_proxy)
    pass
