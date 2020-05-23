#!/usr/bin/env python
# coding: utf-8

# get url page: urllib.urlopen(url)
import urllib2
import os
import sys
import json
from HTMLParser import HTMLParser

# search cve

# NOTE, keyword convert backspace to "+"
# for "linux bpf", the keyword is "linux+bpf"
cve_base_url = "https://cve.mitre.org"
cve_url_f = cve_base_url + "/cgi-bin/cvekey.cgi?keyword={}"

class cve_class(object):
        def __init__(self, id="", desc="", url="", progress="TODO"):
                self.id = id
                self.desc = desc
                self.url = url
                self.progress = progress

def get_url_content(url=""):
        content = urllib2.urlopen(url).read()
        return content

def parse_cve_content(content):
        cve_list = []
        if content == "":
                print("Argument content is empty")
                return cve_list

        # The search result can be filter by "/cgi-bin/cvename.cgi"
        search_key_b = "href=\""
        search_key_e = "/cgi-bin/cvename.cgi?name="
        search_key = search_key_b + search_key_e

        url_key_b = search_key_b
        url_key_e = "\">"
        
        id_key_b = url_key_e
        id_key_e = "</a>"

        desc_key_b = "<td valign=\"top\">"
        desc_key_e = "</td>"

        pos = content
        while True:
                retval = pos.find(search_key)
                if retval == -1:
                        break

                pos = pos[retval:]
                b = pos.find(url_key_b)
                e = pos.find(url_key_e)
                cve_url = pos[b+len(url_key_b):e]
                real_cve_url = HTMLParser().unescape(cve_base_url+cve_url)

                b = pos.find(id_key_b)
                e = pos.find(id_key_e)
                cve_id = pos[b+len(id_key_b):e]

                pos = pos[pos.find(desc_key_b):]
                b = 0
                e = pos.find(desc_key_e)
                cve_desc = pos[b+len(desc_key_b):e]
                real_cve_desc = HTMLParser().unescape(cve_desc)

                cve_list.append(cve_class(cve_id, real_cve_desc, real_cve_url))

                pos = pos[e+len(desc_key_e):]
        return cve_list

def insert(dst_list, newitem, keystr):
        for item in dst_list:
                if item[keystr] == newitem[keystr]:
                        print("Same %s(%s), ignore it."%(keystr, newitem[keystr]))
                        return False
        dst_list.append(newitem)
        return True

def get_cve_lists(keyword="", outfile=""):
        if keyword == "" or outfile == "":
                print("Need a keyword and outfile string")
                return None

        # url = cve_url_f + "+".join(keyword.split())
        url = cve_url_f.format("+".join(keyword.split()))
        print("Reading URL: %s ..."%(url))
        content = get_url_content(url)
        print("Reading URL Done.")

        cve_list = parse_cve_content(content)
        cve_json = []
        try:
                f = open(outfile)
        except:
                pass
        else:
                cve_json = json.load(f)
        orig_len = len(cve_json)

        for item in cve_list:
                this_json = {}
                this_json["CVE_ID"] = item.id
                this_json["CVE_URL"] = item.url
                this_json["CVE_PROGRESS"] = item.progress
                this_json["CVE_DESC"] = item.desc
                this_json["CVE_SEARCH_KEY"] = keyword
                insert(cve_json, this_json, "CVE_ID")

        with open(outfile, "w") as f:
                f.write(json.dumps(cve_json, indent=4))
                print("(new:%d, total:%d) has been written to %s"%(len(cve_json)-orig_len, len(cve_json), outfile))

def usage(program_name):
        print("Search given keywords in %s, output in JSON format."%(cve_base_url))
        print("Usage:\n\t%s (\"keywords\") [outfile]"%(program_name))

if __name__ == "__main__":
        if (len(sys.argv) != 2) and (len(sys.argv) != 3):
                usage(sys.argv[0])
                sys.exit(-1)

        keywords = sys.argv[1]
        outfile = "/tmp/cve-list.json"
        if len(sys.argv) == 3:
                outfile = sys.argv[2]

        get_cve_lists(keywords, outfile)
        sys.exit(0)
