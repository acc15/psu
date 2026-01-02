#pragma once

#include <libserialport.h>

#include "utils.hpp"

namespace psu {

bool check_sp_error(enum sp_return ret);

using rs_sp_port = resource<struct sp_port*, sp_free_port>;
using rs_sp_port_list = resource<struct sp_port**, sp_free_port_list>;



}