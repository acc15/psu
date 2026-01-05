import time
import serial
import struct
import logging

from typing import Callable, Any
from dataclasses import dataclass
import utils

BAUD_RATES = { 9600:1, 19200:2, 38400:3, 57600:4, 115200:5 }

class Dir(utils.IntEnumWithHexStr):
    HOST_TO_DEVICE = 0xF1
    DEVICE_TO_HOST = 0xF0

class Action(utils.IntEnumWithHexStr):
    GET = 0xA1
    BAUD = 0xB0
    SET = 0xB1
    LOCK = 0xC1

class State(utils.IntEnumWithHexStr):
    NONE = 0
    OVP = 1
    OCP = 2
    OPP = 3
    OTP = 4
    LVP = 5
    REP = 6

    @staticmethod
    def from_bytes(payload: bytes):
        return State(*struct.unpack("B", payload))

@dataclass
class Measurement:
    voltage: float
    current: float
    power: float

    @staticmethod
    def from_bytes(payload: bytes):
        return Measurement(*struct.unpack("<fff", payload))

def int_format(b: bytes) -> int:
    return struct.unpack("B", b)[0]

def bool_format(b: bytes) -> bool:
    return struct.unpack("?", b)[0]

def float_format(b: bytes) -> float:
    return struct.unpack("<f", b)[0]

def str_format(b: bytes) -> str:
    return b.decode()

@dataclass
class Dump:
    input_voltage: float
    v_set: float
    i_set: float
    voltage: float
    current: float
    power: float
    temperature: float
    m1_voltage: float
    m1_current: float
    m2_voltage: float
    m2_current: float
    m3_voltage: float
    m3_current: float
    m4_voltage: float
    m4_current: float
    m5_voltage: float
    m5_current: float
    m6_voltage: float
    m6_current: float
    ovp: float
    ocp: float
    opp: float
    otp: float
    lvp: float
    brightness: int
    volume: int
    metering: bool
    capacity: float
    energy: float
    running: bool
    protection: int
    cc_or_cv: bool
    identifier: int # Device identifier
    max_voltage: float # Maximum voltage which can be set (v_set) available at current moment (input_voltage - 0.2V)
    max_current: float # Maximum current which can be set (i_set) available at current moment

    # The next 5 fields is maximum values for protection settings (ovp, ocp, opp, otp, lvp)
    # They are usually constants (doesn't depends on current operation values)

    max_ovp: float # Maximum OVP (30V)
    max_ocp: float # Maximum OCP (5.1A)
    max_opp: float # Maximum OPP (150W)
    max_otp: float # Maximum OTP (99C)
    max_lvp: float # Maximum LVP (30V)

    @staticmethod
    def from_bytes(payload: bytes):
        return Dump(*struct.unpack("<ffffffffffffffffffffffffBB?ff?B?Bfffffff", payload))

class Field(utils.IntEnumWithHexStr):
    formatter: Callable[[bytes],Any] | None

    def __new__(cls, value: int, format: Callable[[bytes],Any] | None):
        member = int.__new__(cls, value)
        member._value_ = value
        member.formatter = format
        return member

    NONE = 0x00, None
    
    INPUT_VOLTAGE = 0xC0, float_format
    V_SET = 0xC1, float_format
    I_SET = 0xC2, float_format
    MEASUREMENT = 0xC3, Measurement.from_bytes,  # 3 floats with measured Voltage, Current, Power
    TEMPERATURE = 0xC4, float_format

    M1_VOLTAGE = 0xC5, float_format
    M1_CURRENT = 0xC6, float_format
    M2_VOLTAGE = 0xC7, float_format
    M2_CURRENT = 0xC8, float_format
    M3_VOLTAGE = 0xC9, float_format
    M3_CURRENT = 0xCA, float_format
    M4_VOLTAGE = 0xCB, float_format
    M4_CURRENT = 0xCC, float_format
    M5_VOLTAGE = 0xCD, float_format
    M5_CURRENT = 0xCE, float_format
    M6_VOLTAGE = 0xCF, float_format
    M6_CURRENT = 0xD0, float_format

    OVP = 0xD1, float_format # Over voltage protection value (V) 
    OCP = 0xD2, float_format # Over current protection value (A)
    OPP = 0xD3, float_format # Over power protection value (W)
    OTP = 0xD4, float_format # Over temperature protection value (C)
    LVP = 0xD5, float_format # Under voltage protection value (V)

    BRIGHTNESS = 0xD6, int_format # 1 - 14 (1 - min brightness, 14 - max brightness)
    VOLUME = 0xD7, int_format # 0 - 15 (0 mute, 15 max volume)

    METERING = 0xD8, bool_format # Starts measuring Energy And Capacity (0 - disable, 1 - enable)
    CAPACITY = 0xD9, float_format # Measured capacity (Ampere/Hour)
    ENERGY = 0xDA, float_format # Measured energy (Watt/Hour)
    RUNNING = 0xDB, bool_format # STOP = 0, RUN = 1
    STATE = 0xDC, State.from_bytes  # current protection state
    CC_CV = 0xDD, bool_format # CC = 0, CV = 1

    MODEL_NAME = 0xDE, str_format # Model name (DPS-150)
    HARDWARE_VERSION = 0xDF, str_format # HW version (V1.0)
    FIRMWARE_VERSION = 0xE0, str_format # FW version (V1.2)

    IDENTIFIER = 0xE1, int_format # One byte int - device identifier (can be changed in settings, useful to distinguish between multiple DPS-150)

    MAX_VOLTAGE = 0xE2, float_format # Maximum available voltage to set
    MAX_CURRENT = 0xE3, float_format # Maximum current to set
    MAX_OVP = 0xE4, float_format # Maximum OVP value (30V)
    MAX_OCP = 0xE5, float_format # Maximum OCP value (5.1A)
    MAX_OPP = 0xE6, float_format # Maximum OPP value (150W)
    MAX_OTP = 0xE7, float_format # Maximum OTP value (99C)
    MAX_LVP = 0xE8, float_format # Maximum LVP value (30V)

    ALL = 0xFF, Dump.from_bytes
    

@dataclass
class Frame:
    dir: Dir
    action: Action
    field: Field
    payload: bytes
    checksum: int

    def verify_checksum(self) -> bool:
        return self.checksum == self.compute_checksum()

    def compute_checksum(self) -> int:
        return (self.field.value + len(self.payload) + sum(self.payload)) & 0xFF

    @staticmethod
    def v(action: Action, field: Field, payload: Any | None = None) -> "Frame":
        frame = Frame(Dir.HOST_TO_DEVICE, action, field, utils.generic_to_bytes(payload), 0) 
        frame.checksum = frame.compute_checksum()
        return frame
    
    def write(self, port: serial.Serial):
        logging.info(">> %s", self.log_format())
        port.write(self.to_bytes())

    @staticmethod
    def read(port: serial.Serial) -> "tuple[Frame, Any | None] | None":
        rx_seq = Dir.DEVICE_TO_HOST.to_bytes()
        start_seq = port.read_until(rx_seq, 1024)
        if not start_seq.endswith(rx_seq):
            return None
        head = port.read(3)
        if len(head) != 3:
            return None
        tail = port.read(head[2] + 1)

        frame = Frame(Dir(start_seq[-1]), Action(head[0]), Field(head[1]), tail[:-1], tail[-1])
        logging.info("<< %s", frame.log_format())
        return (frame, frame.decode())

    def decode(self) -> Any | None:
        return (self.field.formatter(self.payload) 
                if (self.dir == Dir.DEVICE_TO_HOST or self.action == Action.SET) and self.field.formatter is not None 
                else None)

    def log_format(self) -> str:
        d = {
            "Frame": self.to_bytes().hex().upper(),
            "Dir": self.dir,
            "Action": self.action,
            "Field": self.field,
            "Payload": self.payload.hex().upper(),
            "Checksum": f"0x{self.checksum:02X}",
            "Valid": "OK" if self.verify_checksum() else "FAIL",
            "Value": self.decode()
        }
        return ", ".join(k + "=" + str(v) for k, v in d.items())


    def to_bytes(self) -> bytes:
        return (struct.pack("BBBB", self.dir, self.action, self.field, len(self.payload)) 
                + self.payload 
                + struct.pack("B", self.checksum))
    

def read_frames(port: serial.Serial):
    while Frame.read(port) is not None:
        pass


with serial.Serial(
    port='/dev/ttyACM0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.1
) as port:

    logging.info("LOCK")
    Frame.v(Action.LOCK, Field.NONE, True).write(port)
    try:

        baud_rate_value = BAUD_RATES.get(port.baudrate, 0)
        logging.info("READ INIT DATA, BAUDRATE = %s", baud_rate_value)

        # Frame.v(Action.BAUD, Field.NONE, baud_rate_value).write(port)
        Frame.v(Action.GET, Field.MODEL_NAME).write(port)
        Frame.v(Action.GET, Field.FIRMWARE_VERSION).write(port)
        Frame.v(Action.GET, Field.HARDWARE_VERSION).write(port)
        Frame.v(Action.GET, Field.STATE).write(port)
        Frame.v(Action.GET, Field.IDENTIFIER).write(port)
        Frame.v(Action.GET, Field.CC_CV).write(port)
        Frame.v(Action.SET, Field.METERING, True).write(port)
        Frame.v(Action.GET, Field.BRIGHTNESS).write(port)
        Frame.v(Action.GET, Field.VOLUME).write(port)
        Frame.v(Action.GET, Field.ALL).write(port)
        
        read_frames(port)

        Frame.v(Action.SET, Field.V_SET, 1.9).write(port)
        for i in range(1,5):
            read_frames(port)

        Frame.v(Action.SET, Field.RUNNING, True).write(port)
        
        for i in range(1,5):
            read_frames(port)
            time.sleep(1)

        Frame.v(Action.SET, Field.RUNNING, False).write(port)
        for i in range(1,5):
            read_frames(port)

    finally:
        logging.info("UNLOCK")
        Frame.v(Action.LOCK, Field.NONE, False).write(port)

