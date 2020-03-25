import requests
from lxml import etree
import time
import json
import tqdm
import random

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

def get_ip_list(page_num):
    ret = []
    page = requests.get(f'https://www.xicidaili.com/nn/{page_num}', headers=headers)
    root = etree.HTML(page.text)
    item_list = root.xpath('//table[@id="ip_list"]//tr[position() > 1]')
    for each_item in item_list:
        ip = each_item.xpath('.//td[2]/text()')
        if len(ip) == 1:
            ip = ip[0].strip()
        else:
            ip = None
        port = each_item.xpath('.//td[3]/text()')
        if len(port) == 1:
            port = int(port[0].strip())
        else:
            port = None

        http_type = each_item.xpath('.//td[6]/text()')
        if len(http_type) == 1:
            http_type = http_type[0].strip()
        else:
            http_type = None
        ret.append({'ip': ip, 'port': port, 'type': http_type})
    
    return ret

def get_proxy_url(proxy_object):
    if proxy_object['type'] == 'HTTP':
        return f'http://{proxy_object["ip"]}:{proxy_object["port"]}/'
    elif proxy_object['type'] == 'HTTPS':
        return f'https://{proxy_object["ip"]}:{proxy_object["port"]}/'
    else:
        return f'http://{proxy_object["ip"]}:{proxy_object["port"]}/'

def test_ip(proxy_object):
    successed = True
    try:
        url = "http://market.finance.sina.com.cn/transHis.php?symbol=sz002061&date=2006-08-16&page=1"
        # 使用代理发送请求，获取响应
        response = requests.get(url, headers=headers, proxies={'http': get_proxy_url(proxy_object)}, timeout=5)
        if response.status_code != 200:
            successed = False
    except BaseException:
        # logger.info("使用代理< " + _get_url(proxy) + " > 请求 < " + url + " > 结果： 失败 ")
        successed = False

    return successed

def load_ips(file_path):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        result.extend(json.loads(f.read()))
    return result

class ProxyPool(object):
    def __init__(self, path='ip.txt'):
        self.pool = load_ips(path)
        
    
    def get_url(self):
        if len(self.pool) == 0:
            return {'ip': '127.0.0.1', 'port': 10805, 'type': 'HTTP'}
        else:
            return random.sample(self.pool, 1)[0]

    def bad_url(self, url_obj):
        if url_obj in self.pool:
            self.pool.remove(url_obj)
        print(f'ip left: {len(self.pool)}')


if __name__ == "__main__":
    result = []
    for i in range(1, 32):
        time.sleep(0.5)
        ip_list = get_ip_list(i)
        for each_ip in ip_list:
            if each_ip['type'] == 'HTTP':
                result.append(each_ip)

    filtered_result = []
    for each_ip in tqdm.tqdm(iterable=result):
        if test_ip(each_ip):
            filtered_result.append(each_ip)

    # write to file
    with open('ip.txt', 'w', encoding='utf-8') as f:
        f.write(json.dumps(filtered_result) + '\n')
        
    
    
