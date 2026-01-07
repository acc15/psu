#pragma once

#include <string>
#include <vector>
#include <memory>

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
     * Connects to device (opens port and)
     */
    virtual std::unique_ptr<connector> connect(const port& descriptor) = 0;

};

}