import json
import time
from kafka import KafkaProducer

_producer = None


def get_producer():
    global _producer
    if _producer is not None:
        return _producer

    for i in range(5):
        try:
            _producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                api_version=(2, 0, 0),
                request_timeout_ms=10000,
                retries=5
            )
            return _producer
        except Exception as e:
            print(f"⌛ Ожидание Kafka... Попытка {i + 1}/5")
            time.sleep(5)
    raise Exception("❌ Не удалось запустить Kafka Producer")


def send_to_kafka(topic, data):
    try:
        producer = get_producer()
        # Синхронная отправка для гарантии доставки
        future = producer.send(topic, data)
        future.get(timeout=10)
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")