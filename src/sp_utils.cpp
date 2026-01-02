#include <iostream>

#include "sp_utils.hpp"

namespace psu {

bool check_sp_error(enum sp_return ret) {
    switch (ret) {
    case SP_OK: return true;

    case SP_ERR_ARG:
        std::clog << "sp_error: Invalid argument" << std::endl;
        break;

    case SP_ERR_FAIL: {
        std::clog << "sp_error: Invalid argument" << std::endl;
        /* When SP_ERR_FAIL is returned, there was an error from the OS,
         * which we can obtain the error code and message for. These
         * calls must be made in the same thread as the call that
         * returned SP_ERR_FAIL, and before any other system functions
         * are called in that thread, or they may not return the
         * correct results. */
        int error_code = sp_last_error_code();
        char* error_message = sp_last_error_message();
        std::clog << "sp_error: Failed, OS error code: " << error_code << ", message: '" << error_message << "'" << std::endl;
        sp_free_error_message(error_message);
    }

    case SP_ERR_SUPP:
        /* When SP_ERR_SUPP is returned, the function was asked to do
         * something that isn't supported by the current OS or device,
         * or that libserialport doesn't know how to do in the current
         * version. */
        std::clog << "sp_error: Not supported" << std::endl;
        break;

    case SP_ERR_MEM:
        /* When SP_ERR_MEM is returned, libserialport wasn't able to
         * allocate some memory it needed. Since the library doesn't
         * normally use any large data structures, this probably means
         * the system is critically low on memory and recovery will
         * require very careful handling. The library itself will
         * always try to handle any allocation failure safely.
         *
         * In this example, we'll just try to exit gracefully without
         * calling printf, which might need to allocate further memory. */
        std::clog << "sp_error: Not enough memory" << std::endl;
        break;
    }
    return false;
}

}
