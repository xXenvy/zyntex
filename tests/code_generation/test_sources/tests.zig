const std = @import("std");

test "Empty test" {}

test "assert example" {
    std.testing.assert(2 + 2 == 4);
}