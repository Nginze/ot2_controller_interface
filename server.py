import json
from impl.handler import handler_map
from config.redis import conn
from config.constants import CHANNEL_NAME


def handler_callback(message):
    data_as_json = message["data"].decode("utf-8")
    data = json.loads(data_as_json)

    op, d = data.get("op"), data.get("d")
    response = handler_map[op](d)
    print(response)


if __name__ == "__main__":
    print("connected to redis broker")

    pub_sub = conn.pubsub()
    pub_sub.subscribe(CHANNEL_NAME)

    for message in pub_sub.listen():
        try:
            if message["type"] == "message":
                handler_callback(message)
        except Exception as e:
            print(e)
