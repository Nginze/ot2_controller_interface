import pygame
import json
import time
import threading
from config.redis import publish_message, conn
from config.constants import (
    CHANNEL_NAME,
    FEEDBACK_CHANNEL_NAME,
    MIN_X,
    MAX_X,
    MAX_Y,
    MIN_Y,
)


class RobotContext:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {"locx": 100, "locy": 100, "dy": 0, "dx": 0, "block": False}

    def get(self, key):
        with self.lock:
            return self.data.get(key)

    def set(self, key, value):
        with self.lock:
            self.data[key] = value

    def publish_move(self):
        x, y = self.get("locx"), self.get("locy")
        print(x, y)
        publish_message(
            CHANNEL_NAME, json.dumps({"op": "Move", "d": {"x": x, "y": y, "z": 130}})
        )
        self.set("dx", 0)
        self.set("dy", 0)


robot_ctx = RobotContext()


def setup_controller():
    pygame.init()
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    return joystick_count


def navigation_worker():
    global robot_ctx

    print("worker started")

    while True:
        time.sleep(1)

        if robot_ctx.get("block"):
            continue

        if robot_ctx.get("dx") == robot_ctx.get("dy") == 0:
            continue

        robot_ctx.set(
            "locx", min(max(MIN_X, robot_ctx.get("locx") + robot_ctx.get("dx")), MAX_X)
        )
        robot_ctx.set(
            "locy", min(max(MIN_Y, robot_ctx.get("locy") + robot_ctx.get("dy")), MAX_Y)
        )

        robot_ctx.publish_move()

        print("sent")


def response_worker():
    pub_sub = conn.pubsub()
    pub_sub.subscribe(FEEDBACK_CHANNEL_NAME)

    for message in pub_sub.listen():
        try:
            if message["type"] == "message":
                data_as_json = message["data"].decode("utf-8")
                data = json.loads(data_as_json)
                print(data)
                # handler_callback(message)
        except Exception as e:
            print(e)


def setup_worker():
    t = threading.Thread(target=navigation_worker)
    t.daemon = True
    t.start()


def setup_response_worker():
    t = threading.Thread(target=response_worker)
    t.daemon = True
    t.start()


def handle_button_press(button):
    global robot_ctx

    robot_ctx.set("block", True)

    if button == 0:
        publish_message(CHANNEL_NAME, json.dumps({"op": "Aspirate", "d": {}}))
        print("x")
    elif button == 1:
        publish_message(CHANNEL_NAME, json.dumps({"op": "Dispense", "d": {}}))
        print("circle")
    elif button == 2:
        publish_message(CHANNEL_NAME, json.dumps({"op": "Eject", "d": {}}))
        print("square")
    elif button == 3:
        publish_message(CHANNEL_NAME, json.dumps({"op": "Pick", "d": {}}))
        print("triangle")

    robot_ctx.set("block", False)


def init_controller_events(joystick_count):
    if joystick_count <= 0:
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Connected to joystick: {joystick.get_name()}")

    while True:
        pygame.event.pump()
        for event in pygame.event.get():
            # Replace the JOYAXISMOTION part with JOYHATMOTION
            if event.type == pygame.JOYHATMOTION and event.hat == 0:
                hat_x, hat_y = event.value
                if hat_x != 0 or hat_y != 0:
                    d, threshold = 2, 10

                    robot_ctx.set("dx", d if hat_x > 0 else (-d if hat_x < 0 else 0))
                    robot_ctx.set("dy", d if hat_y > 0 else (-d if hat_y < 0 else 0))

            if event.type == pygame.JOYAXISMOTION and event.axis == 3:
                x, y = joystick.get_axis(0), joystick.get_axis(1)
                print(f"Axis X: {x}, Axis Y: {y}")

                d, threshold = 2, 10

                robot_ctx.set(
                    "dx", d if x > threshold else (-d if x < -threshold else 0)
                )
                robot_ctx.set(
                    "dy", d if y > threshold else (-d if y < -threshold else 0)
                )

            if event.type == pygame.JOYBUTTONUP:
                handle_button_press(event.button)


def clean_up():
    pygame.quit()
