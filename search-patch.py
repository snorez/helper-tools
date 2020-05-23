#!/usr/bin/env python
# coding: utf-8

# get url page: urllib.urlopen(url)
import urllib2
import os
import sys
import json
from HTMLParser import HTMLParser

kernel_url_f = 'https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/log/?h=v{}&qt=grep&q={}'

save_content_idx=0
def save_content(content):
        global save_content_idx
        outf = "/tmp/saved_content_%d"%(save_content_idx)
        with open(outf, "w") as f:
                f.write(content)
                print("Content saved in: %s"%(outf))
        save_content_idx += 1

class patch_class(object):
        def __init__(self, id="", age="", commit_msg="", url="", author="",progress="TODO"):
                self.id = id
                self.age = age
                self.commit_msg = commit_msg
                self.url = url
                self.author = author
                self.progress = progress

def get_url_content(url=""):
        content = urllib2.urlopen(url).read()
        return content

def get_version_list():
        url = "https://www.kernel.org/"
        content = get_url_content(url)
        verlist = []

        key0_b = "<table id=\"releases\">"
        key0_e = "</table>"
        pos_b = content.find(key0_b)
        if pos_b == -1:
                print("releases table not found")
                return verlist
        pos_e = content[pos_b:].find(key0_e)
        if pos_e == -1:
                print("releases table end not found")
                return verlist

        while True:
                key1_b = "<tr"
                key1_e = "</tr>"
                key2_b = "<td><strong>"
                key2_e = "</strong></td>"

                if pos_b >= pos_e:
                        break

                s0 = content[pos_b:]
                b = s0.find(key1_b)
                e = s0.find(key1_e)

                pos_b += e + len(key1_e)

                s1 = s0[b:e]
                b = s1.find(key2_b)
                e = s1.find(key2_e)

                verlist.append(s1[b+len(key2_b):e])
        return verlist

def show_vlist(verlist):
        for item in verlist:
                print("Version: %s"%(item))

def parse_patch_content(content):
        base_url = "https://git.kernel.org"
        patch_list = []
        do_next = False
        next_url = ""

        # the result is in <tr><td><span title= ... </tr>
        s = content
        while True:
                key_b = "<tr><td><span"
                key_e = "</tr>"
                pos_b = s.find(key_b)
                if pos_b == -1:
                        break
                pos_e = s[pos_b:].find(key_e)
                if pos_e == -1:
                        print("%s not found"%(key_e))
                        break
                pos_e += pos_b

                s0 = s[pos_b+len(key_b):pos_e]
                s = s[pos_e+len(key_e):]

                # age
                key0_b = "title='"
                key0_e = "'"
                b = s0.find(key0_b)
                e = s0[b+len(key0_b):].find(key0_e)
                e += b + len(key0_b)
                patch_age = s0[b+len(key0_b):e]

                # url
                s0 = s0[e+len(key0_e):]
                key1_b = "<td><a href='"
                key1_e = "'>"
                b = s0.find(key1_b)
                e = s0.find(key1_e)
                patch_url = s0[b+len(key1_b):e]
                real_patch_url = HTMLParser().unescape(base_url+patch_url)

                # commit_msg
                s0 = s0[e+len(key1_e):]
                b = 0
                key2_e = "</a></td>"
                e = s0.find(key2_e)
                patch_commit_msg = s0[b:e]
                real_commit_msg = HTMLParser().unescape(patch_commit_msg)

                s0 = s0[e+len(key2_e):]
                key3_b = "</span>"
                key3_e = "</td>"
                b = s0.find(key3_b)
                e = s0.find(key3_e)
                patch_author = s0[b+len(key3_b):e]

                patch_id = real_patch_url.split("id=")[1]
                patch_list.append(patch_class(patch_id, patch_age, real_commit_msg,
                                                real_patch_url, patch_author))

        # check if the content contain next page
        s = content
        key_b = "<li><a href='"
        key_e = "'>[next]</a></li>"
        b = s.find(key_b)
        e = s.find(key_e)
        if b != -1 and e != -1:
                next_url = base_url + s[b+len(key_b):e]
                next_url = HTMLParser().unescape(next_url)
                do_next = True

        return (patch_list, do_next, next_url)

def insert(dst_list, newitem, keystr):
        for item in dst_list:
                if item[keystr] == newitem[keystr]:
                        print("Same %s(%s), ignore it."%(keystr, newitem[keystr]))
                        return False
        dst_list.append(newitem)
        return True

def get_patch_lists(version="", keywords="", outfile=""):
        if version == "" or keywords == "" or outfile == "":
                print("Need version and keywords and outfile")
                return

        url = kernel_url_f.format(version,"+".join(keywords.split()))
        patch_json = []
        try:
                f = open(outfile)
        except:
                pass
        else:
                patch_json = json.load(f)
        orig_len = len(patch_json)

        while True:
                print("Reading URL: %s ..."%(url))
                content = get_url_content(url)
                print("Reading URL Done.")

                if not content or content == "":
                        print("content is empty")
                        continue

                save_content(content)

                patch_list, do_next, next_url = parse_patch_content(content)
                for item in patch_list:
                        this_json = {}
                        this_json["PATCH_ID"] = item.id
                        this_json["PATCH_AGE"] = item.age
                        this_json["PATCH_URL"] = item.url
                        this_json["PATCH_PROGRESS"] = item.progress
                        this_json["PATCH_COMMIT_MSG"] = item.commit_msg
                        this_json["PATCH_AUTHOR"] = item.author
                        insert(patch_json, this_json, "PATCH_ID")

                if do_next == False:
                        break
                url = next_url

        with open(outfile, "w") as f:
                f.write(json.dumps(patch_json, indent=4))
                print("(new:%d, total:%d)has been written to %s"%(len(patch_json)-orig_len, len(patch_json), outfile))

def usage(name):
        print("Search given keywords in git.kernel.org, output in JSON format.")
        print("Usage:\n\t%s (version) (\"keywords\") [outfile]"%(name))

if __name__ == "__main__":
        if len(sys.argv) != 1 and len(sys.argv) != 3 and len(sys.argv) != 4:
                usage(sys.argv[0])
                sys.exit(-1)

        if len(sys.argv) == 1:
                vlist = get_version_list()
                show_vlist(vlist)
                print("Please rerun this with a version.")
                usage(sys.argv[0])
                sys.exit(0)

        version = sys.argv[1]
        keywords = sys.argv[2]
        outfile = "/tmp/patch-list.json"
        if len(sys.argv) == 4:
                outfile = sys.argv[3]

        get_patch_lists(version, keywords, outfile)

        sys.exit(0)
