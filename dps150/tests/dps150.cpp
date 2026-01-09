#include <catch2/catch_test_macros.hpp>
#include "psu/dps150/dps150.hpp"

#include <array>

using namespace psu::dps150;

TEST_CASE("compute_checksum") {
    REQUIRE( compute_checksum(0xff, 0x01, std::to_array<std::uint8_t>({ 0x00 }).data()) == 0x00 );
    REQUIRE( compute_checksum(0xff, 0xff, std::to_array<std::uint8_t, 0xff>({ 0x00 }).data()) == 0xfe );
    REQUIRE( compute_checksum(0xff, 0xff, std::to_array<std::uint8_t, 0xff>({ 0x01, 0x02, 0x03 }).data()) == 0x04 );
}

TEST_CASE("get_baud_rate_index") {
    REQUIRE( get_baud_rate_index(2) == 0 );
    REQUIRE( get_baud_rate_index(9600) == 1 );
    REQUIRE( get_baud_rate_index(19200) == 2 );
    REQUIRE( get_baud_rate_index(38400) == 3 );
    REQUIRE( get_baud_rate_index(57600) == 4 );
    REQUIRE( get_baud_rate_index(115100) == 0 );
    REQUIRE( get_baud_rate_index(115200) == 5 );
    REQUIRE( get_baud_rate_index(256000) == 0 );
}

