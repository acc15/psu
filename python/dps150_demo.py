import time
import serial
import struct

from typing import Callable, Any
from enum import IntEnum
from dataclasses import dataclass

BAUD_RATES = { 9600:1, 19200:2, 38400:3, 57600:4, 115200:5 }

class Dir(IntEnum):
    TX = 0xF1
    RX = 0xF0

    def as_bytes(self):
        return bytes([self.value])

class Action(IntEnum):
    GET = 0xA1
    BAUD = 0xB0
    SET = 0xB1
    LOCK = 0xC1

class ProtectionState(IntEnum):
    NONE = 0
    OVP = 1
    OCP = 2
    OPP = 3
    OTP = 4
    LVP = 5
    REP = 6

    @staticmethod
    def from_bytes(payload: bytes):
        return ProtectionState(*struct.unpack("B", payload))

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

class Field(IntEnum):
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
    RUNNING = 0xDB, bool_format # RUN = 1, STOP = 0
    PROTECTION = 0xDC, ProtectionState.from_bytes  # current protection state
    CV_CC = 0xDD, bool_format # CV == 1, CC == 0

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
class DataFrame:
    
    action: Action
    field: Field
    payload: bytes

    def compute_checksum(self) -> int:
        return (self.field.value + len(self.payload) + sum(self.payload)) & 0xFF
    
    def total_bytes(self) -> int:
        return len(self.payload) + 5
    
    def write(self, port: serial.Serial):
        port.write(bytes(self))

    @staticmethod
    def read(port: serial.Serial) -> "DataFrame | None":
        rx_seq = Dir.RX.as_bytes()
        start_seq = port.read_until(rx_seq, 1024)
        if not start_seq.endswith(rx_seq):
            return None
        head = port.read(3)
        if len(head) != 3:
            return None
        tail = port.read(head[2] + 1)
        frame = DataFrame(Action(head[0]), Field(head[1]), tail[:-1])
        data_checksum = tail[-1]
        computed_checksum = frame.compute_checksum()
        if data_checksum != computed_checksum:
            raise RuntimeError(f"DPS-150: Checksum mismatch. Data checksum: {data_checksum:02X}, computed checksum: {computed_checksum:02X}")
        return frame

    def __bytes__(self) -> bytes:
        return bytes([
            Dir.TX.value, 
            self.action.value, 
            self.field.value, 
            len(self.payload)
        ]) + self.payload + bytes([self.compute_checksum()])
    

port = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.1
)

def read_frames(port: serial.Serial):
    while (frame := DataFrame.read(port)) is not None:
        d = {
            "Frame": bytes(frame).hex(),
            "Action": f"{frame.action.name}({frame.action.value}, {frame.action.value:2X})",
            "Field": f"{frame.field.name}({frame.field.value}, {frame.field.value:2X})",
            "Payload": frame.payload.hex().upper(),
            "Checksum": f"{frame.compute_checksum():2X}",
            "Valid": "OK" if frame.verify_checksum() else "FAIL"
        }

        if frame.field.formatter is not None:
            d["Value"] = repr(frame.field.formatter(frame.payload))

        print(", ".join(k + "=" + v for k, v in d.items()))

if port.is_open:l,k.
    print("opened")

print("LOCK")
port.write(DataFrame.tx(Action.LOCK, Field.NONE, b"\x01"))
try:

    baud_rate_value = BAUD_RATES.get(port.baudrate, 0) /
    print(f"READ INIT DATA, BAUDRATE = {baud_rate_value}")

    DataFrame(Action.BAUD, Field.NONE, bytes([baud_rate_value])).write(port)
    DataFrame(Action.GET, Field.MODEL_NAME).write(port)
    DataFrame(Action.GET, Field.FIRMWARE_VERSION).write(port)
    DataFrame(Action.GET, Field.HARDWARE_VERSION).write(port)
    DataFrame(Action.GET, Field.PROTECTION).write(port)
    DataFrame(Action.GET, Field.IDENTIFIER).write(port)
    DataFrame(Action.GET, Field.CV_CC).write(port)
    DataFrame(Action.SET, Field.METERING, b"\x01").write(port)
    DataFrame(Action.GET, Field.BRIGHTNESS).write(port)
    DataFrame(Action.GET, Field.VOLUME).write(port)
    DataFrame(Action.GET, Field.ALL).write(port)
    
    read_frames(port)

    print("V_SET")

    DataFrame(Action.SET, Field.V_SET, struct.pack("<f", 1.9)).write(port)
    for i in range(1,5):
        read_frames(port)

    print("RUN")

    DataFrame(Action.SET, Field.RUNNING, b"\x01").write(port)
    
    for i in range(1,5):
        read_frames(port)
        time.sleep(1)

    print("STOP")

    DataFrame(Action.SET, Field.RUNNING, b"\x00").write(port)
    for i in range(1,5):
        read_frames(port)

    print("UNLOCK")
finally:
    port.write(DataFrame.tx(Action.LOCK, Field.NONE, b"\x00"))

