#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pika
import time


credentials = pika.PlainCredentials('guest', 'guest')  # mq用户名和密码
# 生成socket,虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost', port=5672, virtual_host='/', credentials=credentials))
# 生成管道
channel = connection.channel()
# 声明一个queue防止启动报错
channel.queue_declare(queue='rpc_queue')


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)

    print("[.] fib(%s)" % n)
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),
                     body=str(response))

    ch.basic_ack(delivery_tag=method.delivery_tag)  # 回复确认消息


# 处理完这条再发下一条
channel.basic_qos(prefetch_count=1)
# 定义收到消息动作
channel.basic_consume('rpc_queue', on_request)

channel.start_consuming()
