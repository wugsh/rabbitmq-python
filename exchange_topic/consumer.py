import pika
import sys


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='127.0.0.1', port=5672, virtual_host='/', credentials=credentials))
channel = connection.channel()

# 创建模糊匹配的exchange
channel.exchange_declare(exchange='topic_logs', durable = True, exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# 绑定键，'#'匹配所有字符，'*'匹配一个单词
binding_keys = ['[warn].*', 'info.*']

if not binding_keys:
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_logs',
                       queue=queue_name, routing_key=binding_key)


def callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("consumer get：%r:%r" % (method.routing_key, body.decode()))

channel.basic_consume(queue_name, callback, auto_ack = False)
channel.start_consuming()
