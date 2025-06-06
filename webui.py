# 构建一个基于streamlit的web应用
# 页面显示多行，每一行为一个服务器节点，显示内容包括：ip，名称
import json
import streamlit as st
import asyncio
import pandas as pd
import paramiko
import time

from utils import *

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


def load_servers():
    """
    加载服务器列表从本地的文件中
    server_info.json
    :return:
    """
    with open("server_info.json", "r") as f:
        server_list = json.load(f)
    return server_list


def load_config_info():
    """
    加载配置文件信息
    config_info.json
    :return:
    """
    with open("config_info.json", "r") as f:
        config_info = json.load(f)
    return config_info


def init():
    st.session_state.server_list = load_servers()
    st.session_state.server2client = {}
    for server in st.session_state.server_list:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=server["ip"],
            port=22,
            username=server["user"],
            password=server["password"],
        )
        st.session_state.server2client[server["name"]] = client
    st.session_state.config_list = load_config_info()


async def get_servers_gpu_status():
    """
    获取服务器状态
    :return:
    """
    servers_gpu_status = {}
    for server in st.session_state.server_list:
        server_gpu_status = await get_server_gpu_status(
            client=st.session_state.server2client[server["name"]]
        )
        servers_gpu_status[server["name"]] = server_gpu_status
    return servers_gpu_status


async def get_servers_model_status():
    """
    获取服务器上的模型状态
    :return:
    """
    servers_model_status = {}
    for server in st.session_state.server_list:
        server_model_status = await get_server_model_status(
            client=st.session_state.server2client[server["name"]]
        )
        servers_model_status[server["name"]] = server_model_status
    return servers_model_status


async def show_servers():
    """
    显示服务器以及相关信息
    :param servers:
    :return:
    """
    columns_layout = [3, 4, 4]
    # 获取服务器状态
    # gpu
    servers_gpu_status = await get_servers_gpu_status()
    # model
    servers_model_status = await get_servers_model_status()
    col1, col2, col3 = st.columns(columns_layout)
    col1.markdown("## 服务器名称")
    col2.markdown("## GPU状态")
    col3.markdown("## 服务列表")

    for server in st.session_state.server_list:
        # 四列
        # 1：name:user & ip
        # 2: GPU usage: 0% memory: 0% temperature: 0
        # 3: server list
        st.markdown("---")
        col1, col2, col3 = st.columns(columns_layout, vertical_alignment="top")

        with col1:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"### {server['name']}")
            with c2:
                st.markdown(f"**User**: {server['user']}")
                st.markdown(f"**IP**: {server['ip']}")
        with col2:
            df = pd.DataFrame(servers_gpu_status[server["name"]])
            st.dataframe(df.style.set_properties(**{"width": "200px"}))
        with col3:
            df = pd.DataFrame(servers_model_status[server["name"]])
            st.dataframe(df.style.set_properties(**{"width": "200px"}))


async def status_page():
    while True:
        st.title("服务器列表")
        st.write(f"刷新时间: {get_local_time()}")
        await show_servers()
        await asyncio.sleep(60)  # 使用异步sleep
        st.rerun()


async def config_page():
    st.title("配置卡片")
    config_list = st.session_state.config_list
    if not config_list:
        st.warning("没有配置卡片，请添加配置卡片")
        return

    for config in config_list:
        with st.expander(config["name"], expanded=False):
            st.markdown(f"**描述**: {config['description']}")
            st.markdown(f"**依赖镜像**: {', '.join(config['image_depend'])}")
            st.markdown(f"**是否需要GPU**: {'是' if config['if_gpu'] else '否'}")
            st.markdown(f"**允许的服务器**: {', '.join(config['allow_server'])}")
            st.markdown(f"**启动命令**: `{config['start_command']}`")
            st.markdown(f"**停止命令**: `{config['stop_command']}`")


def main():
    init()
    st.markdown(
        """
    <style>
        section[data-testid="stSidebar"] {
            width: 200px !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
    st.sidebar.title("导航")

    page = st.sidebar.radio("---", ["服务器状态", "配置卡片"], index=0)
    if page == "服务器状态":
        # part 1 upload papers
        asyncio.run(status_page())
    elif page == "配置卡片":
        # part 2 show papers
        asyncio.run(config_page())


if __name__ == "__main__":
    main()

# ip 0.0.0.0
# streamlit run webui.py --server.port 8501 --server.address 0.0.0.0
