#!/usr/bin/env python
# coding: utf-8

# get url page: urllib.urlopen(url)
import urllib2
import os
import sys
import json
from HTMLParser import HTMLParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

base_url = "https://bugs.chromium.org"
search_url = base_url + "/p/project-zero/issues/list?&can=1&sort=-reported&q={}"

def expand_shadow_element(driver, element):
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", element)
        return shadow_root

def get_url_content(url=""):
        chrome = True
        if chrome:
                opts = ChromeOptions()
                opts.binary_location="/usr/bin/chromium-browser"
                opts.add_argument("--headless")
                opts.add_argument("--no-sandbox")
                driver = webdriver.Chrome(chrome_options=opts)
        else:
                opts = webdriver.FirefoxOptions()
                #opts.add_argument("-headless")
                driver = webdriver.Firefox(firefox_options=opts)
        driver.get(url)

        body = driver.find_element_by_css_selector("body")
        # everything we need is in body
        mr_app = body.find_element_by_css_selector("mr-app")
        shadow_root0 = expand_shadow_element(driver, mr_app)
        main = shadow_root0.find_element_by_css_selector("main")
        mr_list_page = main.find_element_by_css_selector("mr-list-page")
        shadow_root1 = expand_shadow_element(driver, mr_list_page)

        try:
                mr_issue_list = shadow_root1.find_element_by_css_selector("mr-issue-list")
        except:
                return (None, None, None)

        shadow_root2 = expand_shadow_element(driver, mr_issue_list)
        tbody = shadow_root2.find_element_by_css_selector("tbody")

        # the issue-count is in shadow_root1->list-controls->right-controls
        # the issues are in tbody

        return (driver, shadow_root1, tbody)

class bugs_gpz_class(object):
        def __init__(self, id="", date="", summary="", url="", author="", status="TODO"):
                self.id = id
                self.date = date
                self.summary = summary
                self.url = url
                self.author = author
                self.status = status

def parse_bugs_content(driver, root, tbody):
        bugs_list = []
        do_next = False
        next_url = ""

        tr_eles = tbody.find_elements_by_css_selector("tr")
        for tr_item in tr_eles:
                id = ""
                url = ""
                date = ""
                author = ""
                summary = ""
                td_eles = tr_item.find_elements_by_css_selector("td")
                for td_item in td_eles:
                        class_attr = td_item.get_attribute("class")
                        if class_attr == "col-id":
                                mr_issue_link = td_item.find_element_by_css_selector("mr-issue-link")
                                shadow_rootx = expand_shadow_element(driver, mr_issue_link)
                                a = shadow_rootx.find_element_by_css_selector("a")
                                id = a.text
                                url = a.get_attribute("href")
                        elif class_attr == "col-reported":
                                date = td_item.text
                        elif class_attr == "col-finder":
                                author = td_item.text
                        elif class_attr == "col-summary":
                                summary = td_item.text
                        pass
                bugs_list.append(bugs_gpz_class(id, date, summary, url, author))

        # check if we need to do next page
        list_controls = root.find_element_by_css_selector("div.list-controls")
        right_controls = list_controls.find_element_by_css_selector("div.right-controls")
        try:
                next_a = right_controls.find_element_by_css_selector("a.next-link")
        except:
                return (bugs_list, do_next, next_url)

        next_url = next_a.get_attribute("href")
        do_next = True
        return (bugs_list, do_next, next_url)

def get_bugs_lists(keywords="", outfile=""):
        if keywords == "" or outfile == "":
                print("Need keywords and outfile")
                return 

        url = search_url.format(keywords)
        bugs_json = []

        while True:
                print("Reading URL: %s ..."%(url))
                driver, target_shadow_root, tbody = get_url_content(url)
                print("Reading URL Done.")

                if not driver or not target_shadow_root or not tbody:
                        print("URL content is empty, please try again.")
                        break

                bugs_list, do_next, next_url = parse_bugs_content(driver, target_shadow_root, tbody)
                for item in bugs_list:
                        this_json = {}
                        this_json["BUGS_ID"] = item.id
                        this_json["BUGS_DATE"] = item.date
                        this_json["BUGS_AUTHOR"] = item.author
                        this_json["BUGS_URL"] = item.url
                        this_json["BUGS_DESC"] = item.summary
                        this_json["BUGS_STATUS"] = item.status
                        bugs_json.append(this_json)

                if do_next == False:
                        break
                url = next_url
                driver.close()

        with open(outfile, "w") as f:
                f.write(json.dumps(bugs_json, indent=4))
                print("(%d)JSON format content has been written to %s"%(len(bugs_json), outfile))

def usage(program_name):
        print("Search given keywords in %s, output in JSON format."%(base_url))
        print("Usage:\n\t%s (\"keywords\") [outfile]"%(program_name))

if __name__ == "__main__":
        if (len(sys.argv) != 2) and (len(sys.argv) != 3):
                usage(sys.argv[0])
                sys.exit(-1)

        keywords = sys.argv[1]
        outfile = "/tmp/bugs_list.json"
        if len(sys.argv) == 3:
                outfile = sys.argv[2]

        get_bugs_lists(keywords, outfile)
        sys.exit(0)
