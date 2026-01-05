#pragma once

#include <cstdint>
#include <vector>
#include <string>

namespace psu::dps150 {

constexpr int VID = 0x2e3c;
constexpr int PID = 0x5740;

enum class dir: std::uint8_t {
    TX = 0xF1,
    RX = 0xF0
};

enum class action: std::uint8_t {
    GET = 0xA1,
    BAUD = 0xB0,
    SET = 0xB1,
    LOCK = 0xC1
};

constexpr std::uint32_t baud_rates[] = { 
    0, 
    9600, 
    19200, 
    38400, 
    57600, 
    115200 
};

enum class state: std::uint8_t {
    OK = 0,
    OVP = 1,
    OCP = 2,
    OPP = 3,
    OTP = 4,
    LVP = 5,
    REP = 6
};

struct va {
    float voltage;
    float current;
};

struct measurement: public va {
    float power;
};

struct protection {
    float ovp;
    float ocp;
    float opp;
    float otp;
    float lvp;
};

struct dump {
    float               input_voltage;
    va                  set;
    struct measurement  measurement;
    float               temperature;
    va                  presets[6];
    struct protection   protection;
    std::uint8_t        brightness;
    std::uint8_t        volume;
    bool                metering;
    float               capacity;
    float               energy;
    bool                running;
    enum state          state;
    bool                cc_or_cv;
    std::uint8_t        identifier;
    va                  max_preset;
    struct protection   max_protection;
};

enum class field: std::uint8_t {

    NONE = 0x00,
    
    INPUT_VOLTAGE = 0xC0, // Float32
    V_SET = 0xC1, // Float32
    I_SET = 0xC2, // Float32
    MEASUREMENT = 0xC3, // 3 Float32 with measured Voltage, Current, Power
    TEMPERATURE = 0xC4, // Float32 (in Celsius)

    M1_VOLTAGE = 0xC5, // Float32, M1 voltage
    M1_CURRENT = 0xC6, // Float32, M1 current
    M2_VOLTAGE = 0xC7, // Float32, M2 voltage
    M2_CURRENT = 0xC8, // Float32, M2 current
    M3_VOLTAGE = 0xC9, // Float32, M3 voltage
    M3_CURRENT = 0xCA, // Float32, M3 current
    M4_VOLTAGE = 0xCB, // Float32, M4 voltage
    M4_CURRENT = 0xCC, // Float32, M4 current
    M5_VOLTAGE = 0xCD, // Float32, M5 voltage
    M5_CURRENT = 0xCE, // Float32, M5 current
    M6_VOLTAGE = 0xCF, // Float32, M6 voltage
    M6_CURRENT = 0xD0, // Float32, M6 current

    OVP = 0xD1, // Float32, Over voltage protection Float32 (Volts)
    OCP = 0xD2, // Float32, Over current protection Float32 (Ampheres)
    OPP = 0xD3, // Float32, Over power protection Float32 (Watts)
    OTP = 0xD4, // Float32, Over temperature protection (Celsius)
    LVP = 0xD5, // Float32, Under voltage protection (Volts)

    BRIGHTNESS = 0xD6, // 1 byte, [1..14] (1 - min brightness, 14 - max brightness)
    VOLUME = 0xD7, // 1 byte, [0..15] (0 mute, 15 max volume)

    METERING = 0xD8, // 1 byte bool, Starts measuring Energy And Capacity (0 - disable, 1 - enable)
    CAPACITY = 0xD9, // Float32, Measured capacity Float32
    ENERGY = 0xDA, // Float32,Measured energy Float32
    RUNNING = 0xDB, // 1 byte bool RUN = 1, STOP = 0
    PROTECTION = 0xDC, // 1 byte, [0..6] current protection state (see protection_state enum)
    CV_CC = 0xDD, // 1 byte bool, CV == 1, CC == 0

    MODEL_NAME = 0xDE, // String, Model name
    HARDWARE_VERSION = 0xDF, // String, HW version
    FIRMWARE_VERSION = 0xE0, // String, FW version

    IDENTIFIER = 0xE1, // 1 byte 0-30, Device identifier (can be changed in settings, useful to distinguish between multiple DPS-150)
    MAX_VOLTAGE = 0xE2, // Float32, Maximum available voltage to set
    MAX_CURRENT = 0xE3, // Float32, Maximum current to set

    MAX_OVP = 0xE4, // Float32, Maximum OVP value (30V)
    MAX_OCP = 0xE5, // Float32, Maximum OCP value (5.1A)
    MAX_OPP = 0xE6, // Float32, Maximum OPP value (150W)
    MAX_OTP = 0xE7, // Float32, Maximum OTP value (99C)
    MAX_LVP = 0xE8, // Float32, Maximum LVP value (30V)

    ALL = 0xFF // Dumps all data

};

struct frame {
    enum dir dir;
    enum action action;
    enum field field;
    std::vector<std::uint8_t> payload;
    std::uint8_t checksum;
};

std::uint8_t get_baud_rate_index(std::uint32_t baud_rate);
std::uint8_t compute_checksum(std::uint8_t field, std::uint8_t size, const void* payload);

std::vector<std::string> find_ports();

}