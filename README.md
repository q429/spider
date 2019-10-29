# 招聘网站爬虫项目
招聘网站爬虫：使用Python的requests包爬取智联招聘等网站，使用XPath、BeautifulSoup等包解析网页，保存到MongoDB数据库中。
1. 首先，访问智联招聘网站的搜索页，查看请求和响应。  
可以看到职位的相关数据在`https://fe-api.zhaopin.com/c/i/sou?`中，是一个异步请求。
2. 构造请求体：设置UA、x-requested-with等等参数。
3. 访问网页并获得json：使用get函数发起访问，获取响应的json。
4. 解析json：按照需要的字段，解析json。
5. 保存数据：把数据保存到MongoDB数据库中。

# 代码地址
代码地址：[招聘网站爬虫](https://github.com/q429/spider/blob/master/zhilian_search.py)。

