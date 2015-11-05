#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
import selenium
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import logging
import re
import time
from urllib.parse import quote
import random
from urllib.parse import quote

BASE_URL = 'http://weixin.sogou.com'

UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"

def get_html(url):
    """
        This function is use to get html content by using python selenium & PhantomJS
    """
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        UA
    )
    dcap["takesScreenshot"] = (False)
    #t0 = time.time()
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
        driver.set_page_load_timeout(240)
        # driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
        #
        # driver.execute('executePhantomScript', {'script': '''
        #     var page = this; // won't work otherwise
        #     page.onResourceRequested = function(requestData, request) {
        #         if ((/http:\/\/.+?\.css/gi).test(requestData['url']) || requestData['Content-Type'] == 'text/css') {
        #             console.log('The url of the request is matching. Aborting: ' + requestData['url']);
        #             request.abort();
        #         }
        #     }
        #     ''', 'args': []})
    except selenium.common.exceptions.WebDriverException:
        return None
    try:
        driver.get(url)
        html = driver.page_source
    except Exception as e:
        html = None
        logging.error(e)
    finally:
        driver.quit()
    return html

def get_html_direct(url,cookies=None):
    if not cookies:
        cookies = update_cookies()
    headers = {"User-Agent": UA}
    r = requests.get(url, headers=headers, cookies=cookies, timeout=20)
    return r.text

def get_account_info(open_id=None, link=None, cookies=None):
    url = None
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    if link:
        url = link
    html = get_html(url)
    # html = get_html_direct(url, cookies=cookies)
    if not html:
        return None
    soup = BeautifulSoup(html,'html.parser')
    info_box = soup.select('#weixinname')[0].parent
    """
        <div class="txt-box">
        <h3 id="weixinname">简书</h3>
        <h4>
        <span>微信号：jianshuio</span>
        </h4>
        <div class="s-p2">
        <span class="sp-tit">功能介绍:</span><span class="sp-txt">一个基于内容分享的社区——「交流故事·沟通想法」</span>
        </div>
        <div class="s-p2">
        <span class="sp-tit">微信认证：</span><span class="sp-txt">上海佰集信息科技有限公司</span>
        </div>
        </div>
    """
    account_info = {}
    account_info['account'] = info_box.select('h4 span')[0].text.split('：')[1].strip()
    account_info['name'] = info_box.select('#weixinname')[0].text
    account_info['address'] = url
    account_info['description'] = info_box.select('.sp-txt')[0].text
    """
    <div class="img-box">
        <a href="#"><img src="http://img01.sogoucdn.com/app/a/100520090/oIWsFt3nvJ2jaaxm9UOB_LUos02k" onload="vrImgLoad(this, 'fit', 76, 76)" onerror="vrImgErr(this, '/wechat/images/account/def71-71.png')" extra="err:'http://img01.store.sogou.com/net/a/04/link?appid=100520031&amp;url=http://wx.qlogo.cn/mmhead/Q3auHgzwzM6LgOhEVZlNxwCdGpVtZ338IMTa2btYIuIfU3ejvL8SfQ/0/0'"></a>
    </div>
    """
    logo_img = soup.select('.img-box a img')
    account_info['logo'] = logo_img[0]['src']
    """
    <div class="v-box">
        <img width="70" height="70" alt="" src="http://img03.sogoucdn.com/app/a/100520104/fHVKRWzE7lKRh30mnyBY"><em><img width="16" height="16" alt="" src="http://img01.store.sogou.com/net/a/04/link?appid=100520078&amp;url=http://wx.qlogo.cn/mmhead/Q3auHgzwzM6LgOhEVZlNxwCdGpVtZ338IMTa2btYIuIfU3ejvL8SfQ/0/0"></em>
    </div>
    """
    account_info['qr_code'] = soup.select('.v-box img')[0]['src']
    return account_info


def parse_list(open_id=None, link=None, cookies=None):
    """
        if pass a full link address, apply url to full link address
    """
    url = None
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    if link:
        url = link
    else:
        return None
    html = get_html(url)
    # html = get_html_direct(url, cookies=cookies)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    ls = soup.select('#wxbox .txt-box')
    """
    <div class="txt-box">
        <h4><a class="news_lst_tab zhz" target="_blank" href="/websearch/art.jsp?sg=CBf80b2xkgZWehj5vWa6p7H14bFxHyGAw8mI83NKI1XaytN_OD8yFctpycTXPGOID10f_avp-igWMFJfmYoOs5LyfVPTUowW5Ar6N_4VRwCW_k1bKfg6zJ6yEjmKcYLN&amp;url=p0OVDH8R4SHyUySb8E88hkJm8GF_McJfBfynRTbN8whTDdyB8X8VMQtYHD_ZqIgmFJmAPOq06Mzc3pvRI3iLAGQ3JxMQ33749Bj_jKf9QCAz49DPRRbLQbp8kKPK9fJZBbQVLxWVj6FYy-5x5In7jJFmExjqCxhpkyjFvwP6PuGcQ64lGQ2ZDMuqxplQrsbk" id="sogou_vr_11002601_title_0" title="简书" i="oIWsFt3nvJ2jaaxm9UOB_LUos02k">扒一扒古人的同志情结</a>
        </h4>
        <p id="sogou_vr_11002601_summary_0"> 同志,这是在当今社会无法避开的话题,不管你支持也好,反对也罢,他们一直都在那里.上个月底,台湾举行了一次号称全亚洲最大的同志游行,据说有好几万人,当时气势是出来了,但是很可能就昙花一现,发声过就湮没了.很多人以为同性恋这个现象是从国外舶来,其实不然,...</p>
        <div class="s-p" t="1446629863">17:37</div>
    </div>
    """
    link_list = []
    for item in ls:
        item_dict = {}
        # get item title
        item_dict['title'] = item.h4.text
        # get item address
        item_dict['link'] = item.h4.a['href']
        # get item description
        item_dict['description'] = item.p.text
        # get item update time
        item_dict['updatetime'] = item.div['t']
        link_list.append(item_dict)
    return link_list


def parse_essay(link):
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    try:
        r = s.get(link)
        html = r.text
        soup = BeautifulSoup(html,'html.parser')
        essay = {}
        p = re.compile(r'\?wx_fmt.+?\"')
        content = str(soup.select("#js_content")[0]).replace('data-src', 'src')
        essay['content'] = re.sub(p, '"', content)
        essay['name'] = soup.select('#post-user')[0].text
        essay['date'] = soup.select('#post-date')[0].text
    except Exception:
        return None

    return essay


def weixin_search(name, cookies=None):
    url = BASE_URL + '/weixin?query=' + quote(name)
    html = get_html(url)
    #html = get_html_direct(url, cookies=cookies)
    soup = BeautifulSoup(html,"html.parser")
    ls = soup.select("._item")
    search_list = []
    for item in ls:
        account_info = {}
        account_info['account'] = item.select('h4 span')[0].text.split('：')[1].strip()
        account_info['name'] = item.select('.txt-box h3')[0].text
        account_info['address'] = BASE_URL + item['href']
        account_info['open_id'] = item['href'].split('openid=')[1]
        account_info['description'] = item.select('.sp-txt')[0].text
        account_info['logo'] = item.select('.img-box img')[0]['src']
        try:
            account_info['latest_title'] = item.select('.sp-txt a')[0].text
            account_info['latest_link'] = item.select('.sp-txt a')[0]['href']
        except IndexError:
            pass
        search_list.append(account_info)
        #print(account_info)
    return search_list

def update_cookies():
    s = requests.Session()
    headers = {"User-Agent": UA}
    s.headers.update(headers)
    url = BASE_URL + '/weixin?query=123'
    r = s.get(url)
    if 'SNUID' not in s.cookies:
        p = re.compile(r'(?<=SNUID=)\w+')
        s.cookies['SNUID'] = p.findall(r.text)[0]
        suv = ''.join([str(int(time.time()*1000000) + random.randint(0, 1000))])
        s.cookies['SUV'] = suv
    return s.cookies


if __name__ == '__main__':
    open_id = 'oIWsFt3nvJ2jaaxm9UOB_LUos02k'
    print(weixin_search('简书'))
    cookies = update_cookies()      # request a url to update cookies
    t0 = time.time()
    print(get_account_info(open_id,cookies=cookies))
    # print(weixin_search("简书",cookies))
    t1 = time.time()
    search_list = weixin_search("简书",cookies)
    print(search_list)
    jianshu_url = search_list[0]['address']
    time.sleep(0.5)
    # print(parse_list(open_id, link=jianshu_url, cookies=cookies))
    article_list = parse_list(open_id, link=jianshu_url, cookies=cookies)
    print(article_list)
    t2 = time.time()
    time.sleep(0.5)
    print(parse_essay('http://mp.weixin.qq.com/s?__biz=MjM5NjM4OTAyMA==&mid=205212599&idx=4&sn=6a1de7a7532ba0bcbc633c253b61916f&3rd=MzA3MDU4NTYzMw==&scene=6#rd'))
    t3 = time.time()
    print(t1-t0, t2-t1, t3-t2)
