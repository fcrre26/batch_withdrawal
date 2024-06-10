import logging
import os
from dotenv import load_dotenv
import time
from decimal import Decimal

class Config:
    def __init__(self, api_key, api_secret, chain, currency, interval, retry_count, retry_delay):
        self.api_key = api_key
        self.api_secret = api_secret
        self.chain = chain
        self.currency = currency
        self.interval = interval
        self.retry_count = retry_count
        self.retry_delay = retry_delay

def do_withdrawal(config, address, amount):
    try:
        # 使用 config 中的信息进行提现操作
        # 这里需要您实现具体的提现逻辑,比如调用第三方 API
        print(f"正在提现 {amount} {config.currency} 至地址 {address}")
        return True
    except Exception as e:
        logging.error(f"提现失败: {e}")
        return False

def main():
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

    chain_type = input("请输入主链类型 (例如 BTC、ETH、MATIC): ")
    coin_type = input("请输入币种 (例如 BTC、ETH、MATIC): ")
    interval = int(input("请输入提现间隔时间(秒): "))
    logging.info(f"用户输入了主链类型: {chain_type}, 币种: {coin_type}, 提现间隔时间: {interval} 秒")

    addresses_and_amounts = []
    address_amount_pairs = input("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4b84210a4D44ee2792c03bF76C10c55Cdc71c599,9.77873408780724\n0xbCd519dB657Dbd3A1Fb63C03C51fA86760B3C988,9.81506547392674\n): ").strip().split("\n")
    for pair in address_amount_pairs:
        address, amount = pair.split(",")
        addresses_and_amounts.append((address.strip(), Decimal(amount.strip())))
        logging.info(f"用户输入了提现地址: {address.strip()}, 提现数量: {Decimal(amount.strip())}")

    # 让用户选择是否手动输入重试次数和重试延迟
    user_input = input("是否需要手动设置重试次数和重试延迟? (y/n) ")
    if user_input.lower() == 'y':
        retry_count = int(input("请输入重试次数: "))
        retry_delay = int(input("请输入重试延迟(秒): "))
        logging.info(f"用户设置了重试次数: {retry_count}, 重试延迟: {retry_delay} 秒")
    else:
        retry_count = 3
        retry_delay = 10
        logging.info(f"使用默认的重试次数: {retry_count}, 重试延迟: {retry_delay} 秒")

    # 创建配置对象
    config = Config(api_key, api_secret, chain_type, coin_type, interval, retry_count, retry_delay)

    # 打印提现信息供用户确认
    logging.info("以下是您的提现信息:")
    logging.info(f"主链类型: {chain_type}")
    logging.info(f"币种: {coin_type}")
    logging.info(f"提现间隔: {interval} 秒")
    logging.info(f"重试次数: {retry_count}")
    logging.info(f"重试延迟: {retry_delay} 秒")
    logging.info("提现地址和数量:")
    for address, amount in addresses_and_amounts:
        logging.info(f"{address} - {amount}")

    # 等待用户确认
    confirm = input("是否继续执行提现操作? (回车继续/其他退出) ")
    if confirm != '':
        exit()

    # 执行提现操作
    for address, amount in addresses_and_amounts:
        for i in range(config.retry_count):
            try:
                if do_withdrawal(config, address, amount):
                    logging.info(f"提现成功至 {address} 数量 {amount}")
                    time.sleep(config.interval)
                    break
                else:
                    logging.error(f"提现失败, 正在重试 ({i+1}/{config.retry_count})")
                    time.sleep(config.retry_delay)
            except Exception as e:
                logging.error(f"提现失败, 正在重试 ({i+1}/{config.retry_count}): {e}")
                time.sleep(config.retry_delay)
                continue
        else:
            logging.error(f"提现至 {address} 数量 {amount} 失败")

if __name__ == "__main__":
    main()
