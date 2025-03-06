from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import threading
import time
import redis
import json
from datetime import timedelta
from datetime import datetime

app = Flask(__name__)

# Redis 连接信息
r = redis.Redis(
    host='redis-18691.c244.us-east-1-2.ec2.redns.redis-cloud.com',
    port=18691,
    password='OwIVtHpUb1hGBYsv94Vz5CNpnrzIVIJP'
)

def collect_and_store_data():
    while True:
        # 获取当前日期
        today = str(pd.Timestamp.now()).split()[0]
        # 将当前日期加上一天
        new_today = pd.Timestamp(today) + timedelta(days=1)
        new_today_str = str(new_today).split()[0]
        data_list = []
        for symble, symble_cn in [("^NDX", "纳斯达克 100"),
                                   ("^GSPC", "标准普尔 500"),
                                   ("000300.SS", "沪深 300"),
                                  ("CVX", "雪佛龙"),
                                  ("KO", "可口可乐"),
                                   ]:
            symbol = yf.Ticker(symble)
            print(f"new_today_str={new_today_str}")			   
            hist = symbol.history(start="2020-01-01", end=new_today_str)
            if hist.empty:
                continue
            hist["time"] = hist.index.map(lambda x: str(x).split()[0])
            hist["yesterday_close"] = hist.Close.shift(1)
            hist["today_close"] = hist.Close
            hist["rolling_mean"] = hist.Close.rolling(240).mean()
            hist = hist.fillna(0)[-1:]
            yesterday_close = hist["yesterday_close"].iloc[0]
            today_close = hist["today_close"].iloc[0]
            change = (today_close - yesterday_close) / yesterday_close if yesterday_close!= 0 else 0
            change_percentage = round(change * 100, 2)
            growth_factor = (today_close - hist["rolling_mean"].iloc[0]) / hist["rolling_mean"].iloc[0] if hist["rolling_mean"].iloc[0]!= 0 else 0
            growth_percentage = round(growth_factor * 100, 2)
            data_dict = {
                "symbol": symble_cn,
                "time": hist["time"].iloc[0],
                "yesterday_close": round(hist["yesterday_close"].iloc[0], 2),
                "today_close": round(hist["today_close"].iloc[0], 2),
                "change_percentage": f"{change_percentage}%",
                "growth_percentage": f"{growth_percentage}%"
            }
            data_list.append(data_dict)
        if data_list:
            formatted_data_str = ""
            for data in data_list:
                formatted_data_str += f"• {data['symbol']}（时间：{data['time']}）: 昨日收盘价 {data['yesterday_close']}, 今日收盘价 {data['today_close']}, 涨跌幅为 {data['change_percentage']}, 与 240 天均值相比变化为 {data['growth_percentage']}。\n"
            formatted_data_str = f'''****定投策略参考信息****\n{formatted_data_str}\n\n****定投金额倍数规则说明****
当与 240 均值比较跌幅时，定投金额倍数按以下规则确定：
	• 若跌幅达到 40%，定投倍数为 3 倍。
	• 跌幅为 30% 时，定投倍数为 2.6 倍。
	• 跌幅为 20% 时，定投倍数为 2.2 倍。
	• 跌幅为 10% 时，定投倍数为 1.8 倍。
	• 跌幅为 5% 时，定投倍数为 1.4 倍。
当未跌或跌幅在 0% 以内时，定投倍数为 1 倍。'''
            #增加json格式数据的存储
            r.set('stock_data_json', json.dumps(data_list))
            r.set('stock_data', formatted_data_str)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"数据采集成功并存储到 Redis。当前时间：{current_time}")
        else:
            print("本次采集未获取到有效数据。")
        time.sleep(120)  # 每隔一小时采集一次数据

data_thread = threading.Thread(target=collect_and_store_data)
data_thread.start()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/data', methods=['GET'])
def get_data():
    api_key = request.args.get('api_key')
    if api_key == 'murongweibo':
        data_from_redis = r.get('stock_data')
        if not data_from_redis:
            return jsonify({"message": "暂无数据"}), 200
        return data_from_redis.decode().replace("\n","<br>")
    else:
        return jsonify({"error": "Invalid API key"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
