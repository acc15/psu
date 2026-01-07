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
    using type = std::variant<
        unsigned int,
        float, 
        std::string
    >;

    type value;
};


struct enum_type {
    std::string name;
    typed_value value;
};


using properties = std::unordered_map<std::string, typed_value>;

    

}
