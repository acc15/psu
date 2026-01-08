#pragma once

#include <variant>
#include <string>
#include <vector>
#include <utility>
#include <unordered_map>

namespace psu {

enum class type {
    UINT,
    FLOAT,
    STRING
};

using typed_value = std::variant<
    unsigned int,
    float, 
    std::string
>;

using props = std::unordered_map<std::string, typed_value>;
template <typename T>
using range_def = std::pair<T, T>;
using enum_def = std::vector<std::pair<std::string, typed_value>>;
using type_def = std::variant<type, enum_def, range_def<unsigned int>, range_def<float>>;
using props_def = std::vector<std::pair<std::string, type_def>>;

}
