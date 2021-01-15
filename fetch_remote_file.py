#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: converse
@version: 1.0.0
@file: fetch_remote_file.py
@time: 2020/7/17 11:16
获取云服务器上日志的内容,client1的IP已换成东京
"""
import paramiko
import time

from config import *


def ssh_check_status(ip, username, password, filename, date):
    """
    通过ssh查询云服务器的文件状态，与某个云服务器交互的最后时间状态。
    :param ip:       string 操作的云服务器IP
    :param port:     int ssh的端口
    :param username: string 登陆的用户名
    :param password: string 登陆密码
    :param filename: string 操作的文件名称

    :return:    string 返回文件的状态信息
    eg:
    ssh_check_status(cloudip, port, account, password, cloudname)
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=TIMEOUT)

        try:
            stdin, stdout, stderr = ssh.exec_command(LAST_COMMUNICATION_TIME.format(filename, date))
            # 取最后50条package信息，把最后的和CORR交互的时间戳记录下来

            lastmessage_timestamp = stdout.read().decode("utf-8").split(" ")[0]
            file_lasttimestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(lastmessage_timestamp.split(".")[0])))
        except Exception as e:
            file_lasttimestamp = 0

        # 获取文件的大小
        stdin, stdout, stderr = ssh.exec_command(LOG_SIZE.format(filename, date))
        fileinfo = stdout.read().decode("utf-8").strip('\n').split("\t")
        filesize = fileinfo[0]
        filename = fileinfo[1]

        return "{}\t\t{}\t{}\t\t{}".format(filename, ip, filesize, file_lasttimestamp)
    except Exception as e:
        print(e)


def print_cloud_file_status():
    """
    根据云服务器列表，记录云服务器状态的日志信息
    :return:

    eg:
    print_cloud_file_status()
    """
    f = open(LOGNAME, "a+")
    # 每一次运行都将日志和之前的间隔开
    f.write("\n")
    for cloudname, cloudip in CLOUD_SERVER_DICT.items():
        info = ssh_check_status(cloudip, ACCOUNT, PASSWORD, cloudname, LOGDATE)
        if info:
            print(info)
            f.write(info + "\n")


def rsync_file_among_clouds(ip, port, username, password, filename):
    """
    现在没用
    :param ip:
    :param port:
    :param username:
    :param password:
    :param filename:
    :return:
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,  username=username, password=password)
    except Exception as e:
        print(e)
    stdin, stdout, stderr = ssh.exec_command(
        "rsync -avzP  dev@47.74.146.77:/home/dev/Downloads/{}_20200714.log /home/converse/Downloads/trans_data/test.log".format(
            filename))
    print(stdout.read().decode("utf-8"))
    stdin, stdout, stderr = ssh.exec_command("echo 'meiyou.mima'".format(filename))


def check_tcpdump_process_on_servers():
    """
    可以适用于查询tcpdump的进程
    :return:
    """
    print("查询TCPDUMP进程")
    for cloudname, cloudip in CLOUD_SERVER_DICT.items():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(cloudip, username=ACCOUNT, password=PASSWORD)
            # 查询TCPDUMP进程
            stdin, stdout, stderr = ssh.exec_command(CHECK_TCPDUMP_COMMAND)
            print(cloudname, stdout.read().decode("utf-8").strip())
        except Exception as e:
            print(e)


def stop_tcpdump_process_on_servers():
    """
    可以停止tcpdump进程
    :return:
    """
    print("关闭TCPDUMP进程")
    for cloudname, cloudip in CLOUD_SERVER_DICT.items():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(cloudip, username=ACCOUNT, password=PASSWORD, timeout=TIMEOUT)
            # 关闭tcpdump进程
            stdin, stdout, stderr = ssh.exec_command(KILL_TCPDUMP_COMMAND)
            print(cloudname, stdout.read().decode("utf-8").strip())
        except Exception as e:
            print(e)


def start_tcpdump_process_on_servers():
    """
    启动tcpdump进程
    :return:
    """
    log_date = "20201212"
    for cloudname, cloudip in CLOUD_SERVER_DICT.items():
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cloudip, username=ACCOUNT, password=PASSWORD, timeout=TIMEOUT)
        # 开启tcpdump进程
        stdin, stdout, stderr = ssh.exec_command(TCPDUMP_TRAFFIC_LOG_COMMAND.format(cloudname, log_date))
        print(cloudname, stdout.read().decode("utf-8").strip())
        print(TCPDUMP_TRAFFIC_LOG_COMMAND.format(cloudname, log_date))


if __name__ == '__main__':
    # ssh_check_status("10.38.2.237", 22, "converse", "converse", "client0_715")  # 本地正常
    # print_cloud_file_status()
    check_tcpdump_process_on_servers()
    # start_tcpdump_process_on_servers()
    # stop_tcpdump_process_on_servers()

    # cloudname = "server1"
    # log_date = "20210115"
    # cloudip = CLOUD_SERVER_DICT[cloudname]
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(cloudip, username=ACCOUNT, password=PASSWORD)
    # # 开启tcpdump进程
    # stdin, stdout, stderr = ssh.exec_command(TCPDUMP_TRAFFIC_LOG_COMMAND.format(cloudname, log_date))
    # print(cloudname, stdout.read().decode("utf-8").strip())
    # print(TCPDUMP_TRAFFIC_LOG_COMMAND.format(cloudname, log_date))