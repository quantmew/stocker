import uuid
import models
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import time
import json

def get_stock(driver, url):
    stock_obj = {}
    driver.get(url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)
    stock_obj['StockName'] = tree.xpath('//h1[@id="stockName"]/i[@class="c8_name"]/text()')
    stock_obj['StockNo'] = tree.xpath('//h1[@id="stockName"]/span/text()')

    return stock_obj


# 一级板块搜寻
def stock_lv1(driver):
    url_list = []
    lv1_button = driver.find_element_by_xpath(f'//a[text()="申万行业"]')
    lv1_button.click()

    lv1_list = driver.find_elements_by_xpath(f'//a[text()="申万行业"]/preceding-sibling::div[@class="lv_1"]/dl/dd')

    for each_elem in lv1_list:
        ActionChains(driver)\
            .move_to_element(lv1_button)\
            .click(lv1_button).perform()
        
        ActionChains(driver)\
            .move_to_element(each_elem)\
            .click(each_elem).perform()
        
        driver.implicitly_wait(10)

        while True:
            # 遍历股票列表，获取链接
            tree = etree.HTML(driver.page_source)
            stock_url_list = tree.xpath('//div[@class="tbl_wrap" and @id="tbl_wrap"]/table/tbody/tr/th[@class="sort_down"]/a/@href')
            url_list.extend(stock_url_list)
            # 下一页
            try:
                next_page_button = driver.find_element_by_xpath('//div[@class="pages"]/a[text()="下一页"]')
                next_page_button.click()
                driver.implicitly_wait(3)
            except selenium.common.exceptions.NoSuchElementException:
                break
        
    return url_list

# 二级板块搜寻
def stock_lv2(driver):
    url_list = []
    
    # 获取一级类别
    lv1_button = driver.find_element_by_xpath('//a[text()="申万二级"]')
    ActionChains(driver).move_to_element(lv1_button).click(lv1_button).perform()
    driver.implicitly_wait(10)

    tree = etree.HTML(driver.page_source)
    lv1_list = tree.xpath('//a[text()="申万二级"]/preceding-sibling::div[@class="lv_1"]/dl/dd/a/text()')

    for each_lv1_name in lv1_list:
        each_lv1_elem = driver.find_element_by_xpath(f'//a[text()="申万二级"]/preceding-sibling::div[@class="lv_1"]/dl/dd/a[text()="{each_lv1_name}"]')
        # 获取二级类别
        ActionChains(driver)\
                .move_to_element(lv1_button)\
                .click(lv1_button)\
                .move_to_element(each_lv1_elem)\
                .click(each_lv1_elem).perform()
        lv2_list = driver.find_elements_by_xpath(f'//a[text()="申万二级"]/preceding-sibling::div[@class="lv_1"]/dl/dd/a[text()="{each_lv1_name}"]/preceding-sibling::div[@class="lv_2"]/dl/dd')
        for each_lv2_elem in lv2_list:
            ActionChains(driver)\
                .move_to_element(lv1_button)\
                .click(lv1_button)\
                .move_to_element(each_lv1_elem)\
                .click(each_lv1_elem)\
                .move_to_element(each_lv2_elem)\
                .click(each_lv2_elem).perform()
            
            driver.implicitly_wait(10)

            while True:
                # 遍历股票列表，获取链接
                tree = etree.HTML(driver.page_source)
                stock_url_list = tree.xpath('//div[@class="tbl_wrap" and @id="tbl_wrap"]/table/tbody/tr/th[@class="sort_down"]/a/@href')
                url_list.extend(stock_url_list)
                # 下一页
                try:
                    next_page_button = driver.find_element_by_xpath('//div[@class="pages"]/a[text()="下一页"]')
                    next_page_button.click()
                    driver.implicitly_wait(10)
                except selenium.common.exceptions.NoSuchElementException:
                    break
        
    return url_list

def stock_list():
    main_url = 'http://vip.stock.finance.sina.com.cn/mkt/'

    driver = webdriver.Chrome()
    driver.get(main_url)
    driver.implicitly_wait(10)

    stock_url_list = []
    # 申万行业
    swhy_url_list = stock_lv1(driver)
    stock_url_list.extend(swhy_url_list)
    # 申万二级
    # swej_url_list = stock_lv2(driver)
    # stock_url_list.extend(swej_url_list)

    stock_dataset = []
    for each_stock_url in swhy_url_list:
        stock_obj = get_stock(driver, each_stock_url)
        stock_dataset.append(stock_obj)

    with open('out.txt', 'w', encoding='utf-8') as f:
        for each_stock in stock_dataset:
            f.write(json.dumps(each_stock) + '\n')

    driver.quit()


if __name__ == "__main__":
    # models.db.connect()
    # models.db.create_tables([models.Exchange, models.Market, models.Currency])
    stock_list()
    