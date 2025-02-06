# Description: 服务器相关的工具函数

import time


async def get_server_gpu_status(client):
    """
    获取单个服务器的状态
    :param server:
    :param client:
    :return:
    """
    # gpu_name, gpu_usage, memory_size, memory_usage, temperature
    stdin, stdout, stderr = client.exec_command(
        'nvidia-smi --query-gpu=name,utilization.gpu,memory.total,memory.used,temperature.gpu --format=csv,noheader')
    gpu_info = stdout.readlines()
    keys = ['gpu_name', 'gpu_usage', 'memory_size', 'memory_usage', 'temperature']
    gpu_info = [dict(zip(keys, info.strip().split(','))) for info in gpu_info]

    return gpu_info


async def get_server_model_status(client):
    """
    获取服务器上的模型状态
    :param server:
    :param client:
    :return:
    """
    # model_name, model_image, model_status
    stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Names}} | {{.Image}} | {{.Status}}"')
    model_info = stdout.readlines()
    keys = ['model_name', 'model_image', 'model_status']
    model_info = [dict(zip(keys, info.strip().split('|'))) for info in model_info]
    return model_info


async def stop_all_models(client):
    """
    停止服务器上的所有模型
    :param server:
    :return:
    """
    stdin, stdout, stderr = client.exec_command('docker stop $(docker ps -a -q)')


def get_local_time():
    """
    获取本地时间
    :return:
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# if __name__ == '__main__':
#     server = {
#         "name": "mozinode4p",
#         "ip": "192.168.1.115",
#         "user": "root",
#         "password": "root"
#     }
#     asyncio.run(get_server_model_status(server))
