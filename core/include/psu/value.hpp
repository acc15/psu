#pragma once

#include <functional>

namespace psu {


template <typename T>
class psu_value {
    T value_;

    std::function<void(const T&)> on_query;
    std::function<void(const T&)> on_set;
    std::function<void(const T&)> update_;

public:
    // psu_value(psu_driver_listener<T>* driver): value_(), driver_(driver) {}

    const T& get() const {
        return value_;
    }

    void set(const T& v) const {
        if (value_ != v) {
            value_ = v;
            if (on_set) on_set(value_);
        }
    }

    void update(const T& v) const {
        if (value_ != v) {
            value_ = v;
            if (update_) update_(value_);
        }
    }

    void query() {
        if (on_query) on_query();
    }

};

}