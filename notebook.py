import streamlit as st
import os
from streamlit_ace import st_ace
from diskcache import Cache
from loguru import logger
from datetime import datetime
from datetime import timezone, timedelta
import pytz

def time_ago(time=False):
    """
    获取时间
    """
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    else:
        raise ValueError('invalid date %s of type %s' % (time, type(time)))
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

#设置缓存路径
cache_path = './'
st.set_page_config(layout="wide")

#设置自动刷新时间
from streamlit_autorefresh import st_autorefresh
count = st_autorefresh(interval=1000, limit=1000000000000, key="fizzbuzzcounter")

option = st.selectbox(
    '请选择在线笔记模式：',
    ('查看模式', '编辑模式'))

col1, col2 = st.columns(2)

#第一块区域渲染逻辑
#每次都触发
if option == '编辑模式':
    #submit_button = st.button(label='同步', on_click=show_txt)
    txt = st_ace(key='txt_content', auto_update = True, language = 'python')
    #只有检测到输入的时候，才更新缓存
    if st.session_state.txt_content:
    #logger.info(f"st.session_state.txt_content={st.session_state.txt_content}")
        with Cache(cache_path) as db:
            db.set('txt_content',st.session_state.txt_content)
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            db.set('update_time', now)
            st.success(f'成功更新到云端[更新时间：{now}]', icon="✅")
    
#第二块区域渲染逻辑
if option == '查看模式':

    with Cache(cache_path) as db:
        txt_content = db.get('txt_content')
        
    update_time = db.get('update_time')
    ago = time_ago(update_time)
    st.success(f'update_time : {ago}')
    
    if txt_content:
        st.code(txt_content)
        
    


    



