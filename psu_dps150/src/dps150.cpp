#include <iterator>
#include <numeric>
#include <algorithm>
#include <libserialport.h>

#include "sp_utils.hpp"
#include "psu/dps150.hpp"

namespace psu::dps150 {

std::uint8_t compute_checksum(std::uint8_t field, std::uint8_t size, const void* payload) {
    const std::uint8_t* pc = reinterpret_cast<const std::uint8_t*>(payload);
    return field + size + std::accumulate(pc, pc + size, 0);
}

std::uint8_t get_baud_rate_index(std::uint32_t baud_rate) {
    const auto begin = std::begin(baud_rates), end = std::end(baud_rates);
    const auto it = std::lower_bound(begin, end, baud_rate);
    return it != end && *it == baud_rate ? std::distance(begin, it) : 0;
}

std::vector<std::string> find_ports() {
    
    std::vector<std::string> found_ports;

    rs_sp_port_list port_list;
    sp_ok(sp_list_ports(&port_list));

    struct sp_port* port;
    for (std::size_t i = 0; (port = port_list[i]) != nullptr; ++i) {
        enum sp_transport transport = sp_get_port_transport(port);
        if (transport != SP_TRANSPORT_USB) {
            continue;
        }
        int usb_vid, usb_pid;
        sp_ok(sp_get_port_usb_vid_pid(port, &usb_vid, &usb_pid));
        if (usb_vid == VID && usb_pid == PID) {
            found_ports.push_back(sp_get_port_name(port));
        }
    }
    return found_ports;
}

}
