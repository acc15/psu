#pragma once

#include <variant>
#include <string>
#include <unordered_map>

namespace psu {

enum class type {
    UINT,
    FLOAT,
    STRING
};

struct typed_value {
    using variant = std::variant<
        unsigned int,
        float, 
        std::string
    >;

    variant value;

    type type() const {
        return static_cast<enum type>(value.index());
    }
};

using properties = std::unordered_map<std::string, typed_value>;

}
