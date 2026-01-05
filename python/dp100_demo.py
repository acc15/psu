import hid
import enum
import struct
import time
from dataclasses import dataclass
from typing import Callable, Any, cast
from decimal import Decimal

class Dir(enum.IntEnum):
    HOST_TO_DEVICE = 0xFB
    DEVICE_TO_HOST = 0xFA


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

    def __bytes__(self):
        return struct.pack("<HHBB??", 
            int(self.otp), 
            int(self.opp.scaleb(1)), 
            self.backlight,
            self.volume, 
            self.rep, 
            self.auto_on
        )

class Output(enum.IntEnum):
    CC = 0
    CV = 1
    STOPPED = 2
    NO_INPUT = 130

class State(enum.IntEnum):
    OK = 0
    OVP = 1
    OCP = 2
    OPP = 3
    OTP = 4
    REP = 5
    UVP = 6

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

class BasicSetOp(enum.IntEnum):
    GET_PRESET = 0,
    SET_CURRENT = 2,
    SET_PRESET = 6,
    GET_CURRENT = 8,
    USE_PRESET = 10

@dataclass
class BasicSetAction:
    op: BasicSetOp
    preset: int

    def from_int(v: int):
        return BasicSetAction(BasicSetOp((v & 0xF0) >> 4), v & 0x0F)

    def __int__(self):
        return ((self.op.value << 4) & 0xF0) | (self.preset & 0x0F)
    
    def __bytes__(self):
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
    
    def __bytes__(self):
        return struct.pack("<B?HHHH", 
            int(self.action),
            self.on,
            int(self.v_set.scaleb(3)),
            int(self.i_set.scaleb(3)),
            int(self.ovp.scaleb(3)),
            int(self.ocp.scaleb(3)),
        )



class Operation(enum.IntEnum):

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


def modbus_crc(data:bytes) -> int:
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

@dataclass
class Frame:
    op: Operation
    payload: bytes = b""

    def __post_init__(self):
        if not isinstance(self.payload, bytes):
            self.payload = bytes(self.payload) 


    def write(self, h: hid.Device):
        print(">>", self)
        return h.write(bytes(self))

    @staticmethod
    def read(h: hid.Device, timeout: Any | None = 1) -> "tuple[Frame, Any | None]":
        return Frame.decode(h.read(64, timeout))

    @staticmethod
    def decode(frame_data: bytes) -> "tuple[Frame, Any | None]":
        frame = Frame.from_bytes(frame_data)
        parsed_frame = None
        if frame.op.formatter is not None:
            parsed_frame = frame.op.formatter(frame.payload)
        return (frame, parsed_frame)

    @staticmethod
    def from_bytes(data: bytes) -> "Frame":
        if data[0] != Dir.DEVICE_TO_HOST.value:
            raise RuntimeError(f"DP100. Invalid data flow direction byte: {data[0]:02X}")
        data_crc = struct.unpack("<H", data[4+data[3]:4+data[3]+2])[0]
        computed_crc = modbus_crc(data[0:4+data[3]])        
        if data_crc != computed_crc:
            raise RuntimeError(f"DP100. Invalid CRC16 value. Data CRC: {data_crc:04X}, computed CRC: {computed_crc:04X}")
        return Frame(Operation(data[1]), data[4:4+data[3]])

    def __bytes__(self):
        frame_data = bytes([
            Dir.HOST_TO_DEVICE, 
            self.op.value, 
            0x0, 
            len(self.payload)]) + self.payload
        crc = modbus_crc(frame_data)
        data = frame_data + struct.pack("<H", crc)
        return data


with hid.Device(0x2e3c, 0xaf01) as h:
    print(f'Device manufacturer: {h.manufacturer}')
    print(f'Product: {h.product}')
    print(f'Serial Number: {h.serial}')

    Frame(Operation.DEVICE_INFO).write(h)
    print(Frame.decode(h.read(64, 1)))

    Frame(Operation.FIRMWARE_INFO).write(h)
    print(Frame.decode(h.read(64, 1)))

    Frame(Operation.SYSTEM_INFO).write(h)
    si: SystemInfo
    f, si = Frame.decode(h.read(64, 1))
    print((f, si))

    # time.sleep(1)

    for i in range(5):
        si.backlight = i
        Frame(Operation.SYSTEM_INFO, si).write(h)
        print(Frame.decode(h.read(64, 1)))
        
        Frame(Operation.BASIC_SET, BasicSet(
            BasicSetAction(BasicSetOp.SET_CURRENT, 0), 
            False, 
            Decimal(i), 
            Decimal(0.1), 
            Decimal(30.5), 
            Decimal(5.05)
        )).write(h)
        
        print(Frame.decode(h.read(64, 1)))
        time.sleep(1)


    # Frame(Operation.SYSTEM_SET).write(h)
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
