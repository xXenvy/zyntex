const std = @import("std");
const allocator = std.testing.allocator;

const TranslationUnit = @import("../src/translation_unit.zig");

// Normalize line endings by removing '\r'
fn normalize(input: []const u8, output: []u8) []const u8 {
    const len = std.mem.replace(u8, input, "\r", "", output);
    return output[0..len];
}

test "parsing simple valid code from source produces no errors" {
    var tu = try TranslationUnit.initFromSource("pub fn main() void {}");
    defer tu.deinit();

    try std.testing.expectEqual(tu.errors.len, 0);
    try std.testing.expectEqualStrings(tu.tree.source, "pub fn main() void {}");
    try std.testing.expectEqualStrings(tu.buffer, "pub fn main() void {}");
    try std.testing.expectEqual(tu.tree.tokens.len, 9);
    try std.testing.expectEqual(tu.tree.nodes.len, 5);
}

test "parsing simple invalid code from string produces one error" {
    var tu = try TranslationUnit.initFromSource("pub fn main() void {");
    defer tu.deinit();

    try std.testing.expectEqual(tu.errors.len, 1);
    try std.testing.expectEqualStrings(tu.tree.source, "pub fn main() void {");
    try std.testing.expectEqualStrings(tu.buffer, "pub fn main() void {");
    try std.testing.expectEqual(tu.tree.tokens.len, 8);
    try std.testing.expectEqual(tu.tree.nodes.len, 4);

    const error_report = tu.errors[0];
    try std.testing.expectEqual(error_report.tag_index, 21);
    try std.testing.expectEqual(error_report.is_note, false);
    try std.testing.expectEqual(error_report.token_is_prev, false);
    try std.testing.expectEqual(error_report.token_index, 7);
}

test "parsing simple valid code from file produces no errors" {
    var tu = try TranslationUnit.initFromFile("tests/test_sources/simple.zig");
    defer tu.deinit();

    const expected =
        \\const std = @import("std");
        \\
        \\pub fn main() void {
        \\    std.debug.print("Hello World!", .{});
        \\}
        \\
    ;

    try std.testing.expectEqual(tu.tree.tokens.len, 30);
    try std.testing.expectEqual(tu.tree.nodes.len, 14);

    var buf: [1024]u8 = undefined;
    try std.testing.expectEqualStrings(normalize(tu.tree.source, &buf), normalize(expected, &buf));
    try std.testing.expectEqualStrings(normalize(tu.buffer, &buf), normalize(expected, &buf));

    try std.testing.expectEqual(tu.errors.len, 0);
}

test "parsing large valid code from file produces no errors" {
    var tu = try TranslationUnit.initFromFile("tests/test_sources/large.zig");
    defer tu.deinit();

    try std.testing.expectEqual(tu.tree.tokens.len, 8323);
    try std.testing.expectEqual(tu.tree.nodes.len, 4433);
    try std.testing.expectEqual(tu.errors.len, 0);
    try std.testing.expectEqual(tu.tree.source.len, 69791);
}

test "parsing simple invalid code from file produces two errors" {
    var tu = try TranslationUnit.initFromFile("tests/test_sources/invalid.zig");
    defer tu.deinit();

    const expected =
        \\const std = @import("std")
        \\
        \\pub fn abc() {
        \\
        \\}
    ;

    try std.testing.expectEqual(tu.errors.len, 2);

    var buf: [1024]u8 = undefined;
    try std.testing.expectEqualStrings(normalize(tu.tree.source, &buf), normalize(expected, &buf));
    try std.testing.expectEqualStrings(normalize(tu.buffer, &buf), normalize(expected, &buf));

    try std.testing.expectEqual(tu.tree.tokens.len, 15);
    try std.testing.expectEqual(tu.tree.nodes.len, 7);

    const error_1 = tu.errors[0];
    try std.testing.expectEqual(error_1.tag_index, 42);
    try std.testing.expectEqual(error_1.is_note, false);
    try std.testing.expectEqual(error_1.token_is_prev, true);
    try std.testing.expectEqual(error_1.token_index, 6);

    const error_2 = tu.errors[1];
    try std.testing.expectEqual(error_2.tag_index, 18);
    try std.testing.expectEqual(error_2.is_note, false);
    try std.testing.expectEqual(error_2.token_is_prev, false);
    try std.testing.expectEqual(error_2.token_index, 12);
}
