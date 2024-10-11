from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/data', methods=['GET'])
def get_data():
    api_key = request.args.get('api_key')
    if api_key == 'murongweibo':
        today = str(pd.Timestamp.now()).split()[0]
        data_list = []
        for symble, symble_cn in [("^NDX", "纳斯达克100"),
                                   ("^GSPC", "标准普尔500"),
                                   ("000300.SS", "沪深300"),
                                   ]:
            symbol = yf.Ticker(symble)
            hist = symbol.history(start="2020-01-01", end=today)
            hist["time"] = hist.index.map(lambda x: str(x).split()[0])
            hist["yesterday_close"] = hist.Close.shift(1)
            hist["today_close"] = hist.Close
            hist["rolling_mean"] = hist.Close.rolling(240).mean()
            hist["growth_factor"] = (hist.Close - hist.Close.rolling(240).mean()) / hist.Close.rolling(240).mean()
            hist = hist.fillna(0)[-1:]
            data_dict = {
                "symbol": symble_cn,
                "time" : hist["time"].iloc[0],
                "yesterday_close": round(hist["yesterday_close"].iloc[0], 2),
                "today_close": round(hist["today_close"].iloc[0], 2),
                "growth_factor": round(hist["growth_factor"].iloc[0], 2)
            }
            data_list.append(data_dict)
        return jsonify({"data": data_list})
    else:
        return jsonify({"error": "Invalid API key"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
