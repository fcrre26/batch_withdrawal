import logging
import time
import asyncio
import os
from dotenv import load_dotenv
import sys
import subprocess
import random
import platform

def encrypt(text):
    # 加密函数
    return encrypted_text

async def do_withdrawal(config, withdrawal_info):
    # 执行提现操作
    # 返回 True 表示成功, False 表示失败
    return True

class Config:
    def __init__(self, api_key, api_secret, chain, currency, interval, retry_count, retry_delay):
        self.api_key = api_key
        self.api_secret = api_secret
        self.chain = chain
        self.currency = currency
        self.interval = interval
        self.retry_count = retry_count
        self.retry_delay = retry_delay

def check_and_upgrade_python():
    # 获取当前Python版本
    current_version = sys.version_info.major
    
    # 检查Python版本是否满足要求(3.9或更高)
    if current_version < 3 or current_version < 9:
        print("您的Python版本过低,需要升级到3.9或更高版本。")
        
        # 自动升级Python版本
        if platform.system() == "Windows":
            subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.run(["python", "-m", "pip", "install", "python"])
        else:
            subprocess.run(["sudo", "apt-get", "update"])
            subprocess.run(["sudo", "apt-get", "install", "python3.9"])
            
        print("Python已成功升级,请重新运行脚本。")
        sys.exit()

async def main():
    # 检查并安装依赖库
    dependencies = ['dotenv', 'logging']
    for dependency in dependencies:
        try:
            __import__(dependency)
        except ImportError:
            print(f"正在安装 {dependency} 库...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])

    # 检查是否已经读取过 API 信息
    if 'api_key' in globals() and 'api_secret' in globals():
        print("检测到已经存在 API 信息, 将继续使用.")
    else:
        # 从环境变量加载 API key 和 API secret
        load_dotenv()
        api_key = os.environ.get("API_KEY")
        api_secret = os.environ.get("API_SECRET")

        if not api_key or not api_secret:
            # 如果环境变量中没有找到 API key 和 API secret,则提示用户输入
            api_key = input("请输入您的 API key: ")
            api_secret = input("请输入您的 API secret: ")

            # 将 API 信息保存到环境变量
            os.environ["API_KEY"] = api_key
            os.environ["API_SECRET"] = api_secret

    chain = input("请输入主链类型 (例如 BTC、ETH、MATIC): ")
    currency = input("请输入币种 (例如 BTC、ETH、MATIC): ")
    interval = int(input("请输入提现间隔时间(秒): "))

    withdrawal_infos = []
    address_amount_pairs = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4b84210a4D44ee2792c03bF76C10c55Cdc71c599,9.77873408780724\n0xbCd519dB657Dbd3A1Fb63C03C51fA86760B3C988,9.81506547392674\n): ").strip().split("\n")
    for pair in address_amount_pairs:
        address, amount = pair.split(",")
        withdrawal_infos.append({
            "address": address.strip(),
            "amount": float(amount.strip())
        })

    retry_count = int(input("请输入重试次数: "))
    retry_delay = int(input("请输入重试延迟(秒): "))

    config = Config(api_key, api_secret, chain, currency, interval, retry_count, retry_delay)

    # 加密敏感信息
    encrypted_api_key = encrypt(api_key)
    encrypted_api_secret = encrypt(api_secret)
    logging.info(f"加密后的 API key: {encrypted_api_key}")
    logging.info(f"加密后的 API secret: {encrypted_api_secret}")

    # 测试加密函数
    test_text = "This is a test"
    encrypted_text = encrypt(test_text)
    print(f"原文: {test_text}")
    print(f"加密后: {encrypted_text}")

    # 测试提现操作
    test_withdrawal_info = {
        "address": "0x1234567890abcdef",
        "amount": 10.5
    }
    success = await do_withdrawal(config, test_withdrawal_info)
    if success:
        print("提现测试成功")
    else:
        print("提现测试失败")

    # 执行提现操作
    for withdrawal_info in withdrawal_infos:
        random_interval = random.uniform(config.interval, config.interval + 20)
        print(f"链类型: {chain}, 币种: {currency}, 地址: {withdrawal_info['address']}, 数量: {withdrawal_info['amount']}, 间隔时间: {random_interval:.2f} 秒")
        success = await do_withdrawal(config, withdrawal_info)
        if success:
            logging.info(f"提现成功: 地址 {withdrawal_info['address']}, 数量 {withdrawal_info['amount']}, 间隔 {random_interval:.2f}秒")
        else:
            logging.error(f"提现失败: 地址 {withdrawal_info['address']}, 数量 {withdrawal_info['amount']}, 间隔 {random_interval:.2f}秒")
        await asyncio.sleep(random_interval)

if __name__ == "__main__":
    check_and_upgrade_python()
    asyncio.run(main())
