
import re
import time
import unicodedata
from os.path import isfile
from os import stat
from typing import Dict, List

import nltk
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords as stpwrds
from sklearn.model_selection import train_test_split

CODEUP_BLOG_CSV = 'data/codeup_blog.csv'
INSHORT_CSV = 'data/inshort_articles.csv'


def tvt_split(df: pd.DataFrame, stratify: str = None,
              tv_split: float = .2, validate_split: int = .3):
    '''tvt_split takes a pandas DataFrame, a stringspecifying the variable to
    stratify over, as well as 2 floats where 0< f < 1
    and returns a train, validate, and test split of the DataFame,
    split by tv_split initially and validate_split thereafter. '''
    strat = df[stratify]
    train_validate, test = train_test_split(
        df, test_size=tv_split, random_state=123, stratify=strat)
    strat = train_validate[stratify]
    train, validate = train_test_split(
        train_validate, test_size=validate_split,
        random_state=123, stratify=strat)
    return train, validate, test


def get_blog_articles() -> List[Dict[str, str]]:
    url = 'https://codeup.com/blog/'
    endpoints = [
        'data-science/what-is-the-future-of-data-science/',
        'codeup-news/codeup-is-accredited/',
        'dallas-info/it-professionals-dallas/',
        'codeup-news/dei-report/',
        'data-science/jobs-after-a-coding'
        '-bootcamp-part-1-data-science/']
    articles: List[Dict[str, str]] = []
    headers = {'User-Agent': 'Codeup Data Science'}
    for e in endpoints:
        article = {}
        soup = BeautifulSoup(requests.get(
            url + e, headers=headers).text, 'html.parser')
        article['title'] = soup.title.get_text()
        article['content'] = soup.find('div',
                                       class_='entry-content').get_text()
        articles.append(article)
    return articles


def get_article(url: str, category: str) -> Dict[str, str]:
    response = requests.get(url).content
    bs = BeautifulSoup(response, 'html.parser')
    ret_dict = {}
    ret_dict['category'] = category
    ret_dict['content'] = bs.find('div', itemprop='articleBody').get_text()
    ret_dict['headline'] = bs.find('span', itemprop='headline').get_text()
    return ret_dict


def get_articles(url: str,
                 list_endpoint: str,
                 category: str) -> List[Dict[str, str]]:
    full_url = url + list_endpoint
    response = requests.get(full_url).content
    bs = BeautifulSoup(response, 'html.parser')
    endpoints = bs.find_all('div', class_='news-card-title')
    ret_lst = []
    for e in endpoints:
        eurl = url + e.a['href']
        ret_lst.append(get_article(eurl, category))
    return ret_lst



def get_news_articles() -> List[Dict[str, str]]:
    url = 'https://inshorts.com'
    categories = ['business', 'sports', 'technology', 'entertainment']
    ret_lst = []
    for c in categories:
        ret_lst += get_articles(url, '/en/read/' + c, c)
    return ret_lst


def get_blog_df() -> pd.DataFrame:
    if isfile(CODEUP_BLOG_CSV):
        return pd.read_csv(CODEUP_BLOG_CSV, index_col=0)
    lst = get_blog_articles()
    ret_df = pd.DataFrame(lst)
    ret_df.to_csv(CODEUP_BLOG_CSV)
    return ret_df


def get_article_df() -> pd.DataFrame:
    ret_df = pd.DataFrame()
    if isfile(INSHORT_CSV):
        ret_df = pd.read_csv(INSHORT_CSV, index_col=0)
    last_updated = time.time() - stat(INSHORT_CSV).st_mtime
    scrape = (last_updated > 3600 or not isfile(INSHORT_CSV))
    if scrape:
        lst = pd.DataFrame(get_news_articles())
        ret_df = ret_df.drop_duplicates()
        ret_df = pd.concat([ret_df, lst])
        ret_df.to_csv(INSHORT_CSV)
    return ret_df


stopwords = stpwrds.words('english')


def basic_clean(string: str) -> str:
    # TODO Docstring
    string = string.lower()
    string = unicodedata.normalize('NFKD', string).encode(
        'ascii', 'ignore').decode('utf-8', 'ignore')
    string = re.sub(r"[^a-z0-9'\s]", '', string)
    return string


def tokenize(string: str) -> str:
    # TODO Docstring
    tok = nltk.tokenize.ToktokTokenizer()
    return tok.tokenize(string, return_str=True)


def stem(tokens: str) -> str:
    # TODO Docstring
    ps = nltk.porter.PorterStemmer()
    ret = [ps.stem(s) for s in tokens.split()]
    return ' '.join(ret)


def lemmatize(tokens: str) -> str:
    # TODO Docstring
    lem = nltk.stem.WordNetLemmatizer()
    ret = [lem.lemmatize(s) for s in tokens.split()]
    return ' '.join(ret)


def remove_stopwords(tokens: str,
                     extra_words: List[str] = [],
                     exclude_words: List[str] = []) -> str:
    # TODO Docstring
    tokens = [t for t in tokens.split()]
    for exc in exclude_words:
        stopwords.remove(exc)
    for ext in extra_words:
        stopwords.append(ext)
    stopped = [t for t in tokens if t not in stopwords]
    return ' '.join(stopped)


def squeaky_clean(string: str, extra_words: List[str] = [], exclude_words: List[str] = []) -> str:
    string = basic_clean(string)
    string = tokenize(string)
    return remove_stopwords(string, extra_words, exclude_words)


def prep_df_for_nlp(df: pd.DataFrame, ser: str,
                    extra_words: List[str] = [],
                    exclude_words: List[str] = []) -> pd.DataFrame:
    df['clean'] = df[ser].apply(
        squeaky_clean, exclude_words=exclude_words, extra_words=extra_words)
    df['stem'] = df['clean'].apply(stem)
    df['lemmatized'] = df['clean'].apply(lemmatize)
    return df


def wrangle_codeup_blog() -> pd.DataFrame:
    # TODO Docstring
    df = get_blog_df()
    df = df.rename(columns={'content': 'text'})
    df = prep_df_for_nlp(df, 'text',extra_words=['codeup',"'"])
    return df


def wrangle_inshort_articles(extra_words:List[str]= [],exclude_words:List[str]=[]) -> pd.DataFrame:
    df = get_article_df()
    df = df.rename(columns={'content': 'text'})
    df = prep_df_for_nlp(df, 'text',extra_words=extra_words,exclude_words=exclude_words)
    return df
