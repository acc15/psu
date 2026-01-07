#pragma once

#include <string>
#include <vector>
#include <memory>

namespace psu {

struct port {
    std::string type;
    std::string description;
    std::string name;

    /**
     * Custom port data for faster connection to device
     */
    mutable void* data;
};

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

class psu {


    // virtual std::vector<

};

}