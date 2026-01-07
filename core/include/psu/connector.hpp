#pragma once

#include <string>
#include <vector>
#include <memory>

#include "type.hpp"
#include "port.hpp"


namespace psu {

class connector {
public:

    virtual std::string name() = 0;

    /**
     * Lists all device ports
     */
    virtual std::vector<port> list_ports() = 0;

    /**
     * Additional connector-specific properties to connect
     */
    virtual const props_def& properties() = 0;

    /**
     * Connects to device (opens port and)
     */
    virtual std::unique_ptr<connector> connect(const port& descriptor, const props& props) = 0;

};

}