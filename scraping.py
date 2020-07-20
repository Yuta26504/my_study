import re
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup as bs4
from fake_useragent import UserAgent
from selenium import webdriver
import chromedriver_binary
from urllib.parse import urljoin
import os
import traceback
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import datetime
import time
import sys
import csv

driver = webdriver.Chrome()

ua = UserAgent()
useragent = ua.random

#-------------------------------------------------------
def get_urls(url):
    
    urls = []
    while True:
        try:
            driver.get(url)
        except :
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break

    driver.maximize_window()
    driver.implicitly_wait(30)

    headers = {"User-Agent": useragent}
    res = requests.get(url,headers = headers)
    soup = bs4(res.content, "html.parser")

    while True:
        try:
            house_blocks = soup.find_all('div', class_="_3gn0lkf") #一軒のhref情報
        except:
            continue
        else:
            break

    for house_block in house_blocks:
        href = house_block.find('a').get('href')
        if urljoin(BASE_URL, href) not in urls:
            urls.append(urljoin(BASE_URL, href))
            driver.implicitly_wait(10)

    return(urls)
#-------------------------------------------------------


#-------------------------------------------------------
def get_next_page(url):
    
    while True:
        try:
            driver.get(url)
        except:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break

    driver.maximize_window()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.implicitly_wait(10)

    while True:
        try:
            next_btn = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@data-id="SearchResultsPagination"]/li[@class="_i66xk8d"]/a[@class="_1cnw8os"]'))
            )

        except NoSuchElementException:
                print(f'\n{traceback.format_exc()}')
                continue
        else:
                break

    driver.implicitly_wait(10)
    next_btn.click()

    n_url = driver.current_url
    
    return n_url
#-------------------------------------------------------


#-------------------------------------------------------
def scrape(url): 
    while True:
        try:
            driver.get(url)
            driver.maximize_window()
            driver.implicitly_wait(10)
        except:
                print(f'\n{traceback.format_exc()}')
                continue
        else:
            break

    html_souce = driver.page_source
    soup = bs4(html_souce, "html.parser")

    data = {}
    notFound = []

    scrape_list =   [
            'owner_id', 'title', 'location', 'price',  \
            'guests',  'bedrooms', 'beds', 'bathrooms', 'date', 'datetime', 'url'
        ]

    for r in scrape_list:
            data[r] = None

    try:
        data["owner_id"] = re.search(r'(\d+)', driver.current_url).group()
    except Exception:
        notFound.append("owner_id")
    print("owner_id:", data["owner_id"])

    try:
        data["title"] = driver.find_element_by_xpath('//div[@class="_mbmcsn"]/h1[@tabindex="-1"]').text
    except Exception:
        notFound.append("title")
    print("title:", data["title"])

    try:
        data["location"] = driver.find_element_by_xpath('//div[@class="_abi9lj"]//span[@class="_13myk77s"]/a[@class="_5twioja"]').text
    except Exception:
        notFound.append("location")
    print("location:", data["location"])

    try:
        tmp = driver.find_element_by_xpath('//*[@id="site-content"]/div/div/div[3]/div[1]/div/div[1]/div/div/div/div/div[1]/div[2]/span[1]').text
        m = re.search('\d+', tmp).group()
        data['guests'] = int(m)
    except Exception:
        notFound.append('guests')
    print('guests:', data['guests'])

    try:
        tmp = driver.find_element_by_xpath('//*[@id="site-content"]/div/div/div[3]/div[1]/div/div[1]/div/div/div/div/div[1]/div[2]/span[3]').text
        m = re.search("\d+", tmp).group()
        data["bedrooms"] = int(m)
    except Exception:
        notFound.append("bedrooms")
    print("bedrooms:", data["bedrooms"])

    try:
        tmp = driver.find_element_by_xpath('//*[@id="site-content"]/div/div/div[3]/div[1]/div/div[1]/div/div/div/div/div[1]/div[2]/span[5]').text
        m = re.search("\d+", tmp).group()
        data["beds"] = int(m)
    except Exception:
        notFound.append("beds")
    print("beds:", data["beds"])

    try:
        tmp = driver.find_element_by_xpath('//*[@id="site-content"]/div/div/div[3]/div[1]/div/div[1]/div/div/div/div/div[1]/div[2]/span[7]').text
        if re.search("共用", tmp) == None:
            if re.search('\d+\.\d+', tmp) == None:
                    m = re.search('\d+', tmp).group()
                    n = ""
            else :
                    m = re.search('\d+\.\d+', tmp).group()
                    n = ""
        elif re.search('\d+\.\d+', tmp) == None:
            m = re.search('\d+', tmp).group()
            n = re.search("共用", tmp).group()
        else:
            m = re.search('\d+\.\d+', tmp).group()
            n= re.search("共用", tmp).group()
        data["bathrooms"] = m + n
    except Exception:
        notFound.append("bathrooms")
    print("bathrooms:", data["bathrooms"])

    try:
        tmp = driver.find_element_by_xpath('//*[@id="site-content"]/div/div/div[3]/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div/div/span/span[1]').text
        _tmp = tmp.strip("¥").replace(',','')
        data["price"] = _tmp
    except Exception:
        notFound.append("price")
    print("price:", data["price"], "円")

    data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    print("date:", data["date"])
    data['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("datetime:", data["datetime"])

    house_name = "house_id_{}.png".format(data["owner_id"])
    driver.save_screenshot(os.path.join(house_path, house_name))

    if len(notFound) != 0:
        pass

    data['url'] = driver.current_url
    print("url:", data["url"])

    return data
#-------------------------------------------------------


#-------------------------------------------------------
start = time.time()
if __name__ == '__main__':
    prefectures = [

        "北海道"

    ]
    ''' "大阪","沖縄","熊本","青森","岩手","宮城","秋田","山形","福島","茨城",\
            "栃木","群馬","埼玉","千葉","東京","神奈川","新潟","富山","石川",\
                "福井","山梨","長野","岐阜","静岡","愛知","三重","滋賀","京都",\
                    "兵庫","奈良","和歌山","鳥取","島根","岡山","広島","山口","徳島","香川",\
                        "愛媛","高知","福岡","佐賀","長崎","大分","宮崎","鹿児島","沖縄"
 '''
    for num in tqdm(prefectures):
        BASE_URL = 'https://www.airbnb.com'
        date_of_checkin = '2020-09-07' 
        date_of_checkout = '2020-09-08'
        site = "{}".format(num)
        area_path = "./{}_area".format(site)
        house_path = "./{}_house".format(site)

        if not os.path.exists(area_path):
            os.mkdir(area_path) 
        if not os.path.exists(house_path):
            os.mkdir(house_path)

        URL_frag1 = r'https://www.airbnb.jp/s/{}--日本/homes?tab_id=all_tab&refinement_paths%5B%5D=%2Fhomes&source=structured_search_input_header&search_type=search_query'.format(num)
        URL_checkin = r'&checkin='
        URL_checkout = r'&checkout='
        URL_frag2 = r'&min_beds=1&min_bedrooms=1&min_bathrooms=1'    
        URL_price_min = r'&price_min='
        URL_price_max = r'&price_max='
        URL_frag3 = r'&allow_override%5B%5D=&s_tag=xepuKXHN'

        crawl_number = 1

        price_1100 = 1100
        price_5000 = 5000

        first_list_url = URL_frag1 + URL_checkin + date_of_checkin + URL_checkout + date_of_checkout + URL_frag2 + URL_price_min + str(price_1100) + URL_price_max + str(price_5000) + URL_frag3
        current_url = first_list_url
        print('min_price:'+ str(price_1100) +' max_price:' + str(price_5000))
        print('■', current_url)
        urls = []
        datas = []

        area_id = 1

        while True:
            time.sleep(5)
            urls.extend(get_urls(current_url))
            try:
                time.sleep(5)
                area_png_name = "area_id_{}.png".format(area_id)
                driver.save_screenshot(os.path.join(area_path, area_png_name))
                area_id = area_id + 1
                current_url = get_next_page(current_url)
                print('■', current_url)
            except:
                break

        for min_price in range(5000,40000,5000):
            max_price = min_price +5000
            second_list_url = URL_frag1 + URL_checkin + date_of_checkin + URL_checkout + date_of_checkout + URL_frag2 + URL_price_min + str(min_price) + URL_price_max + str(max_price) + URL_frag3
            current_url = second_list_url
            print('min_price:'+ str(min_price) +' max_price:' + str(max_price))
            print('■', current_url)
            time.sleep(5)
    
            while True:
                time.sleep(5)
                urls.extend(get_urls(current_url))
                try:
                    time.sleep(5)
                    area_png_name = "area_id_{}.png".format(area_id)
                    driver.save_screenshot(os.path.join(area_path, area_png_name))
                    area_id = area_id + 1
                    current_url = get_next_page(current_url)
                    print('■', current_url)
                except:
                    break
        
        price_40000 = 40000
        price_100000 = 100000

        first_list_url = URL_frag1 + URL_checkin + date_of_checkin + URL_checkout + date_of_checkout + URL_frag2 + URL_price_min + str(price_40000) + URL_price_max + str(price_100000) + URL_frag3
        current_url = first_list_url
        print('min_price:'+ str(price_40000) +' max_price:' + str(price_100000))
        print('■', current_url)
        time.sleep(5)

        while True:
            time.sleep(5)
            urls.extend(get_urls(current_url))
            try:
                time.sleep(5)
                area_png_name = "area_id_{}.png".format(area_id)
                driver.save_screenshot(os.path.join(area_path, area_png_name))
                area_id = area_id + 1
                current_url = get_next_page(current_url)
                print('■', current_url)
            except:
                break

        print('■■', urls)
        urls_conts = len(urls)
        print('・・・', str(urls_conts + 1) + 'th listings!')

        for house_data_url in urls:
            try:
                print('■■■', house_data_url)
                datas.append(scrape(house_data_url))
                time.sleep(5)
                print('【No.'+ str(crawl_number) + '】' + house_data_url)
                crawl_number = crawl_number + 1
            except:
                print('・・・ NO LISTING!')

        column_order = [
                'owner_id', 'title', 'location', 'price',  \
                'guests',  'bedrooms', 'beds', 'bathrooms', 'date', 'datetime', 'url'
            ]

        if len(datas)!=0:
                path = './{}_air_inf'.format(site)
                if not os.path.exists(path):
                        os.mkdir(path)  
                    
                df = pd.DataFrame(datas)
                file_name_csv = site + "_" + date_of_checkin + "_" + datetime.datetime.now().strftime('%Y%m%d')+'.csv'
                df.to_csv(os.path.join(path, file_name_csv), sep=',',encoding='utf_8_sig',index=False, quoting=csv.QUOTE_ALL, columns=column_order)
                print("Write out !!")

        end = time.time()
        proc = (end - start) * 1000 * 1.67 * 10 **-5
        print("process {0} min".format(proc))

    sys.exit()

driver.quit()



