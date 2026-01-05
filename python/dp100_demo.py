import hid
import enum
import struct
import time
from dataclasses import dataclass
from typing import Callable, Any, cast
from decimal import Decimal
import logging

import utils

class Dir(utils.IntEnumWithHexStr):
    HOST_TO_DEVICE = 0xFB
    DEVICE_TO_HOST = 0xFA

class Output(utils.IntEnumWithHexStr):
    CC = 0
    CV = 1
    STOPPED = 2
    NO_INPUT = 130

class State(utils.IntEnumWithHexStr):
    OK = 0
    OVP = 1
    OCP = 2
    OPP = 3
    OTP = 4
    REP = 5
    UVP = 6

class BasicSetOp(utils.IntEnumWithHexStr):
    GET_PRESET = 0,
    SET_CURRENT = 2,
    SET_PRESET = 6,
    GET_CURRENT = 8,
    USE_PRESET = 10


@dataclass
class DeviceInfo:
    name: str
    hw_ver: Decimal
    sw_ver: Decimal
    boot_ver: Decimal
    run_area: int
    sn: bytes
    year: int
    month: int
    day: int

    @staticmethod
    def format_ver(v: int):
        return Decimal(v).scaleb(-1)

    @staticmethod
    def from_bytes(payload: bytes) -> "DeviceInfo":
        values = struct.unpack("<16sHHHH12sHBB", payload)
        result = DeviceInfo(*values)
        result.hw_ver = DeviceInfo.format_ver(result.hw_ver)
        result.sw_ver = DeviceInfo.format_ver(result.sw_ver)
        result.boot_ver = DeviceInfo.format_ver(result.boot_ver)
        result.name = cast(bytes, result.name).split(b"\x00")[0].decode()
        return result

@dataclass
class SystemInfo:
    otp: Decimal
    opp: Decimal
    backlight: int
    volume: int
    rep: bool
    auto_on: bool

    @staticmethod
    def from_bytes(payload: bytes) -> "SystemInfo":
        if len(payload) == 1:
            return bool(payload[0])

        values = struct.unpack("<HHBB??", payload)
        result = SystemInfo(*values)
        result.otp = Decimal(result.otp).scaleb(0)
        result.opp = Decimal(result.opp).scaleb(-1)
        return result

    def to_bytes(self):
        return struct.pack("<HHBB??", 
            int(self.otp), 
            int(self.opp.scaleb(1)), 
            self.backlight,
            self.volume, 
            self.rep, 
            self.auto_on
        )

@dataclass
class BasicInfo:

    v_in: Decimal
    v_out: Decimal
    i_out: Decimal
    v_max: Decimal
    temp1: Decimal
    temp2: Decimal
    dc5v: Decimal
    out: Output
    state: State

    @staticmethod
    def from_bytes(payload: bytes) -> "BasicInfo":
        values = struct.unpack("<HHHHHHHBB", payload)
        result = BasicInfo(*values)
        result.v_in = Decimal(result.v_in).scaleb(-3)
        result.v_out = Decimal(result.v_out).scaleb(-3)
        result.i_out = Decimal(result.i_out).scaleb(-3)
        result.v_max = Decimal(result.v_max).scaleb(-3)
        result.temp1 = Decimal(result.temp1).scaleb(-1)
        result.temp2 = Decimal(result.temp2).scaleb(-1)
        result.dc5v  = Decimal(result.dc5v).scaleb(-3)
        result.out = Output(result.out)
        result.state = State(result.state)
        return result


@dataclass
class BasicSetAction:
    op: BasicSetOp
    preset: int

    def from_int(v: int):
        return BasicSetAction(BasicSetOp((v & 0xF0) >> 4), v & 0x0F)

    def __int__(self):
        return ((self.op.value << 4) & 0xF0) | (self.preset & 0x0F)
    
    def to_bytes(self):
        if self.op == BasicSetOp.USE_PRESET:
            return bytes([int(self),0,0,0,0,0,0,0,0,0])
        return bytes([int(self)])

@dataclass
class BasicSet:
    action: BasicSetAction
    on: bool
    v_set: Decimal
    i_set: Decimal
    ovp: Decimal
    ocp: Decimal

    @staticmethod
    def from_bytes(payload: bytes) -> "BasicSet":
        if len(payload) == 1:
            return bool(payload[0])

        values = struct.unpack("<B?HHHH", payload)
        result = BasicSet(
            BasicSetAction.from_int(values[0]), 
            values[1], 
            Decimal(values[2]).scaleb(-3),
            Decimal(values[3]).scaleb(-3),
            Decimal(values[4]).scaleb(-3),
            Decimal(values[5]).scaleb(-3),
        )
        return result
    
    def to_bytes(self):
        return struct.pack("<B?HHHH", 
            int(self.action),
            self.on,
            int(self.v_set.scaleb(3)),
            int(self.i_set.scaleb(3)),
            int(self.ovp.scaleb(3)),
            int(self.ocp.scaleb(3)),
        )


def modbus_crc16(data:bytes) -> int:
    crc = 0xFFFF
    for n in data:
        crc ^= n
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


class Op(utils.IntEnumWithHexStr):
    formatter: Callable[[bytes],Any] | None

    def __new__(cls, value: int, format: Callable[[bytes],Any] | None):
        member = int.__new__(cls, value)
        member._value_ = value
        member.formatter = format
        return member

    DEVICE_INFO	= 0x10, DeviceInfo.from_bytes
    FIRMWARE_INFO = 0x11, DeviceInfo.from_bytes
    START_TRANS	= 0x12, None
    DATA_TRANS = 0x13, None
    END_TRANS = 0x14, None
    DEV_UPGRADE	= 0x15, None
    BASIC_INFO = 0x30, BasicInfo.from_bytes
    BASIC_SET = 0x35, BasicSet.from_bytes
    SYSTEM_INFO	= 0x40, SystemInfo.from_bytes
    SYSTEM_SET = 0x45, None
    SCAN_OUT = 0x50, None
    SERIAL_OUT = 0x55, None
    DISCONNECT = 0x80, None

@dataclass
class Frame:
    dir: Dir
    op: Op
    sequence: int
    payload: bytes
    checksum: int

    @staticmethod
    def v(op: Op, payload: Any|None = None) -> "Frame":
        frame = Frame(Dir.HOST_TO_DEVICE, op, 0x0, utils.generic_to_bytes(payload), 0)
        frame.checksum = frame.compute_checksum()
        return frame

    def write(self, h: hid.Device):
        logging.info(">> %s", self.log_format())
        return h.write(self.to_bytes())

    @staticmethod
    def read(h: hid.Device, timeout: Any | None = 1) -> "tuple[Frame, Any | None]":
        frame = Frame.from_bytes(h.read(64, timeout))
        logging.info("<< %s", frame.log_format())
        return (frame, frame.decode())

    def decode(self) -> Any | None:
        return (self.op.formatter(self.payload) 
                if self.dir == Dir.DEVICE_TO_HOST and self.op.formatter is not None 
                else None)

    @staticmethod
    def from_bytes(data: bytes) -> "Frame":
        dir_byte, op, sequence, payload_len = struct.unpack("<BBBB", data[:4])
        dir = Dir(dir_byte)
        
        if dir != Dir.DEVICE_TO_HOST:
            raise RuntimeError(f"DP100. Invalid data flow direction byte: {dir:02X}")
        
        payload = data[4:4+payload_len]
        checksum = struct.unpack("<H", data[4+payload_len:4+payload_len+2])[0]
        return Frame(dir, Op(op), sequence, payload, checksum)
    
    def head_bytes(self):
        return struct.pack("<BBBB", self.dir, self.op, self.sequence, len(self.payload)) + self.payload

    def compute_checksum(self):
        return modbus_crc16(self.head_bytes())
    
    def verify_checksum(self):
        return self.checksum == self.compute_checksum()

    def to_bytes(self):
        return self.head_bytes() + struct.pack("<H", self.checksum)
    
    def log_format(self) -> str:
        d = {
            "Frame": self.to_bytes().hex().upper(),
            "Dir": self.dir,
            "Op": self.op,
            "Payload": self.payload.hex().upper(),
            "Checksum": f"0x{self.checksum:02X}",
            "Valid": "OK" if self.verify_checksum() else "FAIL",
            "Value": self.decode()
        }
        return ", ".join(k + "=" + str(v) for k, v in d.items())


with hid.Device(0x2e3c, 0xaf01) as h:
    logging.info("Device manufacturer: %s", h.manufacturer)
    logging.info("Product: %s", h.product)
    logging.info("Serial Number: %s", h.serial)

    Frame.v(Op.DEVICE_INFO).write(h)
    Frame.read(h)

    Frame.v(Op.FIRMWARE_INFO).write(h)
    Frame.read(h)

    Frame.v(Op.SYSTEM_INFO).write(h)
    si: SystemInfo
    _, si = Frame.read(h)

    b_set = BasicSet(
        BasicSetAction(BasicSetOp.SET_CURRENT, 0), 
        False, 
        Decimal(1), 
        Decimal(0.01), 
        Decimal(30.5), 
        Decimal(5.05)
    )

    for i in range(5):
        si.backlight = i
        Frame.v(Op.SYSTEM_INFO, si).write(h)
        Frame.read(h)
        
        b_set.on = True
        b_set.v_set = Decimal(i)

        Frame.v(Op.BASIC_SET, b_set).write(h)
        Frame.read(h)

        Frame.v(Op.BASIC_INFO).write(h)
        Frame.read(h)

        time.sleep(1)

    Frame.v(Op.BASIC_INFO).write(h)
    Frame.read(h)

    b_set.on = False
    Frame.v(Op.BASIC_SET, b_set).write(h)

    # Frame.v(Operation.SYSTEM_SET).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # time.sleep(1)

    # si.backlight = 1
    # Frame(Operation.SYSTEM_INFO, si).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # Frame(Operation.SYSTEM_SET).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # time.sleep(1)

    # si.backlight = 2
    # Frame(Operation.SYSTEM_INFO, si).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # Frame(Operation.SYSTEM_SET).write(h)
    # print(Frame.decode(h.read(64, 1)))


    # Frame(Operation.BASIC_SET, BasicSetAction(BasicSetOp.GET_CURRENT, 0)).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # Frame(Operation.BASIC_SET, BasicSetAction(BasicSetOp.USE_PRESET, 2)).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # Frame(Operation.BASIC_SET, BasicSetAction(BasicSetOp.GET_CURRENT, 0)).write(h)
    # preset: BasicSet
    # frame, preset = Frame.decode(h.read(64, 1))
    # preset.action.op = BasicSetOp.SET_CURRENT
    # preset.on = True

    # Frame(Operation.BASIC_SET, preset).write(h)
    # print(Frame.decode(h.read(64, 1)))
    

    # Frame(Operation.BASIC_SET, preset).write(h)
    # Frame.decode(h.read(64, 1))

    # time.sleep(1)

    # Frame(Operation.BASIC_SET, 0, BasicSet(
    #     BasicSetAction(BasicSetOp.SET_CURRENT, 0), 
    #     False, 
    #     Decimal(5), 
    #     Decimal(0.1), 
    #     Decimal(30.5), 
    #     Decimal(5.05)
    # )).write(h)
    # print(Frame.decode(h.read(64, 1)))

    # for p in range(10):
    #     print(f"Preset [{p}]")
    #     Frame(Operation.BASIC_SET, 0, BasicSetAction(BasicSetOp.GET_PRESET, p)).write(h)
    #     print(Frame.decode(h.read(64, 1)))

    # h.write()

    # while True:
    #     h.write(Frame(Operation.BASIC_INFO, 0, b"").to_bytes())
    #     print(Frame.decode(h.read(64, 1)))
    #     time.sleep(1)
