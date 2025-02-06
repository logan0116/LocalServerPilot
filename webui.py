# 构建一个基于streamlit的web应用
# 页面显示多行，每一行为一个服务器节点，显示内容包括：ip，名称
import json
import streamlit as st
import asyncio
import pandas as pd
import paramiko

from utils import *

st.set_page_config(layout="wide")


def load_servers():
    """
    加载服务器列表从本地的文件中
    server_info.json
    :return:
    """
    with open("server_info.json", "r") as f:
        server_list = json.load(f)
    return server_list


def init():
    st.session_state.server_list = load_servers()
    st.session_state.server2client = {}
    for server in st.session_state.server_list:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=server['ip'],
            port=22,
            username=server['user'],
            password=server['password']
        )
        st.session_state.server2client[server['name']] = client


async def get_servers_gpu_status():
    """
    获取服务器状态
    :return:
    """
    servers_gpu_status = {}
    for server in st.session_state.server_list:
        server_gpu_status = await get_server_gpu_status(client=st.session_state.server2client[server['name']])
        servers_gpu_status[server['name']] = server_gpu_status
    return servers_gpu_status


async def get_servers_model_status():
    """
    获取服务器上的模型状态
    :return:
    """
    servers_model_status = {}
    for server in st.session_state.server_list:
        server_model_status = await get_server_model_status(client=st.session_state.server2client[server['name']])
        servers_model_status[server['name']] = server_model_status
    return servers_model_status


async def show_servers():
    """
    显示服务器以及相关信息
    :param servers:
    :return:
    """
    columns_layout = [1, 3, 3, 1]
    # 获取服务器状态
    # gpu
    servers_gpu_status = await get_servers_gpu_status()
    # model
    servers_model_status = await get_servers_model_status()
    col1, col2, col3, col4 = st.columns(columns_layout)
    col1.markdown("## 服务器名称")
    col2.markdown("## GPU状态")
    col3.markdown("## 服务列表")
    col4.markdown("## 操作")

    for server in st.session_state.server_list:
        # 四列
        # 1：name:user & ip
        # 2: GPU usage: 0% memory: 0% temperature: 0
        # 3: server list
        # 4: add server & delete server
        col1, col2, col3, col4 = st.columns(columns_layout, vertical_alignment="top")

        with col1:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"### {server['name']}")
            with c2:
                st.markdown(f"**User**: {server['user']}")
                st.markdown(f"**IP**: {server['ip']}")
        with col2:
            df = pd.DataFrame(servers_gpu_status[server['name']])
            st.dataframe(df.style.set_properties(**{'width': '200px'}))
        with col3:
            df = pd.DataFrame(servers_model_status[server['name']])
            st.dataframe(df.style.set_properties(**{'width': '200px'}))
        with col4:
            st.write("添加服务")
            st.write("删除服务")


async def main():
    init()
    st.title("服务器列表")
    button = st.button("刷新")
    server_placeholder = st.empty()
    with server_placeholder.container():
        st.write(f"刷新时间: {get_local_time()}")
        await show_servers()
    if button:
        server_placeholder.empty()
        with server_placeholder.container():
            st.write(f"刷新时间: {get_local_time()}")
            await show_servers()


if __name__ == "__main__":
    asyncio.run(main())

# streamlit run webui.py
