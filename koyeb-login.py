from playwright.sync_api import sync_playwright
import os
import requests

def send_telegram_message(message):
    bot_token = os.environ.get('TEL_TOK')
    chat_id = os.environ.get('TEL_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()
    
def dingding_bot(title, content):
    bot_token = os.environ.get('DD_TOK')
    bot__id = os.environ.get('DD_SEC')
    timestamp = str(round(time.time() * 1000))  # 时间戳
    secret_enc = DD_BOT_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, bot__id)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
    print('开始使用 钉钉机器人 推送消息...', end='')
    url = f'https://oapi.dingtalk.com/robot/send?access_token={bot_token}&timestamp={timestamp}&sign={sign}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        'msgtype': 'text',
        'text': {'content': f'{title}\n\n{content}'}
    }
    response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=15).json()
    if not response['errcode']:
        print('推送成功！')
    else:
        print('推送失败！')
        
def login_koyeb(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 访问Koyeb登录页面
        page.goto("https://app.koyeb.com/auth/signin")

        # 输入邮箱和密码
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)

        # 点击登录按钮
        page.click('button[type="submit"]')

        # 等待可能出现的错误消息或成功登录后的页面
        try:
            # 等待可能的错误消息
            error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
            if error_message:
                error_text = error_message.inner_text()
                return f"账号 {email} 登录失败: {error_text}"
        except:
            # 如果没有找到错误消息,检查是否已经跳转到仪表板页面
            try:
                page.wait_for_url("https://app.koyeb.com/", timeout=5000)
                return f"账号 {email} 登录成功!"
            except:
                return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('KOY_ACC', '').split()
    login_statuses = []

    for account in accounts:
        email, password = account.split(':')
        status = login_koyeb(email, password)
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "Koyeb登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)
        result = dingding_bot("WEBHOST",message)
        print("消息已发送到DingDing:", result)
    else:
        error_message = "没有配置任何账号"
        send_telegram_message(error_message)
        dingding_bot("WEBHOST",error_message)
        print(error_message)
