#pragma once

#include <libserialport.h>
#include <string>

#include "psu/utils.hpp"

namespace psu {

class sp_error: public std::runtime_error {
    int error_code_;
    std::string error_message_;
public:
    sp_error(int error_code, const std::string& error_message) noexcept;
    int error_code() const noexcept;
    const std::string& error_message() const noexcept;
};

void sp_ok(enum sp_return ret);

using rs_sp_port = resource<struct sp_port*, sp_free_port>;
using rs_sp_port_list = resource<struct sp_port**, sp_free_port_list>;



}