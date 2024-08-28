import os
import time
import requests
from pytubefix import YouTube
from pytubefix.cli import on_progress
from concurrent.futures import ThreadPoolExecutor
import timeit

container_ip = "172.17.0.2"

proxies = {
    'http': f'http://{container_ip}:8888',
    'https': f'http://{container_ip}:8888',
}

session = requests.Session()
session.proxies.update(proxies)

# Test proxy connection
try:
    test_response = session.get('http://ipinfo.io/json', timeout=5)
    if test_response.status_code == 200:
        print("Proxy is working correctly. Using proxy for requests.")
    else:
        print(f"Proxy test failed with status code: {test_response.status_code}")
except Exception as e:
    print(f"Failed to connect using the proxy. Error: {e}")

def download_video(url, save_folder, timeout):
    url = url.strip()
    try:
        yt = YouTube(url, on_progress_callback=on_progress, proxies=proxies)
        print(f"Downloading: {yt.title}")
        ys = yt.streams.get_highest_resolution()
        ys.download(output_path=save_folder)
        print(f"Downloaded: {yt.title} to {save_folder}")
        if timeout:
            print(f"Waiting for {timeout} seconds before downloading the next video...")
            time.sleep(timeout)
        return True
    except Exception as e:
        print(f"Failed to download video from {url}. Error: {e}")
        return False

def download_videos_from_txt():
    file_path = input("Enter the name of the .txt file containing video URLs: ")
    save_folder = input("Enter the folder name where videos will be saved: ")

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    timeout = int(input("Enter the timeout in seconds between each download: "))
    track_time = input("Do you want to track the total time taken? (yes/no): ").strip().lower() == 'yes'
    use_all_threads = input("Do you want to use all available threads? (yes/no): ").strip().lower() == 'yes'

    if use_all_threads:
        max_workers = None
    else:
        max_workers = int(input("Enter the number of threads to use: "))

    start_time = timeit.default_timer()

    with open(file_path, 'r') as file:
        urls = file.readlines()

    total_urls = len(urls)
    downloaded_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda url: download_video(url, save_folder, timeout), urls))
        downloaded_count = sum(results)

    if track_time:
        total_time = timeit.default_timer() - start_time
        print(f"Total time taken: {total_time / 60:.2f} minutes")

    print(f"Total URLs in file: {total_urls}")
    print(f"Total videos downloaded: {downloaded_count}")

download_videos_from_txt()
