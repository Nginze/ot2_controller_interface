import json

from impl.handler import handler_map
from config.redis import conn, publish_feedback
from config.constants import CHANNEL_NAME, FEEDBACK_CHANNEL_NAME, TRAVERSE_HEIGHT


def handler_callback(message):
    data_as_json = message["data"].decode("utf-8")
    data = json.loads(data_as_json)

    op, d = data.get("op"), data.get("d")
    print(op, d)
    response = handler_map[op](d)
    publish_feedback(FEEDBACK_CHANNEL_NAME, json.dumps(response if response else None))
    print(response)


def main():
    print("connected to redis broker")

    pub_sub = conn.pubsub()
    pub_sub.subscribe(CHANNEL_NAME)

    for message in pub_sub.listen():
        try:
            if message["type"] == "message":
                handler_callback(message)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
