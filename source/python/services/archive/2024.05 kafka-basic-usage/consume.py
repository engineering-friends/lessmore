import json

from confluent_kafka import Consumer, KafkaError, KafkaException
from deeplay.utils.loguru_utils import configure_loguru
from deeplay.utils.unified import unified_datetime
from loguru import logger


if __name__ == "__main__":
    configure_loguru()

    consumer = Consumer(
        {
            "bootstrap.servers": "localhost:9092",
            "group.id": "kafka-basics-consumer",
            "enable.auto.commit": False,
            "auto.offset.reset": "latest",
        }
    )

    consumer.subscribe(["test"])

    # - Print available topics

    logger.info("Available topics:", topics=json.dumps(list(sorted(consumer.list_topics().topics.keys()))))

    # - Start polling

    logger.info("Starting polling...")

    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                logger.info(
                    "Reached end at offset",
                    topic=msg.topic(),
                    partition=msg.partition(),
                    offset=msg.offset(),
                )
            elif msg.error():
                logger.error("Error", error=msg.error())
                raise KafkaException(msg.error())
        else:
            logger.info(
                "Received new message",
                message_timestamp=unified_datetime(msg.timestamp()[1]),
                topic=msg.topic(),
                partition=msg.partition(),
                offset=msg.offset(),
                key=msg.key(),
                value=msg.value(),
            )
