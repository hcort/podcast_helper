import json

from selenium.webdriver.common.by import By

from get_driver import get_driver, hijack_cookies
from get_episode import create_filename_and_folders
from mp3_tags import write_mp3_tags


def get_episode(driver, episode, output_dir):
    if not episode or not driver:
        return None
    driver.get(episode)
    try:
        podcast_json_data = driver.find_element(By.ID, 'shoebox-media-api-cache-amp-podcasts').get_attribute("innerHTML")
        json_dict = json.loads(podcast_json_data)
        json_dict = json.loads(json_dict[list(json_dict.keys())[0]])
        episode_title = json_dict['d'][0]['attributes']['name']
        episode_autor = json_dict['d'][0]['attributes']['artistName']
        episode_date = json_dict['d'][0]['attributes']['releaseDateTime']
        episode_mp3_url = json_dict['d'][0]['attributes']['assetUrl']
        image_filename = driver.find_element(By.CLASS_NAME, 'we-artwork__image').get_attribute('src')
        requests_session = hijack_cookies(driver)
        redirected = requests_session.get(episode_mp3_url)
        mp3_filename = create_filename_and_folders(output_dir, episode_autor, episode_title) + '.mp3'
        with open(mp3_filename, mode='wb') as localfile:
            localfile.write(redirected.content)
        write_mp3_tags(episode_title, episode_autor, episode_date, image_filename, mp3_filename)
    except Exception as err:
        print(f'{episode} - {driver.title} - {err}')


def get_apple_podcast_episode(output_path, episode_url, recycled_driver=None):
    driver = recycled_driver if recycled_driver else get_driver()
    get_episode(driver=driver, episode=episode_url, output_dir=output_path)
    if not recycled_driver:
        driver.close()