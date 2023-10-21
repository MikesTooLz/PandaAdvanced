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
CHARGE_ADDR_NAME = 'ID212BMS_status'
CHARGE_STATE_NAME = 'BMS_uiChargeStatus'
CHARGE_CURRENT_STATE = ''
APFUSE2_ADDR_NAME = 'ID2F1VCFRONT_eFuseDebugStatus'
APFUSE2_STATE_NAME = 'VCFRONT_autopilot2State'
APFUSE2_CURRENT_STATE = ''
STATUS_ADDR_NAME = 'ID2E1VCFRONT_status'
STATUS_STATE_NAME = 'VCFRONT_vehicleStatusDBG'
STATUS_CURRENT_STATE = ''
TRACKREQ_ADDR_NAME = 'ID313UI_trackModeSettings'
TRACKREQ_STATE_NAME = 'UI_trackModeRequest'
TRACKREQ_CURRENT_STATE = ''

db = database.load_file(DBC_FILE)
val = 0
p = Panda()
p.set_can_speed_kbps(BUS_AUTOPILOT, BUS_SPEED)
p.set_can_speed_kbps(BUS_VEHICLE, BUS_SPEED)
spinner = '/'

def clear_line(n="1"):
    #clear_string = '\033[#A\033[2K'
    clear_string = "\033[H\033[2J"
    clear_string = clear_string.replace("#",n)
    print(clear_string, end='')

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


#runA thread is just going to check all incoming can bus data for data we want.
def runA():
    while True:
        global GEAR_CURRENT_STATE, SPEED_CURRENT_STATE, CHARGE_CURRENT_STATE, APFUSE2_CURRENT_STATE, STATUS_CURRENT_STATE, TRACKREQ_CURRENT_STATE, db, val, p
        try:

            for addr, _, dat, _ in p.can_recv():
                target_addr = db.get_message_by_name(SPEED_ADDR_NAME).frame_id
                if addr == target_addr:
                    test_state = db.decode_message(target_addr, dat)
                    SPEED_CURRENT_STATE = 0.6214 * test_state[SPEED_STATE_NAME]

                target_addr = db.get_message_by_name(GEAR_ADDR_NAME).frame_id
                if addr == target_addr:
                    test_state = db.decode_message(target_addr, dat)
                    GEAR_CURRENT_STATE = test_state[GEAR_STATE_NAME]

                target_addr = db.get_message_by_name(CHARGE_ADDR_NAME).frame_id
                if addr == target_addr:
                    test_state = db.decode_message(target_addr, dat)
                    CHARGE_CURRENT_STATE = test_state[CHARGE_STATE_NAME]

                target_addr = db.get_message_by_name(APFUSE2_ADDR_NAME).frame_id
                if addr == target_addr:
                    test_state = db.decode_message(target_addr, dat)
                    APFUSE2_CURRENT_STATE = test_state[APFUSE2_STATE_NAME]

                target_addr = db.get_message_by_name(STATUS_ADDR_NAME).frame_id
                if addr == target_addr:
                    test_state = db.decode_message(target_addr, dat)
                    STATUS_CURRENT_STATE = test_state[STATUS_STATE_NAME]

                target_addr = db.get_message_by_name(TRACKREQ_ADDR_NAME).frame_id
                if addr == target_addr:
                    test_state = db.decode_message(target_addr, dat)
                    TRACKREQ_CURRENT_STATE = test_state[TRACKREQ_STATE_NAME]
 
        except Exception as e:
            #print("Exception caught", e)
            sleep(0)


#runB thread is just to print the current known values in a viewable way
def runB():
    while True:
        
        global GEAR_CURRENT_STATE, SPEED_CURRENT_STATE, CHARGE_CURRENT_STATE, APFUSE2_CURRENT_STATE, STATUS_CURRENT_STATE, TRACKREQ_CURRENT_STATE, db, val, p, spinner
        #clear_line(3)
        print('')
        print(f'╭─',spinner,' Live Can Bus Data View ',spinner,' ─────────────────────────╮')
        print(f'│ Speed:         ',SPEED_CURRENT_STATE)
        print(f'│ Charge Status: ',CHARGE_CURRENT_STATE)
        print(f'│ Gear:          ',GEAR_CURRENT_STATE)
        print(f'│ AP eFuse 2:    ',APFUSE2_CURRENT_STATE)
        print(f'│ Track Mode:    ',TRACKREQ_CURRENT_STATE)
        print(f'╰─────────────────────────────────────────────────────────╯')
        sleep(0.3)
        clear_line("7")
        
        if spinner == '-':
            spinner = '/'
        if spinner == '\\':
            spinner = '-'
        if spinner == '|':
            spinner = '\\'
        if spinner == '/':
            spinner = '|'


# runC thread is where we check if the car is in drive and interact with scroll wheel.
def runC():
    while True:
        global GEAR_CURRENT_STATE, SPEED_CURRENT_STATE, CHARGE_CURRENT_STATE, APFUSE2_CURRENT_STATE, STATUS_CURRENT_STATE, TRACKREQ_CURRENT_STATE, db, val, p
        try:
            sleep(randint(MIN_DELAY, MAX_DELAY))
            if GEAR_CURRENT_STATE == 'DI_GEAR_D':
                btn_state = get_state(BTN_ADDR_NAME, BTN_IDX_NAME, BTN_IDX_VAL)
                btn_state[BTN_STATE_NAME] = BTN_STATE_VALS[val]
                set_state(BTN_ADDR_NAME, btn_state)
                val = (val + 1) % len(BTN_STATE_VALS)
                sleep(0.3)
                btn_state = get_state(BTN_ADDR_NAME, BTN_IDX_NAME, BTN_IDX_VAL)
                btn_state[BTN_STATE_NAME] = BTN_STATE_VALS[val]
                set_state(BTN_ADDR_NAME, btn_state)
                val = (val + 1) % len(BTN_STATE_VALS)
        except Exception as e:
            sleep(3.2)

if __name__ == "__main__":
    t1 = Thread(target = runA)
    t2 = Thread(target = runB)
    t3 = Thread(target = runC)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t3.setDaemon(True)
    t1.start()
    t2.start()
    t3.start()
    while True:
        pass
