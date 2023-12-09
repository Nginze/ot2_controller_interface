from opentrons.execute import get_protocol_api
from opentrons import types
from opentrons.protocols.api_support.labware_like import LabwareLike
from opentrons.protocol_api import labware
from opentrons.protocols.api_support.util import AxisMaxSpeeds
from config.constants import TRAVERSE_HEIGHT, DEFAULT_RACK, DEFAULT_PIPETTE
import time


# TODO: dynamic configuration (dynamic slot position and labware type)
def setup_robot(
    rack=DEFAULT_RACK, pipette=DEFAULT_PIPETTE, mount_pos="left", foot_print_loc=5
):
    """
    The function "setup_robot" sets up a robot by loading a tiprack and instrument, homing the robot,
    and disabling the wait feature.

    :param rack: The "rack" parameter is the type of labware rack that holds the tipracks. In this case,
    it is "opentrons_96_tiprack_20ul", which is a 96-well tiprack with a volume capacity of 20 µL
    :param pipette: The "pipette" parameter is the type of pipette being used. In this case, it is a
    p20_single_gen2 pipette, which has a volume range of 2-20 µL
    :param mount_pos: The `mount_pos` parameter specifies the position where the pipette is mounted on
    the robot. It can be either "left" or "right"
    :param foot_print_loc: The `foot_print_loc` parameter is the location where the robot is placed or
    installed. It could be a specific coordinate or a reference point on the lab bench where the robot
    is situated
    :return: four variables: px, tiprack, instr, and hardware.
    """

    print("called again")
    px = get_protocol_api("2.0")
    tiprack = px.load_labware(rack, foot_print_loc)
    reservoir = px.load_labware("nest_1_reservoir_195ml", "4", "reagent reservoir 2")
    elutionplate = px.load_labware(
        "biorad_96_wellplate_200ul_pcr", "3", "elution plate"
    )
    instr = px.load_instrument(pipette, mount_pos, tip_racks=[tiprack])  # 20
    hardware = instr._implementation._protocol_interface.get_hardware()
    instr.home()
    px.home()

    hardware._backend._smoothie_driver.use_wait = False
    print(hardware._backend._smoothie_driver.use_wait)

    return px, tiprack, instr, hardware, reservoir, elutionplate


px, tiprack, instr, hardware, reservoir, elutionplate = setup_robot()


def move2(x, y, z):
    """
    The function `move2` moves a hardware mount to a specified point in 3D space, with specified speed
    and maximum speeds, and catches any exceptions that occur.

    :param x: The parameter `x` represents the x-coordinate of the point where you want to move the
    hardware to
    :param y: The parameter "y" in the move2 function represents the y-coordinate of the point to which
    the hardware should move
    :param z: The parameter "z" in the move2 function represents the desired z-coordinate of the point
    to which the hardware should move. It specifies the vertical position of the point in a
    three-dimensional space
    """
    # print(x, y, z)
    try:
        hardware.move_to(
            types.Mount.LEFT,
            types.Point(x, y, z),
            critical_point=None,
            speed=20,
            max_speeds=AxisMaxSpeeds(),
        )
    except Exception as e:
        print(e)


def move_handler(data):
    """
    The function `move_handler` takes in a dictionary `data` containing values for `x`, `y`, and `z`,
    converts them to floats, and calls the `move2` function with the converted values and a constant
    `TRAVERSE_HEIGHT`, then returns "done".

    :param data: The `data` parameter is expected to be a dictionary containing the values for `x`, `y`,
    and `z`. These values represent the coordinates for a point in a 3D space
    :return: the string "done" if the code executes successfully.
    """
    try:
        x, y, z = data.get("x"), data.get("y"), data.get("z")
        x, y, z = float(x), float(y), float(z)
        move2(x, y, TRAVERSE_HEIGHT)
        return False
    except Exception as e:
        print(e)


def pick_handler(data):
    """
    The function `pick_handler` picks up a tip from a tiprack and moves it to a specified location.
    :return: a dictionary with keys "px", "py", and "pz", and their corresponding values.
    """
    # hardware._backend._smoothie_driver.set_use_wait(True)

    hardware._backend._smoothie_driver.use_wait = True
    print("waiting")
    time.sleep(1)
    print("pickup")

    try:
        tiprack, target_well = labware.next_available_tip(
            instr.starting_tip, instr.tip_racks, instr.channels
        )
        move_to_location = target_well.top()
        move_to_location._point = types.Point(
            move_to_location._point.x + 0,
            move_to_location._point.y,
            move_to_location._point.z,
        )
        instr.pick_up_tip(move_to_location)
    except Exception as e:
        print("error", e)

    time.sleep(1)
    # px, py = 50, 320
    hardware._backend._smoothie_driver.use_wait = False
    move2(move_to_location._point.x, move_to_location._point.y, 130)
    # px.home()
    # move2(320, 360, TRAVERSE_HEIGHT)
    return {
        "x": move_to_location._point.x,
        "y": move_to_location._point.y,
        "z": move_to_location._point.z,
    }


def aspirate_handler(data):
    """
    The function `aspirate_handler` handles the aspiration of a liquid at a specified location using a
    robotic instrument.

    :param data: The `data` parameter is a dictionary that contains the values for the x, y, and z
    coordinates
    :return: the string "done".
    """

    # hardware._backend._smoothie_driver.set_use_wait(True)
    print("waiting")
    time.sleep(1)
    x, y, z = data.get("x"), data.get("y"), data.get("z")
    x, y, z = float(x), float(y), float(z)
    print("aspirate", x, y, z)

    try:
        instr.aspirate(20, types.Location(types.Point(x, y, 20), LabwareLike(None)))
    except Exception as e:
        print("error", e)

    # hardware._backend._smoothie_driver.set_use_wait(False)
    # move2(x, y, z=TRAVERSE_HEIGHT)
    return False


def dispense_handler(data):
    """
    The `dispense_handler` function dispenses a liquid at a specified location using a hardware
    instrument.

    :param data: The `data` parameter is expected to be a dictionary containing the values for `x`, `y`,
    and `z`. These values represent the coordinates for dispensing a substance
    :return: the string "done".
    """
    # hardware._backend._smoothie_driver.set_use_wait(True)
    print("waiting")
    time.sleep(1)

    x, y, z = data.get("x"), data.get("y"), data.get("z")
    x, y, z = float(x), float(y), float(z)
    print("dispense", x, y, z)

    try:
        instr.dispense(20, types.Location(types.Point(x, y, 20), LabwareLike(None)))
    except Exception as e:
        print("error", e)

    # hardware._backend._smoothie_driver.set_use_wait(False)
    return False


def eject_handler(data):
    """
    The function `eject_handler()` ejects a tip from a pipette and returns the coordinates for the
    pipette to traverse to.
    :return: a dictionary with the keys "x", "y", and "z" and their corresponding values.
    """
    # hardware._backend._smoothie_driver.set_use_wait(True)
    print("waiting")
    time.sleep(1)
    print("eject")
    px.home()

    try:
        instr.drop_tip()
    except Exception as e:
        print("error", e)

    move2(320, 360, TRAVERSE_HEIGHT)
    # hardware._backend._smoothie_driver.set_use_wait(False)
    return {"x": 320, "y": 360, "z": TRAVERSE_HEIGHT}


handler_map = {
    "Move": move_handler,
    "Pick": pick_handler,
    "Aspirate": aspirate_handler,
    "Dispense": dispense_handler,
    "Eject": eject_handler,
}
