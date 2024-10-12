from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import threading
import time
import redis
import json

app = Flask(__name__)

# Redis 连接信息
r = redis.Redis(
    host='redis-15994.c275.us-east-1-4.ec2.redns.redis-cloud.com',
    port=15994,
    password='OYhSfW6XrlfVG4amdFcuZIiFt677jvik'
)

def collect_and_store_data():
    while True:
        today = str(pd.Timestamp.now()).split()[0]
        data_list = []
        for symble, symble_cn in [("^NDX", "纳斯达克 100"),
                                   ("^GSPC", "标准普尔 500"),
                                   ("000300.SS", "沪深 300"),
                                   ]:
            symbol = yf.Ticker(symble)
            hist = symbol.history(start="2020-01-01", end=today)
            if hist.empty:
                continue
            hist["time"] = hist.index.map(lambda x: str(x).split()[0])
            hist["yesterday_close"] = hist.Close.shift(1)
            hist["today_close"] = hist.Close
            hist["rolling_mean"] = hist.Close.rolling(240).mean()
            hist["growth_factor"] = (hist.Close - hist.Close.rolling(240).mean()) / hist.Close.rolling(240).mean()
            hist = hist.fillna(0)[-1:]
            data_dict = {
                "symbol": symble_cn,
                "time": hist["time"].iloc[0],
                "yesterday_close": round(hist["yesterday_close"].iloc[0], 2),
                "today_close": round(hist["today_close"].iloc[0], 2),
                "growth_factor": round(hist["growth_factor"].iloc[0], 2)
            }
            data_list.append(data_dict)
        if data_list:
            r.set('stock_data', json.dumps(data_list))
            print("数据采集成功并存储到 Redis。")
        else:
            print("本次采集未获取到有效数据。")
        time.sleep(3600)  # 每隔一小时采集一次数据

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
        formatted_data = json.loads(data_from_redis)
        return jsonify({"data": formatted_data})
    else:
        return jsonify({"error": "Invalid API key"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
