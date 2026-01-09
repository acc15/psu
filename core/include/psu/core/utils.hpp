#pragma once

#include <string>
#include <ranges>

namespace psu::core {

template <typename T, auto Deleter, T default_value = {}>
struct [[nodiscard]] resource {
    T ref;
    
    resource(): resource(default_value) {}
    resource(T init): ref(init) {}
    
    resource(const resource&) = delete;
    resource& operator=(const resource&) = delete;
    
    resource(resource&& other) noexcept : resource(other.ref) { 
        other.ref = default_value; 
    }

    ~resource() { 
        if (ref != default_value) {
            Deleter(ref);
        }
    }
    
    operator bool() const {
        return ref != default_value;
    }

    T* operator&() { 
        return &ref; 
    }

    operator T() const { 
        return ref; 
    }

};

template <std::ranges::input_range Range, typename Sep = std::string_view>
struct joiner {
    const Range& range;
    Sep sep;
    constexpr joiner(const Range& r, Sep s = ","): range(r), sep(s) {}
};

template <typename Stream, std::ranges::input_range Range, typename Sep>
Stream& operator<<(Stream& s, const joiner<Range, Sep>& j) {
    auto cur = std::begin(j.range), end = std::end(j.range);
    if (cur != end) {
        s << *cur;
        while (++cur != end) {
            s << j.sep << *cur;
        }
    }
    return s;
}

}