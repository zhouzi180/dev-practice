#!/usr/bin/python3
import requests
from PIL import Image
from pytesseract import image_to_string
from bs4 import BeautifulSoup
import json
# from flask import *

# app = Flask(__name__)

Basicurl = "http://opac.ncu.edu.cn/reader/redr_verify.php"
Chkurl = "http://opac.ncu.edu.cn/reader/captcha.php"


class LoginUser():
    """docstring for LO"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookies = None
        self.headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://opac.ncu.edu.cn',
            'Referer': 'http://opac.ncu.edu.cn/opac/search.php',
            'Host': 'opac.ncu.edu.cn'
        }

    def get_capture(self):
        chk = requests.get(Chkurl)
        self.chkcookies = chk.cookies
        local = open(
            "./img_cache" + 'PHPSESSID' + ".gif", "wb")
        local.write(chk.content)
        local.close()
        gif = Image.open("./img_cache" + 'PHPSESSID' + ".gif")

        self.Chkcode = image_to_string(gif)

    def login(self):
        self.get_capture()
        post_data = {
            'number': 'username',
            'passwd': 'password',
            'captcha': self.Chkcode,
            'select': 'cert_no',
            'returnUrl': ''
        }
        post_response = requests.post(Basicurl,
                                      headers=self.headers,
                                      cookies=self.chkcookies,
                                      data=post_data
                                      )
        all = requests.get(
            "http://opac.ncu.edu.cn/reader/book_lst.php", cookies=self.chkcookies)
        all.encoding = 'utf-8'
        soup = BeautifulSoup(all.text, "html5lib")
        books = soup.find_all("tr")
        del books[0]
        del books[-1]
        del books[-1]
        book_num = {'books': []}
        for book in books:
            book_json = {}
            book_detail = book.find_all("td")
            book_title = book_detail[1].contents
            book_json["id"] = book_detail[0].text
            book_json["name"] = book_title[0].text
            book_json["author"] = book_title[1].strip(" / ")
            book_json["Borrowing Date"] = book_detail[2].text
            book_json["Return Date"] = book_detail[3].text
            book_json["amount"] = book_detail[4].text
            book_json["location"] = book_detail[5].text
            book_json["attachment"] = book_detail[6].text
            book_num['books'].append(book_json)
        return book_num


user = LoginUser('', '')
page = user.login()
print(page)

