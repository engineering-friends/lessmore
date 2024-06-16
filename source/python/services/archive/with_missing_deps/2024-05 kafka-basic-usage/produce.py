from confluent_kafka import Producer


if __name__ == "__main__":
    producer = Producer(
        {
            "bootstrap.servers": "localhost:9092",
        }
    )

    for i in range(5):
        producer.produce("test", key="key", value="value")

    producer.flush()
