# Paramiko

import paramiko
import asyncio


async def get_server_gpu_status(server):
    """
    获取单个服务器的状态
    :param server:
    :return:
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=server['ip'],
        port=22,
        username=server['user'],
        password=server['password']
    )
    # gpu_name, gpu_usage, memory_size, memory_usage, temperature
    stdin, stdout, stderr = client.exec_command(
        'nvidia-smi --query-gpu=name,utilization.gpu,memory.total,memory.used,temperature.gpu --format=csv,noheader')
    gpu_info = stdout.readlines()
    keys = ['gpu_name', 'gpu_usage', 'memory_size', 'memory_usage', 'temperature']
    gpu_info = [dict(zip(keys, info.strip().split(','))) for info in gpu_info]

    return gpu_info


async def get_server_model_status(server):
    """
    获取服务器上的模型状态
    :param server:
    :return:
    """
    return ['model1', 'model2']
