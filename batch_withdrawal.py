import logging
import os
from dotenv import load_dotenv
import time
from decimal import Decimal
import requests
import random

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

# 获取 API 密钥和密码
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

if not api_key or not api_secret:
    api_key = input("请输入API_KEY: ")
    api_secret = input("请输入API_SECRET: ")

print(f"请输入主链类型 (例如 BTC、ETH、MATIC): ")
chain = input().strip()
print(f"请输入币种 (例如 BTC、ETH、MATIC): ")
currency = input().strip()
print(f"请输入提现间隔时间(秒): ")
interval = int(input().strip())

retry_count = 2
retry_delay = 10

addresses_and_amounts = []
while True:
    address_and_amount = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4b84210a4D44ee2792c03bF76C10c55Cdc71c599,9.77873408780724\n0xbCd519dB657Dbd3A1Fb63C03C51fA86760B3C988,9.81506547392674\n): ")
    if not address_and_amount:
        break
    for line in address_and_amount.splitlines():
        address, amount = line.split(',')
        addresses_and_amounts.append((address.strip(), Decimal(amount.strip())))

total_addresses = len(addresses_and_amounts)
print(f"即将执行以下提现操作:")
print(f"主链: {chain}")
print(f"币种: {currency}")
print(f"提现间隔时间: {interval} 秒 (实际会在 0-{interval//2} 秒内随机)")
for address, amount in addresses_and_amounts:
    print(f"地址: {address}, 数量: {amount}")

print("是否继续执行提现操作? (回车继续/其他退出)")
if input().strip():
    exit()

def do_withdrawal(config, address, amount):
    # 构建 API 请求
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
        logging.error(f"提现出错: {address} - {amount} - {response.status_code}: {response.text}")
        return False

def main():
    config = Config(
        api_key=api_key,
        api_secret=api_secret,
        chain=chain,
        currency=currency,
        interval=interval,
        retry_count=retry_count,
        retry_delay=retry_delay
    )

    processed_addresses = 0

    for address, amount in addresses_and_amounts:
        for i in range(retry_count):
            try:
                success = do_withdrawal(config, address, amount)
                if success:
                    logging.info(f"提现成功: {address} - {amount}")
                    processed_addresses += 1
                    random_interval = random.uniform(0, interval / 2)
                    print(f"已处理 {processed_addresses}/{total_addresses} 个提现地址, 下次提现将在 {random_interval:.2f} 秒后进行")
                    time.sleep(random_interval)
                    break
                else:
                    time.sleep(config.retry_delay)
            except Exception as e:
                logging.error(f"提现出错: {address} - {amount} - {type(e).__name__}: {str(e)}")
                time.sleep(config.retry_delay)

    print(f"提现操作已完成,共处理 {processed_addresses}/{total_addresses} 个地址")

if __name__ == "__main__":
    main()
