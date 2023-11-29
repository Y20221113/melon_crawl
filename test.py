import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("Initializing WebDriver...")
driver = webdriver.Chrome()
driver.maximize_window()
url = 'https://www.melon.com/chart/index.htm'
driver.get(url)

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span')))

print("Navigating to chart finder...")
driver.find_element(By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span').click()

print("Clicking on monthly chart...")
driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/h4[2]/a').click()
time.sleep(2)

print("Initializing DataFrame...")
result_df = pd.DataFrame()

desired_decade_index = 2  # 시작할 decade_index
desired_year_index = 1  # 시작할 year_index
desired_month_index = 1  # 시작할 month_index

# 최대 연도 설정
최대_연도 = 10

# 현재 decade_index, year_index 및 month_index를 원하는 값으로 설정합니다.
decade_index = desired_decade_index
year_index = desired_year_index
month_index = desired_month_index

print("Entering main loop...")

try:
    while decade_index <= 최대_연도:
        try:
            print("Selecting decade...")
            driver.find_element(By.XPATH, f'//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[{decade_index}]/span/label').click()
            time.sleep(2)

            print("Selecting year...")
            driver.find_element(By.XPATH, f'//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[{year_index}]/span/label').click()
            time.sleep(2)
        except Exception as e_year:
            print(f"Error in selecting year: {e_year}")
            decade_index += 1  # Increment decade index
            print(f"Moving to the next decade... Decade index: {decade_index}")

            # Reset year index
            year_index = 1
            continue

        for month in range(month_index, 13):
            print(f"Processing month {month}")
            month_element = driver.find_element(By.XPATH, f'//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{month}]/span/label')
            month_element.click()
            time.sleep(10)

            print("Selecting genre...")
            driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[1]/span/label').click()
            time.sleep(2)

            print("Clicking search button...")
            driver.find_element(By.XPATH, '//*[@id="d_srch_form"]/div[2]/button/span/span').click()
            time.sleep(10)

            print("Fetching song details...")
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            song_elements = soup.select('a[href*=playSong]')
            song_list = []
            singer_list = []
            genre_list = []
            lyrics_list = []

            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537')
            }

            for i, tag in enumerate(song_elements, 1):
                print(f"Processing song {i}")
                title = tag.text
                song_list.append(title)

                js = tag['href']
                matched = re.search(r",'(\d+)'", js)

                if matched:
                    song_Id = matched.group(1)
                    song_url = 'https://www.melon.com/song/detail.htm?songId=' + song_Id
                    response = requests.get(song_url, headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # 가수 정보 가져오기
                    singer_element = soup.select('.artist span')
                    singer = singer_element[0].text if singer_element else 'Unknown'
                    singer_list.append(singer)

                    # 장르 정보 가져오기
                    genre_element = soup.select('.list dd')
                    genre = genre_element[2].text if len(genre_element) > 2 else 'Unknown'
                    genre_list.append(genre)

                    # 가사 정보 가져오기
                    lyric_element = soup.select('.lyric')
                    lyric = lyric_element[0].text if lyric_element else 'Unknown'
                    lyrics_list.append(lyric)

            year = 2008  # 연도는 임의로 설정하였습니다. 실제로는 루프에 맞게 조정 필요
            df = pd.DataFrame({'연도': year, '월': [month]*len(song_list), '곡명': song_list, '가수명': singer_list, '장르': genre_list, '가사': lyrics_list})
            result_df = pd.concat([result_df, df], ignore_index=True)

            # Increment month index for the next iteration
            month_index = 1

            # Increment year index for the next iteration
            year_index += 1

            # Save data at this point
            result_df.to_csv('melon_with_genre7_partial.csv', encoding='utf-8-sig')

    print("Saving final results to CSV file...")
    result_df.to_csv('melon_with_genre7.csv', encoding='utf-8-sig')
    
except Exception as e:
    print(f"Error: {e}")

finally:
    print("Closing WebDriver...")
    driver.quit()
