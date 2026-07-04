from confluent_kafka import Producer

# Tells the client where to find the Kafka broker
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to topic '{msg.topic()}' partition [{msg.partition()}]")

# Send one test message
producer.produce('test-topic', key='order1', value='Hello Kafka!', callback=delivery_report)

# This actually sends it and waits for confirmation
producer.flush()