#include "sp_utils.hpp"

#include <format>

namespace psu::dps150 {

sp_error::sp_error(int error_code, const std::string& error_message) noexcept : 
    std::runtime_error(std::format("SP_ERR_FAIL, OS error code: {}, message: {}", error_code, error_message)),
    error_code_(error_code),
    error_message_(error_message)
{
}

int sp_error::error_code() const noexcept {
    return error_code_;
}
const std::string& sp_error::error_message() const noexcept {
    return error_message_;
}

void sp_ok(enum sp_return ret) {
    switch (ret) {
    case SP_OK: break;
    case SP_ERR_ARG: throw std::invalid_argument("SP_ERR_ARG");
    case SP_ERR_FAIL: {
        int error_code = sp_last_error_code();
        char* error_message = sp_last_error_message();
        sp_error err(error_code, error_message);
        sp_free_error_message(error_message);
        throw err;
    }
    case SP_ERR_SUPP: throw std::logic_error("SP_ERR_SUPP");
    case SP_ERR_MEM: throw std::bad_alloc();
    default: throw std::logic_error("SP_ERR_UNKNOWN");
    }
}

}
