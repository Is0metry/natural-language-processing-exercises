import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict


def get_blog_articles() -> List[Dict[str, str]]:
    url = 'https://codeup.com/blog/'
    endpoints = ['data-science/what-is-the-future-of-data-science/', 'codeup-news/codeup-is-accredited/', 'dallas-info/it-professionals-dallas/',
                 'codeup-news/dei-report/', 'https://codeup.com/data-science/jobs-after-a-coding-bootcamp-part-1-data-science/']
    articles: List[Dict[str, str]] = []
    headers = {'User-Agent': 'Codeup Data Science'}
    for e in endpoints:
        article = {}
        soup = BeautifulSoup(requests.get(
            url + e, headers=headers).text, 'html.parser')
        article['title'] = soup.title.get_text()
        article['content'] = soup.find('div', id='main-content').get_text()
        articles.append(article)
    return articles

def get_article(url:str,category:str)->Dict[str,str]:
    response = requests.get(url).content
    bs = BeautifulSoup(response,'html.parser')
    ret_dict = {}
    ret_dict['category'] = category
    ret_dict['content'] = bs.find('div',itemprop='articleBody').get_text()
    ret_dict['headline'] = bs.find('span',itemprop='headline').get_text()
    return ret_dict

def get_articles(url:str,list_endpoint:str,category:str)->List[Dict[str,str]]:
    full_url = url + list_endpoint
    response = requests.get(full_url).content
    bs = BeautifulSoup(response,'html.parser')
    endpoints = bs.find_all('div',class_='news-card-title')
    ret_lst = []
    for e in endpoints:
        eurl = url + e.a['href']
        ret_lst.append(get_article(eurl,category))
    return ret_lst
def get_news_articles()->List[Dict[str,str]]:
    url = 'https://inshorts.com'
    categories = ['business','sports','technology','entertainment']
    ret_lst = []
    for c in categories:
        ret_lst += get_articles(url,'/en/read/' + c,c)
    return ret_lst