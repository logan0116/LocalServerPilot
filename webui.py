# 构建一个基于streamlit的web应用
# 页面显示多行，每一行为一个服务器节点，显示内容包括：ip，名称
import json
import streamlit as st
import asyncio
import pandas as pd
import paramiko
import time

from utils import *

st.set_page_config(
    page_title="Local Server Pilot",
    layout="wide",
    initial_sidebar_state="collapsed",
)


class Server:
    def __init__(self, name, ip, user, password):
        self.name = name
        self.ip = ip
        self.user = user
        self.password = password
        self.client = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.ip, port=22, username=self.user, password=self.password
        )

    def close(self):
        if self.client:
            self.client.close()


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


server_info_list = load_servers()

server_list = []
for server_info in server_info_list:
    server = Server(
        name=server_info["name"],
        ip=server_info["ip"],
        user=server_info["user"],
        password=server_info["password"],
    )
    server_list.append(server)

config_list = load_config_info()


async def get_servers_gpu_status():
    """
    获取服务器状态
    :return:
    """
    servers_gpu_status = {}
    for server in server_list:
        server.connect()
        server_gpu_status = await get_server_gpu_status(client=server.client)
        server.close()
        servers_gpu_status[server.name] = server_gpu_status
    return servers_gpu_status


async def get_servers_model_status():
    """
    获取服务器上的模型状态
    :return:
    """
    servers_model_status = {}
    for server in server_list:
        server.connect()
        server_model_status = await get_server_model_status(client=server.client)
        server.close()
        servers_model_status[server.name] = server_model_status
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

    for server in server_list:
        # 四列
        # 1：name:user & ip
        # 2: GPU usage: 0% memory: 0% temperature: 0
        # 3: server list
        st.markdown("---")
        col1, col2, col3 = st.columns(columns_layout, vertical_alignment="top")

        with col1:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"### {server.name}")
            with c2:
                st.markdown(f"**User**: {server.user}")
                st.markdown(f"**IP**: {server.ip}")
        with col2:
            df = pd.DataFrame(servers_gpu_status[server.name])
            st.dataframe(df.style.set_properties(**{"width": "200px"}))
        with col3:
            df = pd.DataFrame(servers_model_status[server.name])
            st.dataframe(df.style.set_properties(**{"width": "200px"}))


async def status_page():
    while True:
        st.title("服务器列表")
        st.write(f"刷新时间: {get_local_time()}")
        await show_servers()
        await asyncio.sleep(15)  # 使用异步sleep
        st.rerun()


async def config_page():
    st.title("配置卡片")
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


async def start_service():
    """
    启动服务界面

    整体思路是：

    1.配置服务器
    2.服务模型
    3.操作

    """
    st.title("服务管理")

    st.markdown("### 选择服务器")
    server_names = [server.name for server in server_list]
    selected_server_name = st.selectbox(
        "服务器", server_names, key="start_service_server", label_visibility="collapsed"
    )
    server_index = server_names.index(selected_server_name)

    st.markdown("### 选择服务")
    available_configs = [
        c for c in config_list if selected_server_name in c["allow_server"]
    ]
    config_names = [c["name"] for c in available_configs]
    selected_config = st.selectbox(
        "服务配置",
        config_names,
        key="start_service_config",
        label_visibility="collapsed",
    )

    st.markdown("### 操作")
    config = next(c for c in available_configs if c["name"] == selected_config)

    if st.button("启动服务"):
        try:
            server_list[server_index].connect()
            stdin, stdout, stderr = server_list[server_index].client.exec_command(
                config["start_command"]
            )
            output = stdout.read().decode()
            st.success(f"服务启动成功:\n{output}")
        except Exception as e:
            st.error(f"启动失败: {str(e)}")
        finally:
            server_list[server_index].close()

    if st.button("停止服务"):
        try:
            server_list[server_index].connect()
            stdin, stdout, stderr = server_list[server_index].client.exec_command(
                config["stop_command"]
            )
            output = stdout.read().decode()
            st.success(f"服务停止成功:\n{output}")
        except Exception as e:
            st.error(f"停止失败: {str(e)}")
        finally:
            server_list[server_index].close()

    if st.button("检查状态"):
        try:
            server_list[server_index].connect()
            stdin, stdout, stderr = server_list[server_index].client.exec_command(
                f"ps aux | grep {config['name']}"
            )
            output = stdout.read().decode()
            st.info(f"服务状态:\n{output}")
        except Exception as e:
            st.error(f"检查失败: {str(e)}")
        finally:
            server_list[server_index].close()


def main():
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

    page = st.sidebar.radio("---", ["服务器状态", "配置卡片", "启动服务"], index=0)
    if page == "服务器状态":
        # part 1 upload papers
        asyncio.run(status_page())
    elif page == "配置卡片":
        # part 2 show papers
        asyncio.run(config_page())
    elif page == "启动服务":
        # part 3 start service
        asyncio.run(start_service())


if __name__ == "__main__":
    main()

# ip 0.0.0.0
# streamlit run webui.py --server.port 8501 --server.address 0.0.0.0
