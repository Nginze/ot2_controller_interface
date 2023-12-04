from config.controller import setup_controller, init_controller_events, clean_up


if __name__ == "__main__":
    joystick_count = setup_controller()
    init_controller_events(joystick_count)
    clean_up()
