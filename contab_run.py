import streamlit as st
import os
from streamlit_ace import st_ace
from diskcache import Cache
from loguru import logger as loguru_logger
from datetime import datetime
from datetime import timezone, timedelta
import pytz
import time

class ContabLogger:
    '''
    定义一个logger,用于记录调度日志
    '''
    def __init__(self, cache_path = None):
        self.cache_path = cache_path    #设置缓存路径

    def info(self, msg):
        '''
        记录1条日志
        '''
        with Cache(self.cache_path) as db:
            loguru_logger.info(msg)
            contab_log = db.get('contab_log') if db.get('contab_log') else ''
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            contab_log += f"{now}-{msg}\n"
            #只保留10000个字符串
            contab_log = '\n'.join(contab_log.split('\n')[-10:])

            #重新更新到缓存管理器
            db.set('contab_log',contab_log)
    def get_log(self):
        '''
        获取当前所有日志
        '''
        with Cache(self.cache_path) as db:
            contab_log = db.get('contab_log')
        return contab_log
        

#本代码用于计算当天均值定投策略
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
      password='cHCNjQ5KJg2NUgjiT3PDbb86uG0kJDJO')

    import json

    r.set(redis_symbol, json.dumps(data))

    get_data = r.get(redis_symbol).decode()
    get_data = json.loads(get_data)
    logger.info(f"云端返回数据：{get_data}")
    
if __name__ == '__main__':
    #设置缓存路径
    cache_path = './'
    logger = ContabLogger(cache_path)
    #获取数据库密码
    with Cache(cache_path) as db:
        password = db.get("db_password")
    #password = st.secrets["db_password"]
    while True:
        try:
            main('sp500', '^GSPC')
            main('hs300', '000300.SS')  
            main('ND300', '^NDX') 
            logger.info(f"执行完成！")
        except :
            error = traceback.format_exc()
            logger.error(error)
        logger.info(f"等待1分钟后执行！")
        time.sleep(60)
