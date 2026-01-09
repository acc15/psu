#pragma once

#include <variant>
#include <string>
#include <vector>
#include <utility>
#include <unordered_map>

namespace psu::core {

enum class type {
    UINT,
    FLOAT,
    STRING
};

using type_value = std::variant<
    unsigned int,
    float,
    std::string
>;

using props = std::unordered_map<std::string, type_value>;

template <typename T>
using range_def = std::pair<T, T>;

using enum_descriptor = std::vector<std::pair<std::string, type_value>>;
using type_descriptor = std::variant<type, enum_descriptor, range_def<unsigned int>, range_def<float>>;
using props_descriptor = std::vector<std::pair<std::string, type_descriptor>>;
using props_value = std::vector<std::tuple<std::string, type_descriptor, type_value>>;

}
