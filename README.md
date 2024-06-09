  批量提币脚本
这个 Python 脚本允许您从您的 Gate.io 账户批量提取加密货币,并将提币详情记录在 CSV 文件中。
  功能
支持批量提取各种加密货币(如 BTC、ETH、MATIC)
自动记录提币详情(时间戳、币种、链类型、地址、数量、状态)到 CSV 文件
可自定义每次提币之间的时间间隔
对提币失败进行错误处理和日志记录

  使用方法
克隆代码仓库: git clone https://github.com/your-username/batch_withdrawal.git
安装所需依赖: pip install -r requirements.txt
运行脚本: python batch_withdrawal.py
按提示输入您的 API key、API secret、链类型、币种、提币地址和数量,以及提币间隔时间。
提币记录将保存在名为 withdrawal_log_YYYYMMDD_HHMMSS.csv 的 CSV 文件中。
  贡献
如果您发现任何问题或有改进建议,欢迎提交 issue 或 pull request。
  许可证
本项目采用 MIT 许可证。
