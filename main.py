from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
import threading
import time
from pymongo.mongo_client import MongoClient

app = Flask(__name__)

# MongoDB 连接信息
uri = "mongodb+srv://murongweibo2:LOvyPUBn93K6c1EL@cluster0.t2dl2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

# 初始化数据库和集合名称
database_name = "stock_data_db"
collection_name = "stock_data_collection"
db = client[database_name]
collection = db[collection_name]

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
        # 删除旧数据
        collection.delete_many({})
        if data_list:
            collection.insert_many(data_list)
            print("数据采集成功并存储到 MongoDB。")
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
        data_from_db = list(collection.find())
        if not data_from_db:
            return jsonify({"message": "暂无数据"}), 200
        formatted_data = []
        for item in data_from_db:
            formatted_item = {
                "symbol": item["symbol"],
                "time": item["time"],
                "yesterday_close": item["yesterday_close"],
                "today_close": item["today_close"],
                "growth_factor": item["growth_factor"]
            }
            formatted_data.append(formatted_item)
        return jsonify({"data": formatted_data})
    else:
        return jsonify({"error": "Invalid API key"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
