from confluent_kafka import Producer


producer = Producer(
    {
        "bootstrap.servers": "localhost:9092",
    }
)

for i in range(5):
    producer.produce("test", key="key", value="value")

producer.flush()
