#本代码用于计算当天均值定投策略
from loguru import logger
import time
from tqdm import tqdm
import traceback
import streamlit as st
password = st.secrets["db_password"]
def main(redis_symbol, symbol):
    '''
    定义主方法
    '''
    logger.info(f"开始获取数据...")
    import yfinance as yf
    ticket = yf.Ticker(symbol)
    #logger.info(f"ticket={ticket.info}")
    hist = ticket.history(period="250D")
    logger.info(f"data_size:{len(hist)}")
    hist['MA240'] = hist.rolling(window = 240)['Close'].mean()
    hist['MPCR'] = (hist['MA240'] - hist['Close']) / hist['MA240']
    hist['time'] = hist.index.map(str)
    data = hist[['time','Close','MA240','MPCR']][-1:].to_dict(orient = 'records')[0]
    option_mapper = {0.4:3000,0.3:2600,0.2:2200,0.1:1800,0.05:1400,0:1000 }
    threshood = [0, 0.05, 0.1, 0.2, 0.3 , 0.4]
    BR = 1.0

    for key in threshood:
        value = option_mapper[key]
        if data['MPCR'] > key:
            data['BR'] = value / 1000.0
    logger.info(f"当天定投数据为：{data}")

    #写入redis
    import redis
    r = redis.Redis(
      host='redis-13066.c290.ap-northeast-1-2.ec2.cloud.redislabs.com',
      port=13066,
      password=password)

    import json

    r.set(redis_symbol, json.dumps(data))

    get_data = r.get(redis_symbol).decode()
    get_data = json.loads(get_data)
    logger.info(f"云端返回数据：{get_data}")
    
if __name__ == '__main__':
    while True:
        try:
            main('sp500', '^GSPC')
            main('hs300', '000300.SS')  
            main('ND300', '^NDX') 
            logger.warning(f"执行完成！")
        except :
            error = traceback.format_exc()
            logger.error(error)
        logger.warning(f"等待1分钟后执行！")
        time.sleep(60)
        #with tqdm(total=60) as pbar:
        #    for i in range(60):
        #        time.sleep(1)
        #        pbar.update(1)
