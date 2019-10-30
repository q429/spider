'''
有的时候，网页需要javascript渲染，解析参数比较麻烦时，使用selenium。
'''

import time
from bs4 import BeautifulSoup
from pymongo import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get_detail_position(pos_url):
    try:
        desired_capabilities = DesiredCapabilities.CHROME  # 设置这个选项，加载更快。
        desired_capabilities["pageLoadStrategy"] = "none"
        chrome_options = webdriver.ChromeOptions()  # 无界面模式的选项设置
        chrome_options.add_argument('--headless')
        browser = webdriver.Chrome(executable_path = './venv/Scripts/chromedriver.exe', chrome_options=chrome_options)
        browser.get(pos_url)  # 访问网页
        print('当前访问的网址是：', pos_url)

        # 等待网页加载
        wait = WebDriverWait(browser, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.job-summary')))

        response_text = browser.page_source  # 获得加载后的网页源代码

    finally:
        browser.close()
    return response_text

def parse_detail_position(response_text, pos_url):
    soup = BeautifulSoup(response_text, 'lxml')
    detail_position = {}
    detail_position['crawlTtime'] = time.ctime()  # 抓取时间

    job_info = soup.select('div.summary-plane')[0]
    detail_position['updateTimeStr'] = job_info.select('div.summary-plane__top span.summary-plane__time')[0].contents[1].string  # 职位更新日期
    detail_position['jobName'] = job_info.select('h3.summary-plane__title')[0].string  # 职位名称
    detail_position['jobUrl'] = pos_url  # 职位网址
    detail_position['salary'] = job_info.select('span.summary-plane__salary')[0].string  # 薪资
    detail_position['workExp'] = job_info.select('ul.summary-plane__info')[0].contents[1].string  # 工作年限
    detail_position['education'] = job_info.select('ul.summary-plane__info')[0].contents[2].string  # 学历要求

    job_desc = soup.select('div.job-detail div.describtion__detail-content')[0]  # 职责描述包含html标签，需要重新解析为文本。
    jobDescStr = ''
    for i in job_desc:
        if isinstance(i.string, str):
            jobDescStr += i.string.strip()
    detail_position['jobDesc'] = jobDescStr
    detail_position['companyAddr'] = soup.select('div.job-detail span.job-address__content-text')[0].contents[1].string  # 公司地址

    company_info = soup.select('div.app-main__right')[0]
    detail_position['companyName'] = company_info.select('div.company a')[0].string  # 公司名称
    detail_position['companyUrl'] = company_info.select('div.company a')[0].attrs['href']  # 公司网址
    detail_position['industry'] = company_info.select('div.company button.company__industry')[0].contents[1].string  # 公司所属行业
    detail_position['companySize'] = company_info.select('div.company button.company__size')[0].contents[1].string  # 公司规模大小
    detail_position['companyDesc'] = company_info.select('div.company div.company__description')[0].string  # 公司简介

    print('当前网页提取出来的职位信息是:', detail_position)
    return detail_position

def save_to_mongo(detail_position):
    client = MongoClient()
    db = client.jobs
    collect = db['zhilian_position_detail']
    try:
        if collect.insert(detail_position):
            print('save to mongo succeed')
    except Exception as e:
        print(e.args)
        print('fail to save to mongo')

if __name__ == '__main__':
    # 从职位搜索结果表中取出职位URL，然后依次爬取每个职位的职位详情。
    client = MongoClient()
    db = client.jobs
    collect = db['zhilian_search_results']
    try:
        pos_urls = collect.find({}, {'positionURL': 1})
        for pos_url in pos_urls:
            pos_url = pos_url.get('positionURL')
            print('开始使用selenium访问网页，当前时间：', time.ctime())
            response_text = get_detail_position(pos_url)
            print('访问网页结束，获得响应的body部分。当前时间：', time.ctime())
            detail_position = parse_detail_position(response_text, pos_url)
            print('解析网页数据完毕。当前时间：', time.ctime())
            save_to_mongo(detail_position)
            print('保存数据到MongoDB完毕。当前时间：', time.ctime())
    except Exception as e:
        print(e.args)
