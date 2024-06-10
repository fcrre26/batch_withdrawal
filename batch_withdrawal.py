import logging
import os
from dotenv import load_dotenv
import time
from decimal import Decimal
import requests

# 设置日志配置
logging.basicConfig(filename='batch_withdrawal.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 定义配置类
class Config:
    def __init__(self, api_key, api_secret, chain, currency, interval, retry_count, retry_delay):
        self.api_key = api_key
        self.api_secret = api_secret
        self.chain = chain
        self.currency = currency
        self.interval = interval
        self.retry_count = retry_count
        self.retry_delay = retry_delay

print(f"请输入主链类型 (例如 BTC、ETH、MATIC): ")
chain = input().strip()
print(f"请输入币种 (例如 BTC、ETH、MATIC): ")
currency = input().strip()
print(f"请输入提现间隔时间(秒): ")
interval = int(input().strip())

addresses_and_amounts = []
while True:
    address_and_amount = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4b84210a4D44ee2792c03bF76C10c55Cdc71c599,9.77873408780724\n0xbCd519dB657Dbd3A1Fb63C03C51fA86760B3C988,9.81506547392674\n): ")
    if not address_and_amount:
        break
    address, amount = address_and_amount.split(',')
    addresses_and_amounts.append((address.strip(), Decimal(amount.strip())))

print("是否需要手动设置重试次数和重试延迟? (y/n) 如果是,请输入重试次数和重试延迟(秒),以逗号隔开,例如: y,5,10 (继续执行请直接回车)")
user_input = input().strip()

if user_input:
    parts = user_input.split(',')
    if len(parts) == 3:
        retry_count = int(parts[1].strip())
        retry_delay = int(parts[2].strip())
        if parts[0].lower() == 'y':
            manual_retry = True
        else:
            manual_retry = False
    else:
        print("输入格式有误,请重试")
        return
else:
    retry_count = 3
    retry_delay = 5
    manual_retry = False

print("是否继续执行提现操作? (回车继续/其他退出)")
if input().strip():
    exit()

def do_withdrawal(config, address, amount):
    # 构建API请求
    url = f"https://api.example.com/v1/withdraw"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": config.api_key,
        "X-API-Secret": config.api_secret
    }
    data = {
        "chain": config.chain,
        "currency": config.currency,
        "to_address": address,
        "amount": str(amount)
    }

    # 发送请求
    response = requests.post(url, headers=headers, json=data)

    # 处理响应
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "success":
            return True
        else:
            logging.error(f"提现失败: {address} - {amount} - {result['message']}")
            return False
    else:
        logging.error(f"提现出错: {address} - {amount} - {response.text}")
        return False

def main():
    config = Config(
        api_key=os.getenv("API_KEY", input("请输入API_KEY: ")),
        api_secret=os.getenv("API_SECRET", input("请输入API_SECRET: ")),
        chain=chain,
        currency=currency,
        interval=interval,
        retry_count=retry_count,
        retry_delay=retry_delay
    )

    for address, amount in addresses_and_amounts:
        for i in range(retry_count):
            try:
                success = do_withdrawal(config, address, amount)
                if success:
                    logging.info(f"提现成功: {address} - {amount}")
                    break
                else:
                    logging.error(f"提现失败: {address} - {amount}")
            except Exception as e:
                logging.error(f"提现出错: {address} - {amount} - {e}")
            time.sleep(retry_delay)

if __name__ == "__main__":
    main()
