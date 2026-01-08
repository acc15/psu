#pragma once

#include <string_view>
#include <vector>
#include <functional>
#include <utility>
#include <string>
#include <memory>

#include "type.hpp"
#include "psu.hpp"


namespace psu {

class connector {
public:

    virtual std::string_view name() = 0;

    /**
     * Lists all device ports
     */
    virtual std::vector<std::pair<std::string, std::string>> list_ports() = 0;

    /**
     * Additional connector-specific properties. Examples of such properties are:
     *
     * * USB CDC Serial baud rate
     * * Device identifier which is checked after connection (to reject wrong connections, if psu has support for this)
     * * Check internal device serial number (not USB serial number)
     * * Polling frequency (or delay) - How frequently connector will query main data from device
     */
    virtual const props_descriptor& properties() = 0;

    /**
     * Connects to device (opens port, ensures that protocol is ok, its correct device)
     */
    virtual void connect(
        const std::string& path, 
        const props& props, 
        const std::function<void(std::unique_ptr<psu>, std::exception_ptr)&>
    ) = 0;

};

}