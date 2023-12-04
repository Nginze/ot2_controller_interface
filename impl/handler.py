from opentrons.execute import get_protocol_api
from opentrons import types
from opentrons.protocols.api_support.labware_like import LabwareLike
from opentrons.protocol_api import labware
from opentrons.protocols.api_support.util import AxisMaxSpeeds


# TODO: dynamic configuration (dynamic slot position and labware type)
def setup_hardware(rack, pipette, mount_pos, foot_print_loc):
    px = get_protocol_api("2.0")
    tiprack = px.load_labware("opentrons_96_tiprack_20ul", 10)
    instr = px.load_instrument("p20_single_gen2", "right", tip_racks=[tiprack])  # 20
    hardware = instr._implementation._protocol_interface.get_hardware()

    px.home()

    return px, tiprack, instr, hardware


hardware._backend._smoothie_driver.set_use_wait(False)


# utility functions
def move2(x, y, z):
    hardware.move_to(
        types.Mount.RIGHT,
        types.Point(x, y, z),
        critical_point=None,
        speed=80,
        max_speeds=AxisMaxSpeeds(),
    )


def move_handler():
    pass


def pick_handler():
    pass


def aspirate_handler():
    pass


def dispense_handler():
    pass


def eject_handler():
    pass


handler_map = {
    "Move": move_handler,
    "Pick": pick_handler,
    "Aspirate": aspirate_handler,
    "Dispense": dispense_handler,
    "Eject": eject_handler,
}
