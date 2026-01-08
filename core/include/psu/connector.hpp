#pragma once

#include <string_view>
#include <vector>
#include <memory>

#include "type.hpp"
#include "port.hpp"


namespace psu {

class connector {
public:

    virtual std::string_view name() = 0;

    /**
     * Lists all device ports
     */
    virtual std::vector<port> list_ports() = 0;

    /**
     * Additional connector-specific properties. Examples of such properties are:
     *
     * * USB CDC baud rate
     * * Device identifier which is checked after connection
     * * Internal device serial number (not USB serial number)
     * * Polling frequency (or delay) - How frequently connector will query main data from device
     */
    virtual const props_def& properties() = 0;

    /**
     * Connects to device (opens port and)
     */
    virtual std::unique_ptr<connector> connect(const port& port, const props& props) = 0;

};

}