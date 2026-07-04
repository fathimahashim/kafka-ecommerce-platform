from confluent_kafka import Consumer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'test-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['test-topic'])

print("Listening for messages... (Ctrl+C to stop)")

try:
    while True:
        msg = consumer.poll(1.0)  # wait up to 1 second for a message

        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue

        print(f"Received: key={msg.key().decode('utf-8')}, value={msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()