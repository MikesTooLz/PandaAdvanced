#!/usr/bin/python3
from cantools import database
from panda import Panda
from random import randint
from time import sleep
import pprint
from threading import Thread

# These are in seconds.
MAX_DELAY = 6
MIN_DELAY = 3


# Don't touch these unless you know what you're doing.
BTN_ADDR_NAME = 'ID3C2VCLEFT_switchStatus'
BTN_IDX_NAME = 'VCLEFT_switchStatusIndex'
BTN_IDX_VAL = 'VCLEFT_SWITCH_STATUS_INDEX_1'
BTN_STATE_NAME = 'VCLEFT_swcRightScrollTicks'
BTN_STATE_VALS = [-1, 1]
BUS_VEHICLE = 0
BUS_RADAR = 1
BUS_AUTOPILOT = 2
BUS_SPEED = 500
DBC_FILE = '/usr/local/dbc/Model3CAN.dbc'
SPEED_ADDR_NAME = 'ID257DIspeed'
SPEED_STATE_NAME = 'DI_vehicleSpeed'
GEAR_ADDR_NAME = 'ID118DriveSystemStatus'
GEAR_STATE_NAME = 'DI_gear'
GEAR_CURRENT_STATE = ''
SPEED_CURRENT_STATE = ''
db = database.load_file(DBC_FILE)
val = 0
p = Panda()
p.set_can_speed_kbps(BUS_AUTOPILOT, BUS_SPEED)
p.set_can_speed_kbps(BUS_VEHICLE, BUS_SPEED)

def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)


def get_state(addr_name, idx_name=None, idx_val=None):
    target_addr = db.get_message_by_name(addr_name).frame_id
    state = None

    while state is None:
        for addr, _, dat, _ in p.can_recv():
            if addr == target_addr:
                test_state = db.decode_message(addr_name, dat)

                if idx_name is None or test_state[idx_name] == idx_val:
                    state = test_state

    return state

def set_state(addr_name, state):
    target_addr = db.get_message_by_name(addr_name).frame_id
    p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
    p.can_send(target_addr, db.encode_message(addr_name, state), BUS_VEHICLE)
    p.set_safety_mode(Panda.SAFETY_SILENT)



def runA():
    while True:
        global GEAR_CURRENT_STATE, SPEED_CURRENT_STATE, db, val, p
        try:

            for addr, _, dat, _ in p.can_recv():
                if addr == SPEED_ADDR_NAME:
                    test_state = db.decode_message(SPEED_ADDR_NAME, dat)
                    SPEED_CURRENT_STATE = test_state[SPEED_STATE_NAME]

                if addr == GEAR_ADDR_NAME:
                    test_state = db.decode_message(GEAR_ADDR_NAME, dat)
                    GEAR_CURRENT_STATE = test_state[GEAR_STATE_NAME]
                    

 
        except Exception as e:
            #print("Exception caught", e)
            sleep(0)

def runB():
    while True:
        global GEAR_CURRENT_STATE, SPEED_CURRENT_STATE, db, val, p
        clear_line(3)
        print("Speed: ",SPEED_CURRENT_STATE)
        print("line2: 2")
        print("Gear: ",GEAR_CURRENT_STATE)

if __name__ == "__main__":
    t1 = Thread(target = runA)
    t2 = Thread(target = runB)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass
