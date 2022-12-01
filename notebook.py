import streamlit as st
import os

col1, col2 = st.columns(2)
def show_txt():
    '''
    渲染输入文本
    '''
    with col2:
        #如果左侧文本框已经提交了输入：
        if st.session_state.get("txt_content"):
            #记录输入到本地文件缓存，用于跨session访问
            with open('cache.txt','w') as cache:
                cache.write(st.session_state.txt_content)
            st.code(st.session_state.txt_content)
        else:
            #判断缓存文件是否存在
            if os.path.exists('cache.txt'):
                with open('cache.txt', 'r') as cache:
                    txt = cache.read()
                    st.code(txt)
#当左侧文本框没有提交输入时，触发：
if not st.session_state.get("txt_content"):
    show_txt()

#每次都触发
with col1:
    submit_button = st.button(label='同步', on_click=show_txt)
    txt = st.text_area('请输入笔记', "",key='txt_content', height = 1000)
    



    



