import requests
import json
import time
import datetime
from requests.cookies import RequestsCookieJar
import base64
import re
import urllib.parse

class VietBank:
    def __init__(self):
        self.keyanticaptcha = "b8246038ce1540888c4314a6c043dcae"
        self.cookies = RequestsCookieJar()
        self.session = requests.Session()
        self.accounts_list = []
    def extract_text_from_td(self,td_string):
        return re.sub(r"<[^>]*>", "", td_string).strip()
    def extract_balance_from_td(self,td_string):
        balance_pattern = r"(\d{1,3}(?:,\d{3})*\.\d{2})"
        balances = re.findall(balance_pattern, td_string)
        formatted_balances = [balance.split('.')[0].replace(',', '') for balance in balances]
        return formatted_balances[0]
    def extract_transaction_history(self,html_string):
        html_string = html_string.replace('undefined','').replace(' >','>').replace('< ','<')
        # Define regex pattern to extract transaction rows
        transaction_pattern = r"<tr><td rowspan='2'>(.*?)<br>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr><tr><td colspan='5' style='text-align:center;'>(.*?)</td></tr>"
        # Find all transaction rows
        transactions = re.findall(transaction_pattern, html_string, re.DOTALL)

        # Process each transaction row to create a dictionary
        transaction_history = []
        for transaction in transactions:
            debit = transaction[3].strip() if transaction[3].strip() != '&nbsp;' else '0.00'
            credit = transaction[4].strip() if transaction[4].strip() != '&nbsp;' else '0.00'

            # Convert debit and credit to a unified amount field
            amount = float(credit.replace(',', '')) - float(debit.replace(',', ''))

            transaction_dict = {
                "date": transaction[0].strip(),
                "time": transaction[1].strip(),
                "transaction_id": transaction[2].strip(),
                "amount": amount,
                "balance": transaction[5].strip(),
                "description": transaction[6].strip()
            }
            transaction_history.append(transaction_dict)

        return transaction_history
    def login(self, username, password):
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
        captchaText = self.checkProgressCaptcha(json.loads(task)['taskId'])
        url = "https://online.vietbank.com.vn/ibk/vn/login/verify.jsp"

        payload = 'txtun='+username+'&txtpw='+urllib.parse.quote(password)+'&txtSessID='+captchaText+'&checkbox=on'
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
        if 'Tên truy cập chưa đăng ký sử dụng!' in response.text:
            return {
                'success': False,
                'message': 'Tên truy cập chưa đăng ký sử dụng!'
            }
        elif 'ibk/vn/acctsum' not in response.text:
            return {
                'success': False,
                'message': 'Đăng nhập không thành công!',
                'code': 4011
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
        if 'Đăng nhập không thành công' in response.text:
            return {
                'success': False,
                'message': 'Đăng nhập không thành công!',
                'code': 4012
            }

        if 'Quản lý tài khoản' not in response.text:
            return {
                'success': False,
                'message': 'Đăng nhập không thành công!',
                'code': 4013
            }
        else:
            pattern = r"<tbody>.*<tr>(.*?)\n.*</tbody>"
            tr_elements = re.findall(pattern, response.text, re.DOTALL)
            accounts = []
            for tr in tr_elements:
                # Extract all <td> elements within the <tr>
                td_elements = re.findall(r"<td.*?>(.*?)</td>", tr, re.DOTALL)

                # Create a dictionary for the row data
                row_data = {
                    "account_number": self.extract_text_from_td(td_elements[0]),
                    "balance": self.extract_balance_from_td(td_elements[1]),
                    "status": self.extract_text_from_td(td_elements[5])
                }

                # Add the row data to the extracted data list
                accounts.append(row_data)
                self.accounts_list = accounts
            return {
                'success': True,
                'message': 'Đăng nhập thành công',
                'code': 200,
                'accounts':accounts
            }

    def get_balance(self,account_number):
        for account in self.accounts_list:
            if account.get('account_number') == account_number:
                return {
                    'account_number':account_number,
                    'balance':account.get('balance')
                }
        return None

    def createTaskCaptcha(self, base64_img):
            url = "https://api.anti-captcha.com/createTask"

            payload = json.dumps({
            "clientKey": "f3a44e66302c61ffec07c80f4732baf3",
            "task": {
                "type": "ImageToTextTask",
                "body": base64_img,
                "phrase": False,
                "case": False,
                "numeric": 0,
                "math": False,
                "minLength": 0,
                "maxLength": 0
            },
            "softId": 0
            })
            headers = {
            'Accept': 'application/json',
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

        return self.extract_transaction_history(response.text)

vietbank = VietBank()
username = "0935867473"
password = "Nhi777999#"
fromDate="22-02-2024"
toDate="23-02-2024"
account_number = "000003756036"

session_raw = vietbank.login(username, password)
print(session_raw)

# balance = vietbank.get_balance(account_number)
# print(balance)

history = vietbank.get_transactions(account_number,fromDate,toDate)
print((history))
file_path = "output.json"
with open(file_path, 'w') as json_file:
    json.dump(history, json_file, indent=4)

print(f"JSON data has been saved to {file_path}")