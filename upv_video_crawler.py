"""
    Downloads videos from the UPV/EHU website

    A series of videos has an URL like this one:
    https://ehutb.ehu.eus/series/5cb5e3d3f82b2bcf598b464b
    Serie: V International Conference on the Inklings and the Western Imagination: From the Past to the Future



"""
import os
from urllib.parse import urlparse
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from slugify import slugify

from get_driver import get_driver
from get_substack_audio import download_file
from mp3_tags import mp4_to_mp3, write_id3_tags_dict


def get_video_subtitle(video_element):
    all_subs = video_element.parent.parent.select('div.subtitle')
    return all_subs[0].text.strip(), all_subs[1].text.strip() if (len(all_subs) > 1) else ''


def get_video_id(video_element):
    video_link = video_element.parent.parent.select_one('ul>div>a')
    video_url = video_link.get('href', '')
    # <a href="https://ehutb.ehu.eus/video/5cb6bc46f82b2bd4598b46a8?track_id=5cb6bde2f82b2b05198b4567">
    return video_url.split('=')[1]


def parse_index(index_url, output_path):
    """
        Lee todos los enlaces de una serie.
        Por cada vídeo descarga el fichero mp4, lo convierte a mp3 y añade tag de título

        Al procesar la lista obtenemos todos los datos necesarios y no tenemos que navegar a
        las entradas individuales de cada vídeo

    :param index_url: índice de la serie de vídeos
    :param output_path: donde almaceno los vídeos
    """
    all_video_urls = []
    next_url = index_url
    url_parsed = urlparse(index_url)
    serie_title = ''
    while next_url:
        try:
            response = requests.get(next_url)
            if not response.ok:
                print(f'Error getting index: {next_url}')
                break
            soup = BeautifulSoup(response.text, features="html.parser")
            if not serie_title:
                serie_title = soup.select_one('h1.title-for-crumbs').text[7:]
            all_video_urls += soup.select('div.title>a')
            next_button = soup.select_one('a[rel="next"]')
            next_page = next_button.get('href', '') if next_button else ''
            next_url = f'{url_parsed.scheme}://{url_parsed.netloc}{next_page}' if next_page else ''
        except Exception as err:
            print(f'Error getting index: {next_url} - Exception: {err}')
            next_url = ''
    for video_link in all_video_urls:
        # video link is a <a...> node in the soup.
        video_id = get_video_id(video_link)
        [video_date, video_author] = get_video_subtitle(video_link)
        mp4_url = f'https://ehutb.ehu.eus/trackfile/{video_id}.mp4'
        video_name = slugify(video_link.text.strip())
        video_title = video_link.select_one('div.title>span>strong').text
        tag_dict = {
            'artist': serie_title,
            'album': f'Podcast {serie_title}',
            'title': f'{video_author} - {video_title}',
            'date': video_date,
            'website': index_url,
            'genre': 'Podcast'
        }
        mp4_filename = slugify(f"{serie_title} - {tag_dict['title']}")
        full_mp4_filename = download_file(output_path, mp4_url, mp4_filename + '.mp4', show_progress=False)
        mp3_filename = mp4_to_mp3(output_path, mp4_filename, delete_mp4=True)
        write_id3_tags_dict(mp3_filename=mp3_filename, art_filename=None, tag_dict=tag_dict)


def get_upv_episode(output_path, episode_link):
    """
    Buscar
        Url del episodio: https://ehutb.ehu.eus/video/5cb5e3d3f82b2bcf598b464c

        El reproductor está en un contenedor iframe, aquí no puedo resolverlo con BeautifulSoup

        <video id="playerContainer_videoContainer_master"
            style="width: 100%;
            height: 100%;"
            preload="metadata"
            playsinline=""
            poster="https://ehutb.ehu.eus/uploads/pic/5cb5e3d3f82b2bcf598b464b/bannerInklings.png">

            <source src="https://ehutb.ehu.eus/trackfile/5cb5e9d4f82b2bb7048b4567.mp4" type="video/mp4">
        </video>
    """
    driver = get_driver()
    try:
        driver.get(episode_link)
        timeout = 50
        title = driver.find_element(By.CLASS_NAME, 'mmobj-title').text.strip()
        series = driver.find_element(By.CSS_SELECTOR, 'div.col-xs-12>div>strong>a').text.strip()
        author = driver.find_element(By.CSS_SELECTOR, 'div.col-xs-12>h1.title-for-crumbs').text.strip()
        date = driver.find_element(By.CSS_SELECTOR, 'div.col-xs-12>div.date').text.strip()
        if date:
            date = date[-10:]
        tag_dict = {
            'artist': series,
            'album': f'Podcast {series}',
            'title': f'{author} - {title}',
            'date': date,
            'website': episode_link,
            'genre': 'Podcast'
        }
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, "paellaiframe")))
        driver.switch_to.frame("paellaiframe")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#masterVideoWrapper>video>source')))
        video = driver.find_element(By.CSS_SELECTOR, 'div#masterVideoWrapper>video>source').get_attribute('src')
        mp4_filename = slugify(f"{series} - {tag_dict['title']}")
        download_file(output_path, video, mp4_filename + '.mp4')
        mp3_filename = mp4_to_mp3(path=output_path, mp4_name=mp4_filename)
        write_id3_tags_dict(mp3_filename=mp3_filename, art_filename=None, tag_dict=tag_dict)
    except Exception as ex:
        print(f'Error loading {episode_link} - {ex}')
    finally:
        driver.close()
    pass


# Lanzamos la función principal
if __name__ == "__main__":
    all_series_url = [
        'https://ehutb.ehu.eus/series/58c66f50f82b2b70058b456b',    # I International Conference on the Inklings: Fantasy and National Discourse
        'https://ehutb.ehu.eus/series/58c671d4f82b2bf7228b456b',    # II International conference on the inklings
        'https://ehutb.ehu.eus/series/58fa2ed7f82b2bbd1a8b469e',    # III International Conference on the Inklings
        'https://ehutb.ehu.eus/series/5ae1f9e0f82b2b1e738b48e4',    # IV International Conference on the Inklings: War and Peace in the Works of the Inklings
        'https://ehutb.ehu.eus/series/5cb5e3d3f82b2bcf598b464b',    # V International Conference on the Inklings and the Western Imagination: From the Past to the Future
        'https://ehutb.ehu.eus/series/5f75e4eaf82b2bbf1a8b4599',    # VI International Conference on the Inklings and the Western Imagination
        'https://ehutb.ehu.eus/series/60746606f82b2b2b2a8b4ffc',    # VII International Conference on the Inklings and the Western Imagination
    ]
    mp3_path = './output/'
    for serie in all_series_url:
        parse_index(serie, mp3_path)
    print('done')

