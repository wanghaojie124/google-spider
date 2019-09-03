import re
import time
import random

import requests
from selenium import webdriver
import pandas as pd
from pyquery import PyQuery


def random_wait(max_time=20):
    time.sleep(random.randint(4, 8))


def get_name_list():
    name_list_str = r'''james,john,robert,michael,william,david,richard,charles,
joseph,thomas,christopher,daniel,paul,mark,donald,
george,kenneth,steven,edward,brian,ronald,anthony,kevin,
jason,matthew,gary,timothy,jose,larry,jeffrey,frank,
scott,eric,stephen,andrew,raymond,gregory,joshua,jerry,
dennis,walter,patrick,peter,harold,douglas,henry,carl,
arthur,ryan,roger,joe,juan,jack,albert,jonathan,justin,terry,
gerald,keith,samuel,willie,ralph,lawrence,nicholas'''
    name_list = name_list_str.replace('\n', '').split(',')
    return name_list


name_list = get_name_list()


class FindNameAndCount:
    def __init__(self, name_list):
        self.driver = webdriver.Chrome()
        self.name_list = name_list

    def to_target_page(self, name):
        self.driver.get("https://www.google.com/search?q={}".format(name))
        # self.driver.implicitly_wait(20)

    def parse_count_from_page(self):
        item_num_element = self.driver.find_element_by_id("resultStats")
        if not item_num_element:
            raise ValueError("Can't find the element")
        re_rule = r"约 (.*?) 条"
        result = re.findall(re_rule, item_num_element.text)
        if not result:
            raise ValueError("Can't find the text contained the number")
        result = result[0]
        result = result.replace(",", "")

        try:
            num = int(result)
        except ValueError:
            raise ValueError("Parse error!")
        return num

    def get_item_num_by_name(self, name):
        self.to_target_page(name)
        result_num = self.parse_count_from_page()
        print(name, result_num)
        return result_num

    def run(self):
        df = pd.DataFrame(columns=["name", "item_num"])
        n = 1
        for name in self.name_list:
            item_num = self.get_item_num_by_name(name)
            df = df.append({"name": name, "item_num": item_num}, ignore_index=True)
            n += 1
            print("Progress: %s/%s" % (n, len(self.name_list)))
            random_wait()
        df.sort_values(by="item_num", inplace=True, ascending=False)
        df.to_csv("name-count.csv", index=False)


class FindOriginByName:
    def __init__(self, name_list):
        self.source_url = "https://yingwenming.911cha.com/{}.html"
        self.name_list = name_list

    def download_html(self, name):
        url = self.source_url.format(name)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.7 Safari/537.36'}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print("Can't download the page %s" % url)
            return None
        return r.content.decode()

    @staticmethod
    def parse(content):
        pq = PyQuery(content)
        element = pq("span:contains('来源语种')").parent()[0].cssselect("a")[0]
        country_name = element.text
        return country_name

    @staticmethod
    def order_csv():
        df = pd.read_csv("name-country.csv", encoding='gbk', index_col=0)
        for country_name, _df in df.groupby("country_name"):
            df.loc[_df.index, "count"] = _df.shape[0]

        df.sort_values("count", inplace=True, ascending=False)
        df.index = range(df.shape[0])
        df.drop(["count"], axis=1, inplace=True)
        return df.to_csv("name-origin.csv", encoding='gbk', index=False)

    def run(self):
        df = pd.DataFrame(columns=["name", "country_name"])
        n = 1
        for name in self.name_list:
            content = self.download_html(name)
            if not content:
                country_name = "Unknown"
            else:
                country_name = self.parse(content)
            print(name, country_name)
            print("Progress: %s/%s" % (n, len(self.name_list)))
            df = df.append({"name": name, "country_name": country_name}, ignore_index=True)
            n += 1
            random_wait()
        df.to_csv("name-country.csv", encoding='gbk')
        self.order_csv()


def test_find_name_and_item_num():
    fnai = FindNameAndCount(name_list)
    fnai.run()


def test_find_country_by_name():
    fcb = FindOriginByName(name_list)
    fcb.run()


if __name__ == '__main__':
    test_find_name_and_item_num()
    test_find_country_by_name()
