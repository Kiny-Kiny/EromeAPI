import requests
import re
from bs4 import BeautifulSoup

class Api:
  def __init__(self):
    self.__session = requests.session()
    self.__headers = {
      "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
      "sec-ch-ua-mobile": "?1",
      "sec-ch-ua-platform": '"Android"',
      "upgrade-insecure-requests": "1",
      "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
      "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "sec-fetch-site": "cross-site",
      "sec-fetch-mode": "navigate",
      "sec-fetch-user": "?1",
      "sec-fetch-dest": "document",
      "referer": "https://www.google.com/",
      "accept-encoding": "gzip, deflate, br, zstd",
      "accept-language": "en-US,en;q=0.9",
    }
    self.__media_pattern = r'https?:\/\/([sv]\d+\.erome\.com)(\/[^\s]*)?(\?[^#\s]*)?'
    self.__version_list = ["all", "straight", "trans", "gay", "hentai"]

  def __get_album_data(self, page, keyword="", new=None):
    if not keyword:
      url = f"https://www.erome.com/explore/new?page={page}" if new else f"https://www.erome.com/explore?page={page}"

    else:
      url = f"https://www.erome.com/search?q={keyword}&page={page}"

    response = self.__session.get(url, headers=self.__headers)
    content = []

    if 200 <= response.status_code <= 207:
      soup = BeautifulSoup(response.text, 'html.parser')
      albums_div = soup.find('div', id='albums')

      if albums_div:
        album_links = albums_div.find_all('a', class_='album-link')
        album_thumbs = albums_div.find_all('img', class_='album-thumbnail')
        album_titles = albums_div.find_all('a', class_='album-title')

        if album_links and album_titles:
          for link, thumb, title in zip(album_links, album_thumbs, album_titles):
            album_url = link.get('href')
            album_name = title.text.strip()
            album_thumb = thumb.get('data-src')
            content.append({"title": album_name,
              "thumb": album_thumb,
              "url": album_url})

    return content

  def change_version_content(self, version):
    if not isinstance(version, str):
      raise Exception("'version' should be an string.")

    version = version.strip().lower()
    if not version in self.__version_list:
      raise Exception(f"'version' should be in {self.__version_list}")

    url = f"https://www.erome.com/version/{version}"
    response = self.__session.get(url, headers=self.__headers)

  def get_album_content(self, path):
    path = path.strip()
    path = re.sub(r'\s{2,}', ' ', path)
    path = path.replace(' ', '+')
    url = f"https://www.erome.com/a/{path}"
    response = self.__session.get(url, headers=self.__headers)
    content = {"videos": [], "photos": []}

    if 200 <= response.status_code <= 207:
      soup = BeautifulSoup(response.text, 'html.parser')
      videos = []
      for video in soup.find_all('video'):
        video_src = video.find('source')['src']
        video_poster = video['data-setup'].split('"')[3] if 'data-setup' in video.attrs else None
        videos.append({
          'video_url': video_src,
          'thumb_url': video_poster})

      images = []
      for img_div in soup.find_all('div', class_='img'):
        img_tag = img_div.find('img')
        if img_tag:
          img_url = img_tag['data-src']
          images.append(img_url)

      content["videos"].extend(videos)
      content["photos"].extend(images)

    return content

  def get_content(self, url, max_video_bytes=0):
    if not isinstance(url, str):
      raise Exception("'url' should be an string.")

    elif not isinstance(max_video_bytes, int):
      raise Exception("'max_video_bytes' should be an integer.")

    match = re.search(self.__media_pattern, url)
    if not match:
      raise Exception("'url' must be the erome pattern.")

    host = match.group(1)
    if host.startswith("s"):
      headers = {
        "host": host,
        "sec-ch-ua-platform": "Android",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": "Google Chrome;v=131, Chromium;v=131, Not_A Brand;v=24",
        "sec-ch-ua-mobile": "?1",
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-dest": "image",
        "referer": "https://www.erome.com/",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "priority": "i"
      }

    elif host.startswith("v"):
      headers = {
        "Host": host,
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Android",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": "Google Chrome;v=131, Chromium;v=131, Not_A Brand;v=24",
        "sec-ch-ua-mobile": "?1",
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "video",
        "Referer": "https://www.erome.com/",
        "Accept-Language": "en-US,en;q=0.9",
        "Range": "bytes=0-" + str(max_video_bytes - 1) if max_video_bytes > 1 else ""
      }

    response = self.__session.get(url, headers=headers)

    if 200 <= response.status_code <= 207:
      return response.content

    return Exception("Invalid or expired 'url'")

  def get_all_album_data(self, keyword, page=1, limit=1):
    keyword = keyword.strip()
    keyword = re.sub(r'\s{2,}', ' ', keyword)
    keyword = keyword.replace(' ', '+')
    content = []

    if not isinstance(page, int) or page <= 0:
      raise Exception("'page' should be an integer value and greater than or equal to 1.")

    elif not isinstance(limit, int) or limit <=0:
      raise Exception("'limit' should be an integer value and greater than or equal to 1.")

    elif not isinstance(keyword, str):
      raise Exception("'url' should be an string.")

    elif page > limit:
      raise Exception("'page' should not be a value greater than 'limit'.")

    while page <= limit:
      content.extend(self.__get_album_data(page, keyword=keyword))
      page += 1

    return content

  def get_explore(self, page=1, limit=1, new=False):
    content = []

    if not isinstance(page, int) or page <= 0:
      raise Exception("'page' should be an integer value and greater than or equal to 1.")

    elif not isinstance(limit, int) or limit <=0:
      raise Exception("'limit' should be an integer value and greater than or equal to 1.")

    elif not isinstance(new, bool):
      raise Exception("'new' should be an bool value.")

    elif page > limit:
      raise Exception("'page' should not be a value greater than 'limit'.")

    while page <= limit:
      content.extend(self.__get_album_data(page, new=new))
      page += 1

    return content
