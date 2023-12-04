import pygame
import json
from config.redis import publish_message
from config.constants import CHANNEL_NAME


def setup_controller():
    pygame.init()
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    return joystick_count


def init_controller_events(joystick_count):
    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        print(f"Connected to joystick: {joystick.get_name()}")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    axis_x = joystick.get_axis(0)
                    axis_y = joystick.get_axis(1)
                    print(f"Axis X: {axis_x}, Axis Y: {axis_y}")
                    publish_message(
                        CHANNEL_NAME, json.dumps({"event": "move", "dx": 50, "dy": 50})
                    )

                elif event.type == pygame.JOYBUTTONUP:
                    button = event.button
                    print(f"Button {button} released")
                    publish_message(
                        CHANNEL_NAME, json.dumps({"event": "?", "dx": 50, "dy": 50})
                    )

                # elif event.type == pygame.JOYHATMOTION:
                #     # Joystick hat motion event
                #     hat = joystick.get_hat(0)
                #     print(f"Hat motion: {hat}")


def clean_up():
    pygame.quit()
