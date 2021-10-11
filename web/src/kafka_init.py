from kafka.admin import KafkaAdminClient, NewTopic

from src.config import BOOTSTRAP_SERVER, \
    KAFKA_VIDEOS_TOPIC, \
    KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC, \
    KAFKA_DOWNLOAD_FRAME_DONE_TOPIC, \
    KAFKA_OCR_FRAME_REQUEST_TOPIC, \
    KAFKA_OCR_FRAME_DONE_TOPIC

admin_client = KafkaAdminClient(
    bootstrap_servers=BOOTSTRAP_SERVER,
    client_id='init_topics'
)

topic_list = [NewTopic(name=KAFKA_DOWNLOAD_FRAME_REQUEST_TOPIC,
                       num_partitions=10,
                       replication_factor=1),
              NewTopic(name=KAFKA_DOWNLOAD_FRAME_DONE_TOPIC,
                       num_partitions=1,
                       replication_factor=1),
              NewTopic(name=KAFKA_OCR_FRAME_REQUEST_TOPIC,
                       num_partitions=10,
                       replication_factor=1),
              NewTopic(name=KAFKA_OCR_FRAME_DONE_TOPIC,
                       num_partitions=1,
                       replication_factor=1),
              NewTopic(name=KAFKA_VIDEOS_TOPIC,
                       num_partitions=1,
                       replication_factor=1)]

admin_client.create_topics(new_topics=topic_list, validate_only=False)
