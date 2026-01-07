#pragma once

#include <string>

namespace psu {


struct port {
    std::string type;
    std::string description;
    std::string name;

    /**
     * Custom port data for faster connection to device
     */
    void* data;
};

}