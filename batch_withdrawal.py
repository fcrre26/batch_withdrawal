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

retry_count = 2
retry_delay = 10

addresses_and_amounts = []
while True:
    address_and_amount = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4,9.7\n0x,9.2): ")
    if not address_and_amount:
        break
    for line in address_and_amount.splitlines():
        address, amount = line.split(',')
        addresses_and_amounts.append((address.strip(), Decimal(amount.strip())))

total_addresses = len(addresses_and_amounts)

# 打印提现信息供用户确认
print("\n即将执行以下提现操作:")
print(f"主链: {chain}")
print(f"币种: {currency}")
for address, amount in addresses_and_amounts:
    print(f"地址: {address}, 数量: {amount}")

# 等待用户确认
print("\n请确认无误后输入 'y' 继续:")
if input().strip().lower() != 'y':
    exit()

# 让用户输入提现间隔时间
print(f"\n请输入提现间隔时间(秒,默认为 {interval}):")
interval = int(input().strip()) or interval

# 再次打印提现信息供用户确认
print("\n即将执行以下提现操作:")
print(f"主链: {chain}")
print(f"币种: {currency}")
print(f"提现间隔时间: {interval} 秒 (实际会在 0-{interval//2} 秒内随机)")
for address, amount in addresses_and_amounts:
    print(f"地址: {address}, 数量: {amount}")

# 等待用户最终确认
print("\n确认无误后输入 'y' 开始执行:")
if input().strip().lower() != 'y':
    exit()

def do_withdrawal(config, address, amount):
    try:
        # 执行提现操作的代码
        # 假设返回一个 transaction_id 和一个 status 标志
        transaction_id = "0x123456789abcdef"
        status = True
        return transaction_id, status
    except Exception as e:
        logging.error(f"提现失败: 地址 {address}, 数量 {amount}, 错误: {str(e)}")
        return None, False

def main():
    config = Config(api_key, api_secret, chain, currency, interval, retry_count, retry_delay)
    success_count = 0
    failure_count = 0
    for i, (address, amount) in enumerate(addresses_and_amounts):
        print(f"[{i+1}/{total_addresses}] 正在处理 地址: {address}, 数量: {amount}")
        transaction_id, status = do_withdrawal(config, address, amount)
        if status:
            print(f"提现成功, 交易ID: {transaction_id}")
            success_count += 1
        else:
            print(f"提现失败, 地址: {address}, 数量: {amount}")
            failure_count += 1
        time.sleep(random.uniform(0, interval/2))
    
    print(f"\n提现总数: {total_addresses}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {failure_count}")

if __name__ == "__main__":
    main()
