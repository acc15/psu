#include <catch2/catch_test_macros.hpp>
#include "psu/dp100.hpp"

using namespace psu::dp100;

TEST_CASE("placeholder") {
    REQUIRE( placeholder() == 1234 );
}
