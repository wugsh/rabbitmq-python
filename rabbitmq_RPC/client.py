#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pika
import uuid
import time


class FibonacciRpcClient(object):
    def __init__(self):
        self.credentials = pika.PlainCredentials('guest', 'guest')  # mq用户名和密码
        # 生成socket,虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost', port=5672, virtual_host='/', credentials=self.credentials))
        # 生成管道
        self.channel = self.connection.channel()
        # 声明一个随机queue，exclusive=True会在此queue的消费者断开后，自动将queue删除
        result = self.channel.queue_declare('', exclusive=True)
        # 获取随机queue名
        self.callback_queue = result.method.queue
        # 定义收到消息后的动作
        self.channel.basic_consume(self.callback_queue,  # 获取随机queue名
                                   self.on_response,  # 回调函数on_response
                                   auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:  # 判断uuid是否是否一致
            self.response = body  # 队列返回

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())  # 生成uuid，等会发送给服务端
        # 发送消息给服务端
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',  # 路由键
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,  # 告诉服务端将返回发到哪个队列
                                                                   correlation_id=self.corr_id), body=str(n))  # 发送的消息
        while self.response is None:
            # 非阻塞版的start_consuming()，如果收到消息就执行on_response回调函数
            self.connection.process_data_events()
            #print("no msg....")
            time.sleep(0.5)  # 这里可以执行其他命令
        return int(self.response)  # 返回结果


if __name__ == "__main__":
    # 生成实例
    fibonacci_rpc = FibonacciRpcClient()

    print("[x] Requesting fib(10)")

    # 调用call函数
    response = fibonacci_rpc.call(10)

    print("[x] got %r " % response)
