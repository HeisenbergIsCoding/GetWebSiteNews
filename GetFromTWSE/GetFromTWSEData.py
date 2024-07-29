import requests
from bs4 import BeautifulSoup
import csv
import time
import os


def fetch_company_data(company_code, year, season):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb03'
    payload = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'false',
        'co_id': company_code,
        'year': year,
        'season': season
    }

    for _ in range(3):  # 重試3次
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find('table', class_='hasBorder')
            if table is None:
                print(f"公司代號 {company_code} 年 {year} 季 {season} 沒有找到表格資料。")
                return [], []

            headers = [header.get_text(strip=True) for header in table.find_all('th')]
            data = [[col.get_text(strip=True).replace(',', '') for col in row.find_all('td')] for row in
                    table.find_all('tr') if row.find_all('td')]
            return headers, data
        except requests.exceptions.RequestException as e:
            print(f"請求失敗: {e}")
            time.sleep(5)  # 等待5秒後重試
    return [], []  # 如果重試3次都失敗，返回空數據


def save_to_csv(headers, data, filename):
    os.makedirs('csv', exist_ok=True)
    filepath = os.path.join('csv', filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


if __name__ == '__main__':
    with open('stocks.csv', mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 略過第一行
        company_codes = [row[0] for row in reader]

    years = ['111', '112', '113']
    seasons = ['01', '02', '03', '04']

    for company_code in company_codes:
        for year in years:
            for season in seasons:
                headers, data = fetch_company_data(company_code, year, season)
                if data:
                    filename = f'{company_code}_{year}_{season}.csv'
                    save_to_csv(headers, data, filename)
                    print(f"資料已保存至 csv/{filename}")
                time.sleep(2)  # 每次爬取後休息2秒
