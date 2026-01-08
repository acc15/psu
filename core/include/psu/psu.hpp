#pragma once

#include <span>

namespace psu {

enum class protection {
    OK,
    OVP,
    OCP,
    OPP,
    OTP,
    LVP
};

template <typename T>
struct psu_value {
    void query(); // query value update
    const T& get() const; // return current instant value
    bool set(const T& value); // sets new value and schedules device update
    bool readonly() const; // checks whether its readonly (like measured voltage), or its rw (can be retrieved and changed)
};

struct psu_preset {
    psu_value<float> v;
    psu_value<float> i;
};

struct psu {

    psu_value<float> v_cur;
    psu_value<float> i_cur;
    psu_value<float> p_cur;

    psu_value<float> v_set;
    psu_value<float> i_set;
    
    psu_value<bool> running;
    psu_value<protection> state;

    psu_value<float> temp;
    psu_value<float> ovp;
    psu_value<float> ocp;
    psu_value<float> opp;
    psu_value<float> otp;
    psu_value<float> lvp;

    std::span<psu_preset> presets; // presets span (its pointer to internal implementation array or std::vector)

    //std::unordered_map<std::string, psu_value<typed_value>>& rest;


    // virtual std::vector<va> presets() = 0;

    // virtual std::vector<

};

}