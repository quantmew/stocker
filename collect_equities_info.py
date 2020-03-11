import uuid
import models
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import time
import json
import random
from datetime import datetime

def get_stock(driver, url):
    stock_obj = {}
    driver.get(url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)
    # 判断url是否有效
    jsxx = tree.xpath('//div[@class="title_bar"]/div/label[text()="检索结果"]')
    if len(jsxx) > 0:
        return None

    # 检查是否退市
    delist = tree.xpath('//div[@id="hq"]/div[@class="price_time"]/div[@id="closed" and text()="已退市"]')
    if len(delist) > 0:
        stock_obj['ListStatus'] = 'D'
    else:
        stock_obj['ListStatus'] = 'L'

    # 基本信息
    if stock_obj['ListStatus'] == 'L':
        stock_obj['StockName'] = tree.xpath('//h1[@id="stockName"]/i[@class="c8_name"]/text()')
    else:
        stock_obj['StockName'] = tree.xpath('//h1[@id="stockName"]/text()')
    if len(stock_obj['StockName']) > 0:
        stock_obj['StockName'] = stock_obj['StockName'][0]
    
    stock_obj['StockNo'] = tree.xpath('//h1[@id="stockName"]/span/text()')
    if len(stock_obj['StockNo']) > 0:
        stock_obj['StockNo'] = stock_obj['StockNo'][0]
        if stock_obj['StockNo'].startswith('(') and stock_obj['StockNo'].endswith(')'):
            stock_obj['StockNo'] = stock_obj['StockNo'][1:-1]

    # 公司概况
    company_panel = tree.xpath('//div[@class="com_overview blue_d"]')
    if len(company_panel) > 0:
        company_panel = company_panel[0]
    CompanyName = company_panel.xpath('.//p/b[contains(text(),"公司名称")]/parent::p/following-sibling::p[1]/text()')
    if len(CompanyName) > 0:
        stock_obj['CompanyName'] = CompanyName[0]
    else:
        stock_obj['CompanyName'] = None

    MainBusiness = company_panel.xpath('.//p/b[contains(text(),"主营业务")]/parent::p/following-sibling::p[1]/text()')
    if len(MainBusiness) > 0:
        stock_obj['MainBusiness'] = MainBusiness[0]
    else:
        stock_obj['MainBusiness'] = None

    Telephone = company_panel.xpath('.//p/b[contains(text(),"电　　话")]/parent::p/text()')
    if len(Telephone) > 0:
        stock_obj['Telephone'] = Telephone[0]
    else:
        stock_obj['Telephone'] = None

    Fax = company_panel.xpath('.//p/b[contains(text(),"传　　真")]/parent::p/text()')
    if len(Fax) > 0:
        stock_obj['Fax'] = Fax[0]
    else:
        stock_obj['Fax'] = None

    SetupDate = company_panel.xpath('.//p/b[contains(text(),"成立日期")]/parent::p/text()')
    if len(SetupDate) > 0:
        stock_obj['SetupDate'] = datetime.strptime(SetupDate[0], '%Y-%m-%d')
    else:
        stock_obj['SetupDate'] = None
        
    
    ListDate = company_panel.xpath('.//p/b[contains(text(),"上市日期")]/parent::p/text()')
    if len(ListDate) > 0:
        stock_obj['ListDate'] = datetime.strptime(ListDate[0], '%Y-%m-%d')
    else:
        stock_obj['ListDate'] = None

    Chairman = company_panel.xpath('.//p/b[contains(text(),"法人代表")]/parent::p/text()')
    if len(Chairman) > 0:
        stock_obj['Chairman'] = Chairman[0]
    else:
        stock_obj['Chairman'] = None

    Manager = company_panel.xpath('.//p/b[contains(text(),"总 经 理")]/parent::p/text()')
    if len(Manager) > 0:
        stock_obj['Manager'] = Manager[0]
    else:
        stock_obj['Manager'] = None

    RegCapital = company_panel.xpath('.//p/b[contains(text(),"注册资本")]/parent::p/text()')
    if len(RegCapital) > 0:
        stock_obj['RegCapital'] = int(float(RegCapital[0].replace('万元', '')) * 10000)

    # 行业板块
    industry_page_url = tree.xpath('//div[@id="louver"]//ul/li/a[text()="所属行业"]/@href')
    if len(industry_page_url) > 0:
        industry_page_url = industry_page_url[0]
    else:
        return stock_obj
    # 跳转到所属行业页面
    driver.get(industry_page_url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)
    industry_name = tree.xpath('//tr/td[text()="所属行业板块"]/parent::tr/following-sibling::tr[2]/td[1]/text()')
    if len(industry_name) > 0:
        industry_name = industry_name[0]
    if industry_name != '':
        stock_obj['IndustryName'] = industry_name

    # 概念板块
    concept_name = tree.xpath('//div[@id="con02-0"]/table[2]/tbody/tr[position()>2]/td[1]/text()')
    # 判断是否有概念板块列表
    if '对不起' in concept_name:
        stock_obj['ConceptName'] = []
    else:
        stock_obj['ConceptName'] = concept_name

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

    random.shuffle(stock_url_list)

    stock_dataset = []
    for each_stock_url in stock_url_list:
        stock_obj = get_stock(driver, each_stock_url)
        if stock_obj is None:
            continue
        stock_dataset.append(stock_obj)

        exchange = models.Exchange.get(models.Exchange.name == '上海证券交易所')
        market = models.Market.get(models.Market.name == '主板')
        # 获取申万行业分类
        sw_industry = models.ShenWanIndustry.get_or_none(
            models.ShenWanIndustry.industry_name == stock_obj['IndustryName'],
            models.ShenWanIndustry.level == 2)

        # 获取或创建股票
        equity, created = models.Equities.get_or_create(
            symbol=stock_obj['StockNo'],
            defaults={
                'uuid': uuid.uuid4(),
                'exchange': exchange,
                'market': market,
                'name': stock_obj['StockName'],
                'list_status': stock_obj['ListStatus'],
                'list_date': stock_obj['ListDate'],
                'company_name': stock_obj['CompanyName'],
                'main_business': stock_obj['MainBusiness'],
                'telephone': stock_obj['Telephone'],
                'fax': stock_obj['Fax'],
                'setup_date': stock_obj['SetupDate'],
                'chairman': stock_obj['Chairman'],
                'manager': stock_obj['Manager'],
                'reg_capital': stock_obj['RegCapital'],
                'industry': sw_industry,
            })
        if not created:
            equity.list_status = stock_obj['ListStatus']
            equity.save()

        # 创建概念板块
        for each_concept_name in stock_obj['ConceptName']:
            concept, created = models.ConceptMarket.get_or_create(
                name=each_concept_name,
                defaults={
                    'uuid': uuid.uuid4()
                })
            # 因为一个股票所属概念会有重复
            models.EquitiesConceptMarket.get_or_create(equity=equity, concept=concept)

    driver.quit()


if __name__ == "__main__":
    # models.db.connect()
    # models.db.create_tables([models.Exchange, models.Market, models.Currency])
    stock_list()
    