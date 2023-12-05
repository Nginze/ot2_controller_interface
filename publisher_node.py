from config.controller import (
    setup_controller,
    setup_response_worker,
    setup_worker,
    init_controller_events,
    clean_up,
)


def main():
    joystick_count = setup_controller()
    setup_worker()
    setup_response_worker()
    init_controller_events(joystick_count)
    clean_up()


if __name__ == "__main__":
    main()
