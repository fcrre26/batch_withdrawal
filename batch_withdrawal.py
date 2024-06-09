# -*- coding: utf-8 -*-
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import csv
import time
import datetime
import platform
import subprocess
import sys

def install_dependency(package):
    try:
        __import__(package)
    except ImportError:
        print("需要安装 {} 依赖,正在安装...".format(package))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])

def main():
    # 判断系统版本并安装依赖
    system = platform.system()
    if system == 'Linux':
        install_dependency('gate_api')
    else:
        print("不支持的系统: {}".format(system))
        return

    print(f"您正在使用 Linux 系统,需要安装以下依赖: gate_api")
    input("按回车键继续...")

    # 获取用户输入
    key = input("请输入您的 API key: ")
    secret = input("请输入您的 API secret: ")
    chain = input("请输入主链类型 (例如 BTC、ETH、Polygon): ")
    currency = input("请输入币种 (例如 BTC、ETH、MATIC): ")
    address_amount_pairs = input("请输入提币地址和数量(以逗号分隔,一行一个,例如: \n0x123...,0.1\n0x456...,0.2): ").strip().split("\n")
    interval = int(input("请输入提币间隔时间(秒): "))

    # 将用户输入保存到文件
    filename = f"withdrawal_config_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='') as csv_file:
        fieldnames = ['key', 'secret', 'chain', 'currency']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'key': key, 'secret': secret, 'chain': chain, 'currency': currency})
    print(f"配置信息已保存到文件 {filename}")

    # 配置 APIv4 密钥授权
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4",
        key=key,
        secret=secret
    )

    api_client = gate_api.ApiClient(configuration)
    api_instance = gate_api.WithdrawalApi(api_client)

    # 将提现记录写入文件
    filename = f"withdrawal_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='') as csv_file:
        fieldnames = ['timestamp', 'currency', 'chain', 'address', 'amount', 'status']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        print(f"提现记录将写入文件 {filename}")

    # 执行提币操作
    for address_amount in address_amount_pairs:
        address, amount = address_amount.split(",")
        address = address.strip()
        amount = float(amount.strip())

        # 创建提现记录
        ledger_record = gate_api.LedgerRecord(currency=currency, address=address, amount=amount, chain=chain)

        try:
            # 执行提现
            api_response = api_instance.withdraw(ledger_record)
            record = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': currency,
                'chain': chain,
                'address': address,
                'amount': amount,
                'status': 'Success'
            }
            print(f"提现成功, {currency} {amount} 到 {address}: {api_response}")

            # 将提现记录写入文件
            with open(filename, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(record)

        except GateApiException as ex:
            record = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': currency,
                'chain': chain,
                'address': address,
                'amount': amount,
                'status': f"Failed, label: {ex.label}, message: {ex.message}"
            }
            print(f"Gate API 异常, 标签: {ex.label}, 消息: {ex.message}")

            # 将提现记录写入文件
            with open(filename, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(record)

        except ApiException as e:
            record = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': currency,
                'chain': chain,
                'address': address,
                'amount': amount,
                'status': f"Failed, exception: {e}"
            }
            print(f"调用 WithdrawalApi->withdraw 时出现异常: {e}")

            # 将提现记录写入文件
            with open(filename, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(record)

        # 等待下次提现
        print(f"等待 {interval} 秒后执行下一次提现...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
