#pragma once

#include <functional>
#include <span>

#include "type.hpp"

namespace psu::core {

enum class mode {
    OFF,
    CV,
    CC
};

enum class protection {
    OK,
    OVP,
    OCP,
    OPP,
    OTP,
    LVP
};

class psu;

template <typename T>
class psu_value {
    
    T value_;

    std::function<void(psu_value<T>&)> on_set;
    std::function<void(psu_value<T>&)> on_query;

public:
    std::function<void(psu_value<T>&)> on_change;

    void query() {
        if (on_query) {
            on_query(*this);
        }
    }
    
    operator const T&() const {
        return value_;
    }

    psu_value<T>& operator=(const T& value) {
        if (on_set) {
            value_ = value;
            on_set(*this);
        }
        return *this;
    }

    bool readonly() const {
        return static_cast<bool>(on_set);
    }

    friend psu;
};

struct psu_preset {
    psu_value<float> v;
    psu_value<float> i;
    props_value rest;
};

class psu {

protected:
    template<typename T>
    void update(psu_value<T>& psu_value, const T& value) {
        psu_value.value_ = value;
        if (psu_value.on_change) {
            psu_value.on_change(psu_value);
        }
    }

    std::vector<psu_preset> presets_; // presets span (its pointer to internal implementation array or std::vector)

public:
    psu_value<float>        v_cur;
    psu_value<float>        i_cur;
    psu_value<float>        p_cur;

    psu_value<float>        v_set;
    psu_value<float>        i_set;
    
    psu_value<mode>         mode;
    psu_value<protection>   state;

    psu_value<float>        temperature;
    psu_value<float>        ovp;
    psu_value<float>        ocp;
    psu_value<float>        opp;
    psu_value<float>        otp;
    psu_value<float>        lvp;

    std::span<psu_preset> presets() {
        return presets_;
    }

    props_value rest;


    // virtual std::vector<va> presets() = 0;

    // virtual std::vector<

};

}