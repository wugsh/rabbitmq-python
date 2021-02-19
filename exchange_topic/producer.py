import pika


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host = '127.0.0.1', port = 5672,virtual_host = '/',credentials = credentials))
channel = connection.channel()

#创建模糊匹配的exchange
channel.exchange_declare(exchange='topic_logs',durable = True, exchange_type='topic')

#这里关键字必须为点号隔开的单词，以便于消费者进行匹配。
routing_key = '[warn].kern'

message = 'Hello World!'
channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message, properties=pika.BasicProperties(delivery_mode = 2))

print('producer send %r:%r' %(routing_key, message))
connection.close()