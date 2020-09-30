#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: converse
@version: 1.0.0
@file: fetch_remote_file.py
@time: 2020/7/17 11:16
获取云服务器上日志的内容
"""
import paramiko
import time

cloud_server_dict = {
    "client0": "47.74.146.77",
    "client1": "47.74.27.90",
    "client2": "47.74.85.193",
    "client3": "47.88.93.79",
    "server0": "47.252.82.139",
    "server1": "47.74.66.121",
    "server2": "8.209.73.245",
    "server3": "161.117.179.104",
    # "corr": "8.209.73.245",
}


def ssh_check_status(ip, port, username, password, filename, date):
    """
    通过ssh查询云服务器的文件状态，与某个云服务器交互的最后时间状态。
    :param ip:       string 操作的云服务器IP
    :param port:     int ssh的端口
    :param username: string 登陆的用户名
    :param password: string 登陆密码
    :param filename: string 操作的文件名称

    :return:    string 返回文件的状态信息
    eg:
    ssh_check_status(cloudip, 8010, "dev", "meiyou.mima", cloudname)
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)

        # 获取文件的最后时间
        # stdin, stdout, stderr = ssh.exec_command(
        #     "tail -n 2 /home/converse/Downloads/trans_data/715/{}.log".format(filename))     # 本地测试
        try:
            stdin, stdout, stderr = ssh.exec_command(
                "tail -n 100  /home/dev/Downloads/disorder/{}_{}.log | grep 8.209.73.245.8005 | sort -r |head -1".format(
                    filename, date))
            # 取最后50条package信息，把最后的和8.209.73.245.8005交互的时间戳记录下来

            lastmessage_timestamp = stdout.read().decode("utf-8").split(" ")[0]
            file_lasttimestamp = time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.localtime(int(lastmessage_timestamp.split(".")[0])))
        except Exception as e:
            file_lasttimestamp = 0

        # 获取文件的大小
        stdin, stdout, stderr = ssh.exec_command("du -h /home/dev/Downloads/disorder/{}_{}.log".format(filename,date))
        fileinfo = stdout.read().decode("utf-8").strip('\n').split("\t")
        filesize = fileinfo[0]
        filename = fileinfo[1]

        return "{}\t\t{}\t{}\t\t{}".format(filename, ip, filesize, file_lasttimestamp)
        # return "{}\t\t{}\t{}\t".format(filename, ip, filesize)
    except Exception as e:
        print(e)


def print_cloud_file_status():
    """
    根据云服务器列表，记录云服务器状态的日志信息
    :return:

    eg:
    print_cloud_file_status()
    """
    f = open("logstatus.log", "a+")
    # 每一次运行都将日志和之前的间隔开
    f.write("\n")
    date = "20200930"
    for cloudname, cloudip in cloud_server_dict.items():
        info = ssh_check_status(cloudip, 8010, "dev", "meiyou.mima", cloudname, date)
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
        ssh.connect(ip, port=port, username=username, password=password)
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
    for cloudname, cloudip in cloud_server_dict.items():
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cloudip, port=8010, username="dev", password="meiyou.mima")
        stdin, stdout, stderr = ssh.exec_command("ps -ef |grep tcpdump|grep -v grep")
        print(cloudname, stdout.read().decode("utf-8").strip())


def stop_tcpdump_process_on_servers():
    """
    可以停止tcpdump进程
    :return:
    """
    for cloudname, cloudip in cloud_server_dict.items():
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cloudip, port=8010, username="dev", password="meiyou.mima")
        # 关闭tcpdump进程
        stdin, stdout, stderr = ssh.exec_command(
            "ps -ef |grep tcpdump |grep -v grep| awk '{print $2}'| sudo xargs kill -9")
        print(cloudname, stdout.read().decode("utf-8").strip())


def start_tcpdump_process_on_servers():
    """
    可以停止tcpdump进程
    :return:
    """
    log_date = "20200727"
    for cloudname, cloudip in cloud_server_dict.items():
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(cloudip, port=8010, username="dev", password="meiyou.mima")
        # # 开启tcpdump进程
        # stdin, stdout, stderr = ssh.exec_command(
        #     "sudo nohup tcpdump tcp -i any -n -tt -q and  '((dst host 8.209.73.245 and dst port 8005) or (src host 8.209.73.245 and src port 8005))'  and  '(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)' >> /home/dev/Downloads/{}_{}.log"
        #         .format(cloudname, log_date)
        # )
        # print(cloudname, stdout.read().decode("utf-8").strip())
        print(
            "sudo nohup tcpdump tcp -i any -n -tt -q and  '((dst host 8.209.73.245 and dst port 8005) or (src host 8.209.73.245 and src port 8005))'  and  '(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)' >> /home/dev/Downloads/{}_{}.log"
                .format(cloudname, log_date)
        )


if __name__ == '__main__':
    # ssh_check_status("10.38.2.237", 22, "converse", "converse", "client0_715")  # 本地正常
    print_cloud_file_status()
    # check_tcpdump_process_on_servers()
    # start_tcpdump_process_on_servers()
    # stop_tcpdump_process_on_servers()
