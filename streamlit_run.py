import streamlit as st
import json
from loguru import logger

def get_desc(redis_symbol, symbol_cn):
    '''
    获取云端数据，用于后续显示
    '''
    #写入redis
    import redis
    r = redis.Redis(
      host='redis-13066.c290.ap-northeast-1-2.ec2.cloud.redislabs.com',
      port=13066,
      password='cHCNjQ5KJg2NUgjiT3PDbb86uG0kJDJO')

    data = r.get(redis_symbol).decode()
    data = json.loads(data)
    logger.info(f"云端返回数据：{data}")
    time = data["time"].split()[0]
    close = int(data["Close"])
    MA240 = int(data["MA240"])
    BR = data["BR"]
    MPCR = int(data["MPCR"] * 100 ) 
    symbol = symbol_cn
    method = '均值智能定投策略'
    desc = f"跟踪指数：{symbol}\n定投跟踪策略：{method}\n当天时间:{time}\n当天240日移动均值：{MA240}\n当天收盘价:{close}，低于240天均值[{MPCR}%]\n你应该定投：单次定投金额 * {BR} 倍"
    return desc, data


method = '均值智能定投策略'
st.markdown(f"#### {method}")





#标准普尔500指数
symbol = '标准普尔500指数'
redis_symbol = 'sp500'
desc1, data = get_desc(redis_symbol,symbol)
time = data["time"].split()[0]

st.markdown(f"##### 时间：{time}")
st.markdown(" * * *")
col1, col2, col3 = st.columns(3)


close = int(data["Close"])
MA240 = int(data["MA240"])
BR = data["BR"]
MPCR = int(data["MPCR"] * 100 ) 
col1.metric(symbol, f"{BR}倍", f"{MPCR}%")


#纳斯达克100指数
symbol = '纳斯达克100指数'
redis_symbol = 'ND300'
desc2, data = get_desc(redis_symbol,symbol)
time = data["time"].split()[0]
close = int(data["Close"])
MA240 = int(data["MA240"])
BR = data["BR"]
MPCR = int(data["MPCR"] * 100 ) 
col2.metric(symbol, f"{BR}倍", f"{MPCR}%")

#纳斯达克100指数
symbol = '沪深300指数'
redis_symbol = 'hs300'
desc3, data = get_desc(redis_symbol,symbol)
time = data["time"].split()[0]
close = int(data["Close"])
MA240 = int(data["MA240"])
BR = data["BR"]
MPCR = int(data["MPCR"] * 100 ) 
col3.metric(symbol, f"{BR}倍", f"{MPCR}%")


title = desc1.split("\n")[0]
st.markdown(f"* * * \n {title}")
st.code(desc1)

title = desc2.split("\n")[0]
st.markdown(f"* * * \n {title}")
st.code(desc2)

title = desc3.split("\n")[0]
st.markdown(f"* * * \n {title}")
st.code(desc3)