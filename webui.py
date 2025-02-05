# 构建一个基于streamlit的web应用
# 页面显示多行，每一行为一个服务器节点，显示内容包括：ip，名称
import json
import streamlit as st
import asyncio

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


if 'server_list' not in st.session_state:
    st.session_state.server_list = load_servers()


async def get_servers_gpu_status_single(server):
    """
    获取单个服务器的状态
    :param server:
    :return:
    """
    gpu_usage = 0
    memory_usage = 0
    temperature = 0
    return {'gpu_usage': gpu_usage, 'memory_usage': memory_usage, 'temperature': temperature}


async def get_servers_gpu_status(servers):
    """
    获取服务器状态
    :param servers:
    :return:
    """
    servers_gpu_status = {}
    for server in servers:
        server_gpu_status = await get_servers_gpu_status_single(server)
        servers_gpu_status[server['name']] = server_gpu_status
    return servers_gpu_status


async def get_servers_model_status_single(server):
    """
    获取服务器上的模型状态
    :param server:
    :return:
    """
    return ['model1', 'model2']


async def get_servers_model_status(servers):
    """
    获取服务器上的模型状态
    :param servers:
    :return:
    """
    servers_model_status = {}
    for server in servers:
        server_model_status = await get_servers_model_status_single(server)
        servers_model_status[server['name']] = server_model_status
    return servers_model_status


async def show_servers(servers):
    """
    显示服务器以及相关信息
    :param servers:
    :return:
    """
    columns_layout = [2, 1, 2, 2]
    # 获取服务器状态
    # gpu
    servers_gpu_status = await get_servers_gpu_status(servers)
    # model
    servers_model_status = await get_servers_model_status(servers)
    col1, col2, col3, col4 = st.columns(columns_layout)
    col1.markdown("## 服务器名称")
    col2.markdown("## GPU状态")
    col3.markdown("## 服务列表")
    col4.markdown("## 操作")

    for server in servers:
        # 四列
        # 1：name:user & ip
        # 2: GPU usage: 0% memory: 0% temperature: 0
        # 3: server list
        # 4: add server & delete server
        col1, col2, col3, col4 = st.columns(columns_layout, vertical_alignment="center")

        with col1:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"### {server['name']}")
            with c2:
                st.markdown(f"User: {server['user']}")
                st.markdown(f"IP: {server['ip']}")
        with col2:
            st.markdown(f"GPU usage: {servers_gpu_status[server['name']]['gpu_usage']}%")
            st.markdown(f"Memory: {servers_gpu_status[server['name']]['memory_usage']}%")
            st.markdown(f"Temperature: {servers_gpu_status[server['name']]['temperature']}")
        with col3:
            for model in servers_model_status[server['name']]:
                st.write(model)
        with col4:
            st.write("添加服务")
            st.write("删除服务")


async def main():
    st.title("服务器列表")
    await show_servers(st.session_state.server_list)


if __name__ == "__main__":
    asyncio.run(main())

# streamlit run webui.py
