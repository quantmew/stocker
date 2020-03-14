import uuid
import models
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
import time
import json
import random
import re
import tqdm
from datetime import datetime

def first(lst):
    ret = None
    if len(lst) > 0:
        ret = lst[0]
    return ret

def get_person(driver, url):
    person_obj = {}
    driver.get(url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)

    # 获取信息第一行
    person_obj['name'] = first(tree.xpath('//table[@id="Table1"]/tbody/tr[1]/td[1]/div/text()'))
    person_obj['gender'] = first(tree.xpath('//table[@id="Table1"]/tbody/tr[1]/td[2]/div/text()'))
    person_obj['birth'] = first(tree.xpath('//table[@id="Table1"]/tbody/tr[1]/td[3]/div/text()'))
    person_obj['education'] = first(tree.xpath('//table[@id="Table1"]/tbody/tr[1]/td[4]/div/text()'))
    person_obj['nationality'] = first(tree.xpath('//table[@id="Table1"]/tbody/tr[1]/td[5]/div/text()'))

    second_line = first(tree.xpath('//table[@id="Table1"]/tbody/tr[2]/td[2]/text()'))
    if second_line is not None:
        person_obj['resume'] = second_line.strip()
    else:
        person_obj['resume'] = None
    return person_obj

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

    # 公司资料
    company_info_url = tree.xpath('//div[@id="louver"]//ul/li/a[text()="公司简介"]/@href')
    if len(company_info_url) > 0:
        company_info_url = company_info_url[0]
    else:
        print('error: fail to get company url.')
        return stock_obj
    # 跳转到公司资料页面
    driver.get(company_info_url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)
    # 公司名称
    company_name = tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司名称")]/following-sibling::td/text()')
    if len(company_name) > 0:
        company_name = company_name[0]
    stock_obj['CompanyName'] = company_name

    # 公司英文名称
    company_enname = tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司英文名称")]/following-sibling::td/text()')
    if len(company_enname) > 0:
        company_enname = company_enname[0]
    stock_obj['CompanyEnname'] = company_enname

    # 上市市场
    list_market = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "上市市场")]/following-sibling::td[1]/text()'))
    stock_obj['ListMarket'] = list_market

    # 上市日期
    list_date = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "上市日期")]/following-sibling::td[1]/a/text()'))
    stock_obj['ListDate'] = datetime.strptime(list_date, '%Y-%m-%d')

    # 发行价格
    init_price = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "发行价格")]/following-sibling::td[1]/text()'))
    stock_obj['InitPrice'] = init_price

    # 主承销商
    lead_underwriter = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "主承销商")]/following-sibling::td[1]/a/text()'))
    stock_obj['LeadUnderwriter'] = lead_underwriter

    # 成立日期
    create_date = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "成立日期")]/following-sibling::td[1]/a/text()'))
    stock_obj['CreateDate'] = datetime.strptime(create_date, '%Y-%m-%d')

    # 注册资本
    reg_capital = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "注册资本")]/following-sibling::td[1]/text()'))
    stock_obj['RegCapital'] = reg_capital

    # 机构类型
    organization_type = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "机构类型")]/following-sibling::td[1]/text()'))
    stock_obj['OrganizationType'] = organization_type

    # 组织形式
    organization_form = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "组织形式")]/following-sibling::td[1]/text()'))
    stock_obj['OrganizationForm'] = organization_form

    # 董事会秘书
    board_secretary = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "董事会秘书")]/following-sibling::td[1]/text()'))
    stock_obj['BoardSecretary'] = board_secretary

    # 董秘电话
    board_secretary_telephone = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "董秘电话")]/following-sibling::td[1]/text()'))
    stock_obj['BoardSecretaryTelephone'] = board_secretary_telephone

    # 董秘传真
    board_secretary_fax = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "董秘传真")]/following-sibling::td[1]/text()'))
    stock_obj['BoardSecretaryFax'] = board_secretary_fax

    # 董秘邮箱
    board_secretary_mail = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "董秘电子邮箱")]/following-sibling::td[1]/text()'))
    stock_obj['BoardSecretaryMail'] = board_secretary_mail

    # 公司电话
    company_telephone = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司电话")]/following-sibling::td[1]/text()'))
    stock_obj['CompanyTelephone'] = company_telephone

    # 公司传真
    company_fax = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司传真")]/following-sibling::td[1]/text()'))
    stock_obj['CompanyFax'] = company_fax

    # 公司邮箱
    company_mail = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司电子邮箱")]/following-sibling::td[1]/a/text()'))
    if company_mail is not None:
        stock_obj['CompanyMail'] = company_mail.strip()
    else:
        stock_obj['CompanyMail'] = None

    # 公司网址
    company_website = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司网址")]/following-sibling::td[1]/a/@href'))
    stock_obj['CompanyWebsite'] = company_website

    # 邮政编码
    zip_code = first(tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "邮政编码")]/following-sibling::td[1]/text()'))
    stock_obj['ZipCode'] = zip_code

    # 注册地址
    reg_address = tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "注册地址")]/following-sibling::td[1]/text()')
    if len(reg_address) > 0:
        reg_address = reg_address[0]
    stock_obj['RegAddress'] = reg_address

    # 办公地址
    office_address = tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "办公地址")]/following-sibling::td[1]/text()')
    if len(office_address) > 0:
        office_address = office_address[0]
    stock_obj['OfficeAddress'] = office_address

    # 公司简介
    company_description = tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "公司简介")]/following-sibling::td[1]/text()')
    if len(company_description) > 0:
        company_description = company_description[0]
        stock_obj['CompanyDescription'] = company_description.strip()
    else:
        stock_obj['CompanyDescription'] = None

    # 经营范围
    business_scope = tree.xpath('//div[@id="con02-0"]/table[@id="comInfo1"]//td[contains(text(), "经营范围")]/following-sibling::td[1]/text()')
    if len(business_scope) > 0:
        business_scope = business_scope[0]
    stock_obj['BusinessScope'] = business_scope

    # 公司高管
    company_executives_url = tree.xpath('//div[@id="louver"]//ul/li/a[text()="公司高管"]/@href')
    if len(company_executives_url) > 0:
        company_executives_url = company_executives_url[0]
    else:
        print('error: fail to get company executives url.')
        return stock_obj
    # 跳转到公司高管页面
    driver.get(company_executives_url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)

    # 历届高管成员
    executive_info = []
    executive_lines = tree.xpath('//table[@id="comInfo1"]//th[text()="历届高管成员"]/parent::tr/parent::thead/following-sibling::tbody/tr[position()>1]')
    period_info = ''
    for each_executive in executive_lines:
        # 检查是否是第几届信息
        each_period = each_executive.xpath('.//td[1]/div/text()')
        if len(each_period) > 0 and '起始日期' in each_period[0]:
            period_info = each_period[0]
            continue
        # 收集个人数据
        person_url = first(each_executive.xpath('.//td[1]/div/a/@href'))   

        position = first(each_executive.xpath('.//td[2]/div/text()'))
        start_date = first(each_executive.xpath('.//td[3]/div/text()'))
        if start_date is not None:
            if start_date == '--':
                start_date = None
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = first(each_executive.xpath('.//td[4]/div/text()'))
        if end_date is not None:
            if end_date == '--':
                end_date = None
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        executive_info.append([person_url, position, start_date, end_date, period_info])

    # 历届董事会成员
    period_info = ''
    executive_lines = tree.xpath('//table[@id="comInfo1"]//th[text()="历届董事会成员"]/parent::tr/parent::thead/following-sibling::tbody/tr[position()>1]')
    for each_executive in executive_lines:
        # 检查是否是第几届信息
        each_period = each_executive.xpath('.//td[1]/div/text()')
        if len(each_period) > 0 and '起始日期' in each_period[0]:
            period_info = each_period[0]
            continue
        # 收集任职数据
        person_url = first(each_executive.xpath('.//td[1]/div/a/@href'))   

        position = first(each_executive.xpath('.//td[2]/div/text()'))
        start_date = first(each_executive.xpath('.//td[3]/div/text()'))
        if start_date is not None:
            if start_date == '--':
                start_date = None
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = first(each_executive.xpath('.//td[4]/div/text()'))
        if end_date is not None:
            if end_date == '--':
                end_date = None
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        executive_info.append([person_url, position, start_date, end_date, period_info])

    # 历届监事会成员
    period_info = ''
    executive_lines = tree.xpath('//table[@id="comInfo1"]//th[text()="历届监事会成员"]/parent::tr/parent::thead/following-sibling::tbody/tr[position()>1]')
    for each_executive in executive_lines:
        # 检查是否是第几届信息
        each_period = each_executive.xpath('.//td[1]/div/text()')
        if len(each_period) > 0 and '起始日期' in each_period[0]:
            period_info = each_period[0]
            continue
        # 收集任职数据
        person_url = first(each_executive.xpath('.//td[1]/div/a/@href'))   

        position = first(each_executive.xpath('.//td[2]/div/text()'))
        start_date = first(each_executive.xpath('.//td[3]/div/text()'))
        if start_date is not None:
            if start_date == '--':
                start_date = None
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = first(each_executive.xpath('.//td[4]/div/text()'))
        if end_date is not None:
            if end_date == '--':
                end_date = None
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        executive_info.append([person_url, position, start_date, end_date, period_info])
    
    stock_obj['ExecutiveList'] = executive_info
    # 行业板块
    industry_page_url = tree.xpath('//div[@id="louver"]//ul/li/a[text()="所属行业"]/@href')
    if len(industry_page_url) > 0:
        industry_page_url = industry_page_url[0]
    else:
        print('error: fail to get industry url.')
        return stock_obj
    # 跳转到所属行业页面
    driver.get(industry_page_url)
    driver.implicitly_wait(10)
    tree = etree.HTML(driver.page_source)
    industry_name = tree.xpath('//tr/td[text()="所属行业板块"]/parent::tr/following-sibling::tr[2]/td[1]/text()')
    if len(industry_name) > 0:
        industry_name = industry_name[0]
        stock_obj['IndustryName'] = industry_name
    else:
        stock_obj['IndustryName'] = None

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
            except selenium.common.exceptions.StaleElementReferenceException:
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
    filter_url = False
    for each_stock_url in tqdm.tqdm(iterable=stock_url_list, ascii=True):
        # 过滤已经爬取的url
        # http://biz.finance.sina.com.cn/suggest/lookup_n.php?q=sz000993
        if filter_url:
            m = re.search(r'http://biz\.finance\.sina\.com\.cn/suggest/lookup_n\.php\?q=([a-z]{2})([0-9]{6})', each_stock_url)
            e = models.Equities.get_or_none(
                symbol=f'{m.group(2)}.{m.group(1).upper()}'
            )
            # print(f'skip: {m.group(2)}.{m.group(1).upper()}\n')
            if e is not None:
                continue
        # 开始爬取该股票
        stock_obj = get_stock(driver, each_stock_url)
        if stock_obj is None:
            continue
        stock_dataset.append(stock_obj)

        exchange = models.Exchange.get(models.Exchange.name == '上海证券交易所')
        market = models.Market.get(models.Market.name == '主板')
        # 获取申万行业分类
        sw_industry = None
        if stock_obj['IndustryName'] is not None:
            # 先找二类
            sw_industry = models.ShenWanIndustry.get_or_none(
                models.ShenWanIndustry.industry_name == stock_obj['IndustryName'],
                models.ShenWanIndustry.level == 2)
            # 二类找不到找三类
            if sw_industry is None:
                sw_industry = models.ShenWanIndustry.get_or_none(
                models.ShenWanIndustry.industry_name == stock_obj['IndustryName'],
                models.ShenWanIndustry.level == 3)

        # 获取或创建公司信息
        company, created = models.Company.get_or_create(
            name=stock_obj['CompanyName'],
            defaults={
                'uuid': uuid.uuid4(),
                'enname': stock_obj['CompanyEnname'],
                'market': market,
                'list_date': stock_obj['ListDate'],
                'init_price': stock_obj['InitPrice'],
                'lead_underwriter': stock_obj['LeadUnderwriter'],
                'create_date': stock_obj['CreateDate'],
                'reg_capital': stock_obj['RegCapital'],
                'organization_type': stock_obj['OrganizationType'],
                'organization_form': stock_obj['OrganizationForm'],
                'board_secretary': stock_obj['BoardSecretary'],
                'board_secretary_telephone': stock_obj['BoardSecretaryTelephone'],
                'board_secretary_fax': stock_obj['BoardSecretaryFax'],
                'board_secretary_mail': stock_obj['BoardSecretaryMail'],
                'company_telephone': stock_obj['CompanyTelephone'],
                'company_fax': stock_obj['CompanyFax'],
                'company_mail': stock_obj['CompanyMail'],
                'company_website': stock_obj['CompanyWebsite'],

                'zip_code': stock_obj['ZipCode'],
                'register_address': stock_obj['RegAddress'],
                'office_address': stock_obj['OfficeAddress'],
                'description': stock_obj['CompanyDescription'],
                'business_scope': stock_obj['BusinessScope'],
            })

        if not created:
            company.board_secretary_mail = stock_obj['BoardSecretaryMail']
            company.company_mail = stock_obj['CompanyMail']
            company.company_website = stock_obj['CompanyWebsite']
            company.save()

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
                'company': company,
            })

        # 企业高管信息管理
        # 按照url去重
        person_list = []
        url_dict = {}
        for each_person in stock_obj['ExecutiveList']:
            if each_person[0] not in url_dict:
                url_dict[each_person[0]] = each_person

        for url, each_person in url_dict.items():
            person_list.append(each_person)
        
        # 遍历高管信息
        for each_person in person_list:
            if each_person[0] is None:
                continue
            person_obj = get_person(driver, 'http://vip.stock.finance.sina.com.cn' + each_person[0])
            if person_obj['name'] is None:
                print('person name can not be null, person: ' + str(person_obj))
                continue
            person, created = models.Person.get_or_create(
                name=person_obj['name'],
                gender=person_obj['gender'],
                birth=person_obj['birth'],
                defaults={
                    'uuid': uuid.uuid4(),
                    'education': person_obj['education'],
                    'nationality': person_obj['nationality'],
                    'resume': person_obj['resume'],
                }
            )

            m = re.search('第([0-9]+)届', each_person[4])
            person_period = None
            if m is not None:
                person_period = int(m.group(1))
            job, created = models.Tenure.get_or_create(
                person=person,
                company=company,
                position=each_person[1],
                appointment_date=each_person[2],
                departure_date=each_person[3],
                period=person_period,
                defaults={
                    'uuid': uuid.uuid4(),
                }
            )

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
    