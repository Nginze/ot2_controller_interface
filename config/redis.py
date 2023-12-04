import redis
import time

conn = redis.StrictRedis(
    host="redis-19325.c293.eu-central-1-1.ec2.cloud.redislabs.com",
    password="HMY8CRXldidQIPQTdfz0yFBqJy1xhJNw",
    port=19325,
    db=0,
)


def publish_message(channel, msg):
    conn.publish(channel, msg)
    time.sleep(1)
