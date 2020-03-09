import uuid
import models
import requests
from selenium import webdriver
import time


def stock_list():
    main_url = 'http://vip.stock.finance.sina.com.cn/mkt/'

    driver = webdriver.Chrome()
    driver.get(main_url)
    driver.implicitly_wait(10)
    lv1 = driver.find_element_by_xpath('//a[text()="申万行业"]')
    lv1.click()

    with open('out.html', 'w', encoding='gb2312') as f:
        f.write(driver.page_source)

    driver.quit()


if __name__ == "__main__":
    # models.db.connect()
    # models.db.create_tables([models.Exchange, models.Market, models.Currency])
    stock_list()
    