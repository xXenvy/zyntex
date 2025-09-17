const std = @import("std");

// Valid: 1 param
fn greet(name: []const u8) void {
    std.debug.print("Hello, {}\n", .{name});
}

// Invalid: 8 parameters (exceeds max)
fn configure_all(a: i32, b: i32, c: i32, d: i32, e: i32, f: i32, g: i32, h: i32) void {
    std.debug.print("Config: {}, {}, {}, {}, {}, {}, {}, {}\n", .{a, b, c, d, e, f, g, h});
}

// Valid: snake_case, 1 param
fn print_number(n: i32) void {
    std.debug.print("Number: {}\n", .{n});
}

// Invalid: name starts with digit (invalid name)
fn _1invalid_name() void {
    std.debug.print("Invalid function name\n", .{});
}
