import logging
import os
from dotenv import load_dotenv
import time
from decimal import Decimal
import random
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# 设置日志配置
logging.basicConfig(filename='batch_withdrawal.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 定义配置类
class Config:
    def __init__(self, api_key, api_secret, chain, currency, interval, retry_count, retry_delay, host):
        self.api_key = api_key
        self.api_secret = api_secret
        self.chain = chain
        self.currency = currency
        self.interval = interval
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.host = host

# 获取 API 密钥和密码
load_dotenv()
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

if not api_key or not api_secret:
    api_key = input("请输入API_KEY: ")
    api_secret = input("请输入API_SECRET: ")

# 配置 APIv4 密钥认证
configuration = gate_api.Configuration(
    host="https://api.gateio.ws/api/v4",
    key=api_key,
    secret=api_secret
)

api_client = gate_api.ApiClient(configuration)
api_instance = gate_api.WithdrawalApi(api_client)

print(f"请输入主链类型 (例如 BTC、ETH、MATIC): ")
chain = input().strip()
print(f"请输入币种 (例如 BTC、ETH、MATIC): ")
currency = input().strip()

retry_count = 2
retry_delay = 10
interval = 10  # 默认10秒

addresses_and_amounts = []
print("请输入提现地址和数量(以逗号分隔,一行一个,例如: \n0x4,9.7\n0x,9.2): ")
while True:
    address_and_amount = input()
    if not address_and_amount:
        break
    address, amount = address_and_amount.split(',')
    addresses_and_amounts.append((address.strip(), Decimal(amount.strip())))

total_addresses = len(addresses_and_amounts)

# 打印提现信息供用户确认
print("\n即将执行以下提现操作:")
print(f"主链: {chain}")
print(f"币种: {currency}")
for address, amount in addresses_and_amounts:
    print(f"地址: {address}, 数量: {amount}")

# 等待用户确认
while True:
    confirm = input("\n请确认无误后输入 'y' 继续, 或者输入 'n' 取消: ")
    if confirm.strip().lower() == 'y':
        break
    elif confirm.strip().lower() == 'n':
        print("取消提现操作。")
        exit()
    else:
        print("输入无效，请重新输入。")

# 让用户输入提现间隔时间
print(f"\n请输入提现间隔时间(秒,默认为 {interval}):")
user_interval = int(input().strip()) or interval

# 再次打印提现信息供用户确认
print("\n即将执行以下提现操作:")
print(f"主链: {chain}")
print(f"币种: {currency}")
for address, amount in addresses_and_amounts:
    print(f"地址: {address}, 数量: {amount}")

# 等待用户最终确认
while True:
    confirm = input("\n确认无误后输入 'y' 开始执行, 或者输入 'n' 取消: ")
    if confirm.strip().lower() == 'y':
        break
    elif confirm.strip().lower() == 'n':
        print("取消提现操作。")
        exit()
    else:
        print("输入无效，请重新输入。")

def do_withdrawal(config, address, amount):
    try:
        withdrawal_response = api_instance.withdraw(currency=config.currency, address=address, amount=float(amount), chain=config.chain)
        transaction_id = withdrawal_response.transaction_id
        status = True
    except GateApiException as ex:
        error_message = f"提现失败: 地址 {address}, 数量 {amount}, 错误代码: {ex.status}, 错误信息: {ex.body}"
        logging.error(error_message)
        print(error_message)
        transaction_id = None
        status = False
    except ApiException as e:
        error_message = f"提现失败: 地址 {address}, 数量 {amount}, 错误: {str(e)}"
        logging.error(error_message)
        print(error_message)
        transaction_id = None
        status = False
    return transaction_id, status

def main():
    config = Config(api_key, api_secret, chain, currency, user_interval, retry_count, retry_delay, "https://api.gateio.ws/api/v4")
    success_count = 0
    failure_count = 0
    for i, (address, amount) in enumerate(addresses_and_amounts):
        print(f"[{i+1}/{total_addresses}] 正在处理 地址: {address}, 数量: {amount}")
        logging.info(f"Processing address {address} with amount {amount}")
        # 生成随机间隔
        random_delay = random.randint(10, 30)
        wait_time = user_interval + random_delay
        print(f"等待 {wait_time} 秒后提现...")
        logging.info(f"Waiting {wait_time} seconds before withdrawal...")
        time.sleep(wait_time)
        transaction_id, status = do_withdrawal(config, address, amount)
        if status:
            print(f"提现成功! 交易ID: {transaction_id}")
            success_count += 1
        else:
            print(f"提现失败...")
            failure_count += 1
    print(f"提现完成, 成功 {success_count} 次, 失败 {failure_count} 次。")

if __name__ == "__main__":
    main()
