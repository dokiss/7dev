#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cookielib
import urllib2
import urllib
import requests
from urlparse import urlparse
from HTMLParser import HTMLParser
import f

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
def auth(email, password, client_id, scope, client_secret):
    def split_key_value(kv_pair):
        kv = kv_pair.split("=")
        return kv[0]#, kv[1]

    # Authorization form
    def auth_user(email, password, client_id, scope, opener):
        response = opener.open(
            "https://connect.ok.ru/oauth/authorize?" + \
            "redirect_uri=http://api.ok.ru/blank.html&response_type=code&" + \
            "client_id=%s&scope=%s&layout=a" % (client_id, ",".join(scope))
            )
        doc = response.read()
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
    opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
        urllib2.HTTPRedirectHandler())
    doc, url = auth_user(email, password, client_id, scope, opener)
    if urlparse(url).path != "/blank.html":
        # Need to give access to requested scope
        docs, url = give_access(doc, opener)
    if urlparse(url).path != "/blank.html":
        raise RuntimeError("Expected success here")
    if urlparse(url).query.split('=')[0] == 'code':
        code = urlparse(url).query.split('=')[1]
        #client_secret = 'B343067022C770032FBA4408'
        result = auth_user_next(code,client_id,client_secret,opener)
        #print result
    else:
        raise RuntimeError("Code not Find")
   # if "access_token" not in answer or "session_secret_key" not in answer:
   #     raise RuntimeError("Missing some values in answer")
    return result["access_token"]#, result["refresh_token"]
def searcher(query):
    link = "https://m.ok.ru/dk?st.cmd=usersSearch&st.search=%s&st.page=1" % (query)
    print link
    opener = urllib2.build_opener(
    urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
    urllib2.HTTPRedirectHandler())
    response = opener.open("https://m.ok.ru/dk?st.cmd=usersSearch&st.search=%s&st.page=1" % (query))
    doc = response.read()
    parser = FormParser()
    print doc.decode('utf-8')
    parser.feed(doc)
    parser.close()
    # if not parser.form_parsed or parser.url is None or "fr.password" not in parser.params or \
    #   "fr.email" not in parser.params:
    #       raise RuntimeError("Something wrong")
    # parser.params["fr.email"] = email
    # parser.params["fr.password"] = password
    # parser.url = 'https://connect.ok.ru' + parser.url
    # if parser.method == "POST":
    #     response = opener.open(parser.url, urllib.urlencode(parser.params))
    # else:
    #     raise NotImplementedError("Method '%s'" % parser.method)
    # return response.read(), response.geturl()
    return True
login = 'developer.seven@mail.ru'
password = 'white_tiger'
clent_id = '1156316672'
client_access = 'VALUABLE_ACCESS'
client_key = 'CBAPPMOFEBABABABA'
client_secret = 'B343067022C770032FBA4408'
access_token = auth(login, password, clent_id, client_access, client_secret)
query = 'Вильданов%20Ильшат'
searcher(query)
# ok = odnoklassniki.Odnoklassniki(client_key, client_secret, access_token)
# result = ok.friends.get()
# for keys in result.keys():
#     print keys, ':', result[keys]
# result = ok.users.getInfo(uids='574807055017', fields='uid,first_name,last_name,current_location,gender,pic_1,pic_2')
# for keys in result.keys():
#     print keys, ':', result[keys]

