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

# 执行提现操作
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

    try:
        # 发送提现请求
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        # 记录提现成功日志
        logging.info(f"提现成功: {address} - {amount}")
        return True
    except requests.exceptions.RequestException as e:
        # 记录提现失败日志
        logging.error(f"提现失败: {address} - {amount} - {e}")
        return False

def main():
    # 加载环境变量
    load_dotenv()

    # 输入主链类型、币种和提现间隔时间
    print(f"请输入主链类型 (例如 BTC、ETH、MATIC): ")
    chain = input().strip()
    print(f"请输入币种 (例如 BTC、ETH、MATIC): ")
    currency = input().strip()
    print(f"请输入提现间隔时间(秒): ")
    interval = int(input().strip())

    # 输入提现地址和数量
    addresses_and_amounts = []
    while True:
        address_and_amount = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4b84210a4D44ee2792c03bF76C10c55Cdc71c599,9.77873408780724\n0xbCd519dB657Dbd3A1Fb63C03C51fA86760B3C988,9.81506547392674\n): ")
        if not address_and_amount:
            break
        address, amount = address_and_amount.split(',')
        addresses_and_amounts.append((address.strip(), Decimal(amount.strip())))

    # 创建配置对象
    config = Config(
        api_key=os.getenv("API_KEY", input("请输入API_KEY: ")),
        api_secret=os.getenv("API_SECRET", input("请输入API_SECRET: ")),
        chain=chain,
        currency=currency,
        interval=interval,
        retry_count=3,
        retry_delay=5
    )

    # 批量提现
    for address, amount in addresses_and_amounts:
        for i in range(config.retry_count):
            try:
                # 尝试提现
                success = do_withdrawal(config, address, amount)
                if success:
                    # 记录提现成功日志
                    logging.info(f"提现成功: {address} - {amount}")
                    # 打印提现成功信息
                    print(f"提现成功: {address} - {amount}")
                    break
                else:
                    # 记录提现失败日志
                    logging.error(f"提现失败: {address} - {amount}")
                    # 打印提现失败信息
                    print(f"提现失败: {address} - {amount}")
            except Exception as e:
                # 记录提现出错日志
                logging.error(f"提现出错: {address} - {amount} - {e}")
                # 打印提现出错信息
                print(f"提现出错: {address} - {amount} - {e}")
            # 延迟一段时间再重试
            time.sleep(config.retry_delay)

    # 提醒用户检查日志文件
    print("提现操作已完成,请检查日志文件 'batch_withdrawal.log'。")

if __name__ == "__main__":
    main()
