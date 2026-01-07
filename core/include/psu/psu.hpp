#pragma once

namespace psu {

struct va {
    float voltage;
    float current;
};

enum class protection {
    OK,
    OVP,
    OCP,
    OPP,
    OTP,
    LVP,
};

class psu {


    virtual struct va current() = 0;
    virtual struct va set() = 0;

    // virtual std::vector<va> presets() = 0;

    // virtual std::vector<

};

}