#!/usr/bin/python3

from cantools import database
from panda import Panda
from random import randint 
from time import sleep

# These are in seconds.
MAX_DELAY      = 6
MIN_DELAY      = 3

# Don't touch these unless you know what you're doing.
BTN_ADDR_NAME    = 'ID3C2VCLEFT_switchStatus'
BTN_IDX_NAME     = 'VCLEFT_switchStatusIndex'
BTN_IDX_VAL      = 'VCLEFT_SWITCH_STATUS_INDEX_1'
BTN_STATE_NAME   = 'VCLEFT_swcRightScrollTicks'
BTN_STATE_VALS   = [-1, 1]
BUS_ID           = 6
BUS_SPEED        = 500
DBC_FILE         = '/usr/local/dbc/Model3CAN.dbc'
SPEED_ADDR_NAME  = 'ID257DIspeed'
SPEED_STATE_NAME = 'DI_vehicleSpeed'
AP_ADDR_NAME = 'ID399DAS_status'
AP_STATE_NAME = 'DAS_autopilotState'

def get_state(addr_name, idx_name = None, idx_val = None):
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
  p.can_send(target_addr, db.encode_message(addr_name, state), BUS_ID)
  p.set_safety_mode(Panda.SAFETY_SILENT)

db = database.load_file(DBC_FILE)
val = 0
p = Panda()
p.set_can_speed_kbps(BUS_ID, BUS_SPEED)

while True:
  sleep(randint(MIN_DELAY, MAX_DELAY))
  speed_state = get_state(SPEED_ADDR_NAME)

  if speed_state[SPEED_STATE_NAME] > 0:
    #speed_finalstate = speed_state[SPEED_STATE_NAME]
    ap_state = get_state(AP_ADDR_NAME)
    ap_finalstate = ap_state[AP_STATE_NAME]
    print(ap_finalstate)
