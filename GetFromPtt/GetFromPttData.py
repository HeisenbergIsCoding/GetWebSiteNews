import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os

BASE_URL = 'https://www.ptt.cc/bbs/Stock/index.html'
DATA_DIR = 'PttStockData'


# 抓取單個頁面的文章列表
def fetch_page(url):
    print(f'Fetching {url}')
    response = requests.get(url, cookies={'over18': '1'})
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}")
    return response.text


# 解析頁面中的文章列表
def parse_articles(html, keyword=None, stock_id=None):
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    for item in soup.select('.r-ent'):
        title_tag = item.select_one('.title a')

        if title_tag:
            title = title_tag.text
            href = title_tag['href']
            date = item.select_one('.date').text.strip()
            if (keyword and keyword in title) or (stock_id and stock_id in title):
                articles.append({
                    'title': title,
                    'href': 'https://www.ptt.cc' + href,
                    'date': date
                })
    return articles


# 根據日期篩選文章
def filter_by_date(articles, target_date):
    filtered_articles = []
    for article in articles:
        try:
            article_date = datetime.strptime(article['date'], '%m/%d')
            article_date = article_date.replace(year=target_date.year)
            if article_date.date() == target_date.date():
                filtered_articles.append(article)
        except ValueError:
            continue
    return filtered_articles


# 抓取文章內容
def fetch_article_content(url):
    html = fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    main_content = soup.find(id="main-content")
    article_text = main_content.get_text() if main_content else ''
    return article_text


# 保存文章到本地文件
def save_article_to_file(article, stock_id, target_date):
    article_date = datetime.strptime(article['date'], '%m/%d').replace(year=target_date.year)
    title = article['title']
    safe_title = "".join(x for x in title if x.isalnum() or x in " -_")
    filename = f"{article_date.strftime('%Y-%m-%d')}-{safe_title}.txt"

    # 確保資料夾存在
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    filepath = os.path.join(DATA_DIR, filename)
    content = fetch_article_content(article['href'])

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f"Title: {title}\n")
        file.write(f"Date: {article_date.strftime('%Y-%m-%d')}\n")
        file.write(f"Link: {article['href']}\n\n")
        file.write(content)

    # 添加日志信息确认文件保存
    print(f"Saved article to {filepath}")


# 抓取多個頁面的文章，根據日期和關鍵字/股票代號篩選
def fetch_articles(stock_id, keyword, target_date):
    url = BASE_URL
    all_articles = []

    while True:
        html = fetch_page(url)
        articles = parse_articles(html, keyword, stock_id)
        filtered_articles = filter_by_date(articles, target_date)
        all_articles.extend(filtered_articles)

        if any(datetime.strptime(article['date'], '%m/%d').replace(year=target_date.year) != target_date for article in articles):
            break

        soup = BeautifulSoup(html, 'html.parser')
        prev_link = soup.select_one('.btn.wide:-soup-contains("‹ 上頁")')
        if prev_link:
            url = 'https://www.ptt.cc' + prev_link['href']
        else:
            break

        time.sleep(3)

    return all_articles


# 主函數
def main():
    stock_id = input("請輸入股票代號 (可選): ").strip()
    keyword = input("請輸入關鍵字 (可選): ").strip()

    # 如果沒有輸入股票代號和關鍵字，提示用戶輸入
    if not stock_id and not keyword:
        print("請至少輸入股票代號或關鍵字中的一個。")
        return

    today = datetime.now()
    target_date = today

    start_date_str = input("請輸入開始日期 (MM/DD) (預設為今天): ").strip()
    end_date_str = input("請輸入結束日期 (MM/DD) (預設為今天): ").strip()

    if start_date_str or end_date_str:
        start_date = datetime.strptime(start_date_str, '%m/%d') if start_date_str else target_date
        end_date = datetime.strptime(end_date_str, '%m/%d') if end_date_str else target_date
    else:
        start_date = target_date
        end_date = target_date

    articles = fetch_articles(stock_id, keyword, target_date)

    for article in articles:
        print(f"Title: {article['title']}, Date: {article['date']}, Link: {article['href']}")
        save_article_to_file(article, stock_id, target_date)


if __name__ == '__main__':
    main()
