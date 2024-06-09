# -*- coding: utf-8 -*-
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import csv
import time
import datetime
from pathlib import Path
import platform
import subprocess
import sys
import argparse

def install_dependency(package):
    try:
        __import__(package)
    except ImportError:
        print(f"需要安装 {package} 依赖,正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='批量提现加密货币')
    parser.add_argument('--key', required=True, help='API key')
    parser.add_argument('--secret', required=True, help='API secret')
    parser.add_argument('--chain', required=True, help='主链类型 (例如 BTC、ETH、Polygon)')
    parser.add_argument('--currency', required=True, help='币种 (例如 BTC、ETH、MATIC)')
    parser.add_argument('--addresses', required=True, help='提币地址和数量(以逗号分隔,一行一个,例如: \n0x123...,0.1\n0x456...,0.2)')
    parser.add_argument('--interval', type=int, required=True, help='提币间隔时间(秒)')
    args = parser.parse_args()

    # 判断系统版本并安装依赖
    system = platform.system()
    if system == 'Linux':
        install_dependency('gate_api')
    else:
        print(f"不支持的系统: {system}")
        return

    print(f"您正在使用 Linux 系统,需要安装以下依赖: gate_api")
    input("按回车键继续...")

    # 配置 APIv4 密钥授权
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4",
        key=args.key,
        secret=args.secret
    )

    api_client = gate_api.ApiClient(configuration)
    api_instance = gate_api.WithdrawalApi(api_client)
    account_api = gate_api.AccountApi(api_client)

    # 测试 API 连接
    try:
        balance = account_api.get_user_balance(currency=args.currency)
        print(f"账户 {args.currency} 余额: {balance.available}")
    except (ApiException, GateApiException) as e:
        print(f"连接 API 时出现异常: {e}")
        return

    # 验证提币地址和数量
    address_amount_pairs = args.addresses.strip().split("\n")
    for address_amount in address_amount_pairs:
        address, amount = address_amount.split(",")
        address = address.strip()
        amount = float(amount.strip())
        if amount > float(balance.available):
            print(f"提币数量 {amount} {args.currency} 超过账户可用余额 {balance.available} {args.currency}")
            return

    # 将提现记录写入文件
    log_dir = Path('withdrawal_logs')
    log_dir.mkdir(exist_ok=True)
    filename = log_dir / f"withdrawal_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fieldnames = ['timestamp', 'currency', 'chain', 'address', 'amount', 'status']
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        print(f"提现记录将写入文件 {filename}")

    # 执行提币操作
    for address_amount in address_amount_pairs:
        address, amount = address_amount.split(",")
        address = address.strip()
        amount = float(amount.strip())

        # 创建提现记录
        ledger_record = gate_api.LedgerRecord(currency=args.currency, address=address, amount=amount, chain=args.chain)

        try:
            # 执行提现
            api_response = api_instance.withdraw(ledger_record)
            record = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': args.currency,
                'chain': args.chain,
                'address': address,
                'amount': amount,
                'status': 'Success'
            }
            print(f"提现成功, {args.currency} {amount} 到 {address}: {api_response}")

            # 将提现记录写入文件
            with open(filename, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(record)

        except GateApiException as ex:
            record = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': args.currency,
                'chain': args.chain,
                'address': address,
                'amount': amount,
                'status': f"Failed, label: {ex.label}"
            }
            print(f"提现失败, {args.currency} {amount} 到 {address}: {ex}")

            # 将提现记录写入文件
            with open(filename, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(record)

        time.sleep(args.interval)

if __name__ == '__main__':
    main()
