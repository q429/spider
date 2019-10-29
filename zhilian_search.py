'''
1.首先分析网页的请求响应：https://sou.zhaopin.com/?jl=763&kw=%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90&kt=3。
  数据的位置：是在https://fe-api.zhaopin.com/c/i/sou?中，是一个异步请求。
2.构建请求头。
3.发起响应，获得json。
4.解析json。
5.保存到数据库。

'''


import requests
import time
import json

from pymongo import *
from urllib.parse import urlencode
from urllib.parse import quote

def get_one_page(page=1, cityId=763, search_keywords='数据分析'):
    """构造请求头，发起请求，获取响应json。
        page: 第N页搜索结果
        cityId: 城市的ID
        search_keywords: 搜索关键词
        return: 返回json
    """
    start = (page - 1) * 90  # 搜索结果每页90个，请求参数的start的值为0,90,180等。
    headers = {
        'referer': 'https://sou.zhaopin.com/?jl=' + str(cityId) + '&kw=' + quote(search_keywords) + '&kt=3',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)',
        'x-requested-with': 'XMLHttpRequest'  # ajax异步请求
    }
    params = {
        'start': start,
        'pageSize': '90',
        'cityId': cityId,
        'workExperience': -1,
        'education': -1,
        'companyType': -1,
        'employmentType': -1,
        'jobWelfareTag': -1,
        'kw': search_keywords,
        'kt': 3,
        '_v': '0.00882343',
        'x-zp-page-request-id': '2275381cb6bf46c9a719bdbc7fca9ff0-1572342384239-996098',
        'x-zp-client-id': '7fb87906-040b-43cb-a4d7-095e68713ac5'
    }

    url_search = 'https://fe-api.zhaopin.com/c/i/sou?' + urlencode(params)

    try:
        response = requests.get(url_search, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        print('连接错误')
        return None

def parse_one_page(response_json):
    if response_json:
        items = response_json.get('data').get('results')
        for item in items:
            zhilian_search_results = {}
            zhilian_search_results['crawlTime'] = str(time.ctime())  # 抓取时间
            zhilian_search_results['businessArea'] = item.get('businessArea')  # 公司所在区域
            zhilian_search_results['city'] = item.get('city').get('items')[0].get('name')  # 公司所在城市
            zhilian_search_results['companyName'] = item.get('company').get('name')  # 公司名称
            zhilian_search_results['companyNumber'] = item.get('company').get('number')  # 公司ID
            zhilian_search_results['companySize'] = item.get('company').get('size').get('name')  # 公司人数规模
            zhilian_search_results['eduLevel'] = item.get('eduLevel').get('name')  # 职位要求的学历
            zhilian_search_results['jobName'] = item.get('jobName')  # 职位名称
            zhilian_search_results['jobNumber'] = item.get('number')  # 职位ID
            zhilian_search_results['jobType'] = item.get('jobType').get('items')[0].get('name')  # 职位类别
            zhilian_search_results['positionURL'] = item.get('positionURL')  # 职位网址
            zhilian_search_results['salary'] = item.get('salary')  # 薪资
            zhilian_search_results['updateDate'] = item.get('updateDate')  # 职位更新时间
            zhilian_search_results['workingExp'] = item.get('workingExp').get('name')  # 工作年限要求
            print(zhilian_search_results)
            yield zhilian_search_results

def save_to_mongo(zhilian_search_results):
    client = MongoClient()
    db = client.jobs
    collect = db['zhilian_search_results']
    try:
        if collect.insert(zhilian_search_results):
            print('save to mongo succeed')
    except Exception as e:
        print(e.args)
        print('fail to save to mongo')

if __name__ == '__main__':
    # 抓取搜索相关性较高的前5页
    for i in range(1, 6):
        time.sleep(1)
        response_json = get_one_page(i)
        zhilian_search_results = parse_one_page(response_json)
        save_to_mongo(zhilian_search_results)