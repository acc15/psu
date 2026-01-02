#include <iostream>
#include <vector>
#include <string>
#include <libserialport.h>

#include "dps150.hpp"
#include "utils.hpp"
#include "sp_utils.hpp"


int main() {
    const char* port_name = "/dev/ttyUSB0";
    const std::vector<std::string> found_port_names = psu::dps150::find_ports();
    if (found_port_names.empty()) {
        std::clog << "can't find DPS-150 port" << std::endl;
        return -1;
    }

    std::cout << "found ports: " << psu::joiner(found_port_names) << std::endl;

    psu::rs_sp_port port;
    if (!psu::check_sp_error(sp_get_port_by_name(found_port_names.front().c_str(), &port))) {
        return -1;
    }

    if (!psu::check_sp_error(sp_open(port, sp_mode::SP_MODE_READ_WRITE))) {
        return -1;
    }

    return 0;
}