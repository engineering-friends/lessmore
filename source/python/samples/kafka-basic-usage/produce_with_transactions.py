import uuid

from deeplay.utils.clients.kafka.elt_kafka_client import ETLKafkaClient


kafka_client = ETLKafkaClient(
    {
        "bootstrap.servers": "localhost:9092",
        "transactional.id": str(uuid.uuid4()),
    }
)

kafka_client.load(
    values=[f"hello-world-{i}" for i in range(5)],
    topic="test",
    message_key="",
)
