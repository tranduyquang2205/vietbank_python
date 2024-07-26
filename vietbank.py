import requests
import json
import time
import datetime
from requests.cookies import RequestsCookieJar
import base64
import re
import urllib.parse
from bs4 import BeautifulSoup
import os 
class VietBank:
    def __init__(self,username, password, account_number):
        self.keyanticaptcha = "b8246038ce1540888c4314a6c043dcae"
        self.file = f"db/users/{account_number}.json"
        self.cookies_file = f"db/cookies/{account_number}.json"
        self.cookies = RequestsCookieJar()
        self.session = requests.Session()
        self.load_cookies()
        self.accounts_list = {}
        
        self.username = username
        self.password = password
        self.account_number = account_number
        if not os.path.exists(self.file):
            self.username = username
            self.password = password
            self.account_number = account_number
            self.is_login = False
            self.time_login = time.time()
            self.save_data()
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
            self.save_data()
    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'time_login': self.time_login,
            'is_login': self.is_login
        }
        with open(f"db/users/{self.account_number}.json", 'w') as file:
            json.dump(data, file)
    def parse_data(self):
        with open(f"db/users/{self.account_number}.json", 'r') as file:
            data = json.load(file)
            self.username = data['username']
            self.password = data['password']
            self.account_number = data['account_number']
            self.time_login = data['time_login']
            self.is_login = data['is_login']

    def save_cookies(self,cookie_jar):
        # with open(self.cookies_file, 'w') as f:
        #     json.dump(cookie_jar.get_dict(), f)
        cookies = []
        for cookie in self.session.cookies:
            cookies.append({
                'Name': cookie.name,
                'Value': cookie.value,
                'Domain': cookie.domain,
                'Path': cookie.path,
                'Expires': cookie.expires,
                'Secure': cookie.secure,
                'HttpOnly': cookie.has_nonstandard_attr('HttpOnly')
            })
        with open(self.cookies_file, 'w') as file:
            json.dump(cookies, file, indent=4)
    def reset_cookies(self):
        # with open(self.cookies_file, 'w') as f:
        #     json.dump(cookie_jar.get_dict(), f)
        self.init_data()
        cookies = []
        with open(self.cookies_file, 'w') as file:
            json.dump(cookies, file, indent=4)
        self.session.cookies.clear()
    def load_cookies(self):
        # try:
        #     with open(self.cookies_file, 'r') as f:
        #         cookies = json.load(f)
        #         self.cookies = cookies
        #         return
        # except (FileNotFoundError, json.decoder.JSONDecodeError):
        #     return requests.cookies.RequestsCookieJar()
        try:
            with open(self.cookies_file, 'r') as file:
                cookies = json.load(file)
                for cookie in cookies:
                    self.session.cookies.set(cookie['Name'], cookie['Value'])
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return requests.cookies.RequestsCookieJar()
    def extract_text_from_td(self,td_string):
        return re.sub(r"<[^>]*>", "", td_string).strip()
    def extract_balance_from_td(self,td_string):
        balance_pattern = r"(\d{1,3}(?:,\d{3})*\.\d{2})"
        balances = re.findall(balance_pattern, td_string)
        formatted_balances = [balance.split('.')[0].replace(',', '') for balance in balances]
        return formatted_balances[0]
    def extract_account_number(self,html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        ac_element = soup.find('span', class_='me-2')
        if ac_element:
            ac_text = ac_element.get_text(strip=True)
        return (ac_text.strip()) if ac_element else None
    def extract_balance(self,html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        ac_element = soup.find('span', class_='me-2 text-blue')
        if ac_element:
            ac_text = ac_element.get_text(strip=True)
        return float(ac_text.strip().replace('.', '').replace(',','.')) if ac_element else None
    def extract_transaction_history(self,html_string):
        html_content = html_string.replace('undefined','').replace(' >','>').replace('< ','<')
        soup = BeautifulSoup(html_content, 'html.parser')
        transactions = []

        items = soup.find_all('div', class_='item-account-statement')
        for item in items:
            date_time = item.find('p', class_='mb-2 fs-small').text.strip()
            description = item.find('p', class_='fw-bold m-0 text-break').text.strip()
            transaction_code = item.find('span', class_='fw-bold').text.strip()
            amount_element = item.find('p', class_='text-danger m-0 text-end fw-bold') or item.find('p', class_='text-green m-0 text-end fw-bold')
            amount = amount_element.text.strip() if amount_element else 'N/A'
            
            transaction = {
                'date_time': date_time,
                'transaction_id': transaction_code,
                'remark': description,
                'amount': amount
            }
            transactions.append(transaction)

        return transactions
    def login(self):
        self.session = requests.Session()
        url = "https://online.vietbank.com.vn/ibk/vn/login/index.jsp"

        payload = {}
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://online.vietbank.com.vn/ibk/vn/acctsum/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
        }

        response = self.session.get(url, headers=headers, data=payload,allow_redirects=True)
       
        base64_captcha_img = self.getCaptcha()
        task = self.createTaskCaptcha(base64_captcha_img)
        captchaText = json.loads(task)['prediction']
        # print(captchaText)
        url = "https://online.vietbank.com.vn/ibk/vn/login/verify_.jsp"

        payload = 'txtun='+self.username+'&txtpw='+urllib.parse.quote(self.password)+'&txtSessID='+captchaText
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://online.vietbank.com.vn',
        'Connection': 'keep-alive',
        'Referer': 'https://online.vietbank.com.vn/ibk/vn/login/index.jsp',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
        }

        response = self.session.post(url, headers=headers, data=payload)
        if 'Sai mã xác thực!' in response.text:
            return {
                'success': False,
                'message': 'Sai mã xác thực!',
                'code': 421
            } 
        elif 'Tên truy cập chưa đăng ký sử dụng!' in response.text:
            return {
                'success': False,
                'message': 'Tên truy cập chưa đăng ký sử dụng!',
                'code': 404
            }
        elif 'ibk/vn/acctsum' not in response.text:
            return {
                'success': False,
                'message': 'Đăng nhập không thành công!',
                'code': 444
            }
        url = "https://online.vietbank.com.vn/ibk/vn/acctsum/"

        payload = {}
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://online.vietbank.com.vn/ibk/vn/login/verify.jsp',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
        }
        response = self.session.get(url, headers=headers, data=payload)
        self.save_cookies(self.session.cookies)
        # print(response.text)
        if 'Đăng nhập không thành công' in response.text:
            return {
                'success': False,
                'message': 'Đăng nhập không thành công!',
                'code': 400
            }

        if 'Tài khoản thanh toán' not in response.text:
            return {
                'success': False,
                'message': 'Đăng nhập không thành công!',
                'code': 400
            }
        else:
            account_number = self.extract_account_number(response.text)
            balance = self.extract_balance(response.text)
            accounts = {
                "account_number": account_number,
                "balance": balance
            }
            self.accounts_list = accounts
            self.is_login = True
            self.time_login = time.time()
            self.save_data()
            return {
                'success': True,
                'message': 'Đăng nhập thành công',
                'code': 200,
                'accounts':accounts
            }

    def get_balance(self,account_number):
        login = self.login()
        if not login['success']:
            return login
        account = self.accounts_list
        if account.get('account_number'):
            if account.get('account_number') == account_number:
                return {'code':200,'success': True, 'message': 'Thành công',
                                'data':{
                                    'account_number':account_number,
                                    'balance':account.get('balance')
                        }}
            else:
                return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else:
            return {'code':520 ,'success': False, 'message': 'Unknown Error!'} 

    def createTaskCaptcha(self, base64_img):
            url = "https://captcha.pay2world.vip//ibk"
            payload = json.dumps({
            "image_base64": base64_img
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            return(response.text)

    def checkProgressCaptcha(self, task_id):
        url = 'https://api.anti-captcha.com/getTaskResult'
        data = {
            "clientKey": "f3a44e66302c61ffec07c80f4732baf3",
            "taskId": task_id
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = json.loads(response.text)
        if response_json["status"] != "ready":
            time.sleep(1)
            return self.checkProgressCaptcha(task_id)
        else:
            return response_json["solution"]["text"]
    def getCaptcha(self):
        url = 'https://online.vietbank.com.vn/ibk/vn/login/capcha.jsp'
        headers = {}
        response = self.session.get(url, headers=headers)
        return base64.b64encode(response.content).decode('utf-8')

    def get_transactions(self,account_number,fromDate,toDate):
        if not self.is_login or time.time() - self.time_login > 300:
            login = self.login()
            if not login['success']:
                return login
        url = "https://online.vietbank.com.vn/ibk/vn/acctsum/resulttrans.jsp"
        payload = "acctnbr="+account_number+"&tungay="+fromDate+"&denngay="+toDate+"&cboThang=12&cboNam=2024&sorttype=1&kq=1"
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://online.vietbank.com.vn',
        'Connection': 'keep-alive',
        'Referer': 'https://online.vietbank.com.vn/ibk/vn/acctsum/trans.jsp?acctnbr='+account_number,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
        }

        response = self.session.post(url, headers=headers, data=payload)
        transactions =  self.extract_transaction_history(response.text)
        if  transactions:
            return {'code':200,'success': True, 'message': 'Thành công',
                    'data':{
                        'transactions':transactions,
            }}
        else:
            return {'code':200,'success': True, 'message': 'Thành công',
                    'data':{
                        'message': 'No data',
                        'transactions':[],
            }}


