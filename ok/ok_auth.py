#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cookielib
import urllib2
import urllib
import requests
from urlparse import urlparse
from HTMLParser import HTMLParser
import odnoklassniki
import lxml.html  as html
import lxml 
from grab import Grab
import urllib
import time
class FormParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = None
        self.params = {}
        self.in_form = False
        self.form_parsed = False
        self.method = "GET"

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "form":
            if self.form_parsed:
                raise RuntimeError("Second form on page")
            if self.in_form:
                raise RuntimeError("Already in form")
            self.in_form = True
        if not self.in_form:
            return
        attrs = dict((name.lower(), value) for name, value in attrs)
        if tag == "form":
            self.url = attrs["action"]
            if "method" in attrs:
                self.method = attrs["method"].upper()
        elif tag == "input" and "type" in attrs and "name" in attrs:
            if attrs["type"] in ["hidden", "text", "password"]:
                self.params[attrs["name"]] = attrs["value"] if "value" in attrs else ""

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "form":
            if not self.in_form:
                raise RuntimeError("Unexpected end of <form>")
            self.in_form = False
            self.form_parsed = True
def auth_user_next(code, client_id, client_secret, opener):
    url = "https://api.odnoklassniki.ru/oauth/token.do?" + \
        "redirect_uri=http://api.ok.ru/blank.html&grant_type=authorization_code&" + \
        "code=%s&client_id=%s&client_secret=%s" % (code, client_id, client_secret)
    r = requests.post(url)
    return r.json()
    # Permission request form
def auth(email, password, client_id, scope, client_secret, opener):
    def split_key_value(kv_pair):
        kv = kv_pair.split("=")
        return kv[0]#, kv[1]

    # Authorization form
    def auth_user(email, password, client_id, scope, opener):
        url = "https://connect.ok.ru/oauth/authorize?" + \
            "redirect_uri=http://api.ok.ru/blank.html&response_type=code&" + \
            "client_id=%s&scope=%s&layout=a" % (client_id, ",".join(scope))
        r = opener.open(url)
        doc = r.read()
        parser = FormParser()
      ##  print doc.decode('utf-8')
        parser.feed(doc)
        parser.close()
        if not parser.form_parsed or parser.url is None or "fr.password" not in parser.params or \
          "fr.email" not in parser.params:
              raise RuntimeError("Something wrong")
        parser.params["fr.email"] = email
        parser.params["fr.password"] = password
        parser.url = 'https://connect.ok.ru' + parser.url
        if parser.method == "POST":
            response = opener.open(parser.url, urllib.urlencode(parser.params))
        else:
            raise NotImplementedError("Method '%s'" % parser.method)
        return response.read(), response.geturl()
    def give_access(doc, opener):
        parser = FormParser()
        parser.feed(doc)
        parser.close()
        parser.url = 'https://connect.ok.ru' + parser.url
        if not parser.form_parsed or parser.url is None:
              raise RuntimeError("Something wrong")
        if parser.method == "POST":
            response = opener.open(parser.url, urllib.urlencode(parser.params))
        else:
            raise NotImplementedError("Method '%s'" % parser.method)
        return response.read(), response.geturl()


    if not isinstance(scope, list):
        scope = [scope]
    doc, url = auth_user(email, password, client_id, scope, opener)
    if urlparse(url).path != "/blank.html":
        # Need to give access to requested scope
        docs, url = give_access(doc, opener)
    if urlparse(url).path != "/blank.html":
        raise RuntimeError("Expected success here")
    if urlparse(url).query.split('=')[0] == 'code':
        code = urlparse(url).query.split('=')[1]
        result = auth_user_next(code,client_id,client_secret,opener)
    else:
        raise RuntimeError("Code not Find")
    return result["access_token"]#, result["refresh_token"]
def searcher(query):
    g = Grab()
    # g.go('http://m.ok.ru')
    g.go('http://www.ok.ru')
    # print g.xpath_text('//title').encode('utf-8')
    # params = {}
    # params["fr.login"] = 'developer.seven@mail.ru'#email
    # params["fr.password"] = 'white_tiger'#password
    # g.setup(post=params, reuse_cookies=True)
    # g.set_input('fr.login','developer.seven@mail.ru')
    # g.set_input('fr.password','white_tiger')
    g.set_input('st.email','developer.seven@mail.ru')
    g.set_input('st.password','white_tiger')
    g.submit()
    # g.go('http://m.ok.ru/dk?st.cmd=usersSearch')
    # query = 'Вильданов Ильшат'
    # print query.encode('utf-8')
    # g.set_input('fr.search',query)
    # g.set_input('st.query',query.encode('utf-8'))
    # g.submit()
    g.go(u'ok.ru/dk?st.cmd=searchResult&'+urllib.urlencode({'st.query':query,'st.mode':'Users'}))
    # &st.bthDay=8 
    # &st.bthMonth=7
    # &st.bthYear=1990
    print g.response.url
    uids = []
    uid = ''
    base_url =  g.response.url
    j=1
    while uid <> None or j==1 :
        g.go(base_url+'&'+urllib.urlencode({'st.page':str(j)}))
        for i in xrange(1,200,1):
            # xpath = '//*[@id="user-list"]/li[' + str(i) +  ']/a/@href'
            # //*[@id="gs_result_list"]/div[200]/div/div/div[2]/div[1]/div[1]/a
            xpath = '//*[@id="gs_result_list"]/div[' + str(i) +  ']/div/div/div[2]/div[1]/div[1]/a/@href'
            uid = g.xpath_number(xpath, default=None)
            if uid == None:
                break
            uids.append(str(uid))
        j+=1
        time.sleep(10)
        print g.response.url
    return uids

login = 'developer.seven@mail.ru'
password = 'white_tiger'
clent_id = '1156316672'
client_access = 'VALUABLE_ACCESS'
client_key = 'CBAPPMOFEBABABABA'
client_secret = 'B343067022C770032FBA4408'
opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
        urllib2.HTTPRedirectHandler())
access_token = auth(login, password, clent_id, client_access, client_secret, opener)
print access_token
query = 'Вильданов Ильшат 25'
uids = searcher(query)
uids =  ','.join(uids)
ok = odnoklassniki.Odnoklassniki(client_key, client_secret, access_token)
result = ok.users.getInfo(uids=uids,fields="first_name,last_name,name,birthday,age,location")
for result_elem in result:
    for key, elem in result_elem.items():
        try:
            elem = elem.encode('utf-8')
        except:
            pass
        print key, elem
    print '--------------------------'
# for keys in enumerate(result):#.keys():
#     print keys, ':', result[keys]
# result = ok.users.getInfo(uids='574807055017', fields='uid,first_name,last_name,current_location,gender,pic_1,pic_2')
# for keys in result[0].keys():
#     print keys, ':', result[keys]

