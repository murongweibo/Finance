import streamlit as st
import os
from streamlit_ace import st_ace
from diskcache import Cache
from loguru import logger
from datetime import datetime
from datetime import timezone, timedelta
import pytz
from contab_run import ContabLogger

def start_contab():
    '''
    开启调度程序
    '''
    os.system('nohup python contab_run.py >/dev/null 2>&1 &')
    

#设置缓存路径
cache_path = './'
st.set_page_config(layout="wide")
logger = ContabLogger(cache_path)
#获取redis数据库密码
password = st.secrets["db_password"]
#保存密码到缓存数据
with Cache(cache_path) as db:
    db.set('db_password', password)
#设置自动刷新时间
from streamlit_autorefresh import st_autorefresh
count = st_autorefresh(interval=1000, limit=1000000000000, key="fizzbuzzcounter")


st.button('开启调度', on_click = start_contab)
#实时刷新日志
txt_content = logger.get_log()
if txt_content:
    st.code(txt_content)
