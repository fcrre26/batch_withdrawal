import logging
import os
from dotenv import load_dotenv
import random
import asyncio

class Config:
    def __init__(self, api_key, api_secret, chain, currency, interval, retry_count, retry_delay):
        self.api_key = api_key
        self.api_secret = api_secret
        self.chain = chain
        self.currency = currency
        self.interval = interval
        self.retry_count = retry_count
        self.retry_delay = retry_delay

async def do_withdrawal(config, withdrawal_info):
    # 实现提现逻辑
    # 这里需要根据您使用的具体API进行实现
    # 示例代码如下:
    try:
        # 使用 config 和 withdrawal_info 进行提现操作
        # 如果提现成功,返回 True
        # 否则, 返回 False
        return True
    except Exception as e:
        logging.error(f"提现失败: {e}")
        return False

async def main():
    # 设置日志配置
    logging.basicConfig(filename='batch_withdrawal.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
        logging.info("用户输入了新的 API key 和 API secret")

    chain = input("请输入主链类型 (例如 BTC、ETH、MATIC): ")
    currency = input("请输入币种 (例如 BTC、ETH、MATIC): ")
    interval = int(input("请输入提现间隔时间(秒): "))
    logging.info(f"用户输入了主链类型: {chain}, 币种: {currency}, 提现间隔时间: {interval} 秒")

    withdrawal_infos = []
    address_amount_pairs = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4b84210a4D44ee2792c03bF76C10c55Cdc71c599,9.77873408780724\n0xbCd519dB657Dbd3A1Fb63C03C51fA86760B3C988,9.81506547392674\n): ").strip().split("\n")
    for pair in address_amount_pairs:
        address, amount = pair.split(",")
        withdrawal_infos.append({
            "address": address.strip(),
            "amount": float(amount.strip())
        })
        logging.info(f"用户输入了提现地址: {address.strip()}, 提现数量: {float(amount.strip())}")

    # 设置默认的重试次数和重试延迟
    retry_count = 3
    retry_delay = 10

    # 让用户选择是否手动输入重试次数和重试延迟
    user_input = input("是否需要手动设置重试次数和重试延迟? (y/n) ")
    if user_input.lower() == 'y':
        retry_count = int(input("请输入重试次数: "))
        retry_delay = int(input("请输入重试延迟(秒): "))
        logging.info(f"用户设置了重试次数: {retry_count}, 重试延迟: {retry_delay} 秒")
    else:
        logging.info(f"使用默认的重试次数: {retry_count}, 重试延迟: {retry_delay} 秒")

    # 创建配置对象
    config = Config(api_key, api_secret, chain, currency, interval, retry_count, retry_delay)

    # 执行提现操作
    for withdrawal_info in withdrawal_infos:
        random_interval = random.uniform(config.interval, config.interval + 20)
        print(f"链类型: {config.chain}, 币种: {config.currency}, 地址: {withdrawal_info['address']}, 数量: {withdrawal_info['amount']}, 间隔时间: {random_interval:.2f} 秒")
        logging.info(f"开始提现: 链类型 {config.chain}, 币种 {config.currency}, 地址 {withdrawal_info['address']}, 数量 {withdrawal_info['amount']}, 间隔时间 {random_interval:.2f} 秒")
        success = await do_withdrawal(config, withdrawal_info)
        if success:
            logging.info(f"提现成功: 地址 {withdrawal_info['address']}, 数量 {withdrawal_info['amount']}, 间隔 {random_interval:.2f}秒")
            print("提现成功")
        else:
            logging.error(f"提现失败: 地址 {withdrawal_info['address']}, 数量 {withdrawal_info['amount']}, 间隔 {random_interval:.2f}秒")
            print("提现失败")
        await asyncio.sleep(random_interval)

if __name__ == "__main__":
    asyncio.run(main())
