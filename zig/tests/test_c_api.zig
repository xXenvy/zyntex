const std = @import("std");

const c_api = @import("../src/c_api.zig");
const structs = @import("../src/structs.zig");
const normalize = @import("helpers.zig").normalize;
const TranslationUnit = @import("../src/translation_unit.zig");

const ErrorReport = structs.ErrorReport;
const ASTToken = structs.ASTToken;
const ASTNode = structs.ASTNode;
const allocator = std.testing.allocator;

test "parser generic slice roundtrip" {
    const Item = struct {
        a: u16,
        b: u32,
    };
    var arr: [3]Item = .{
        Item{ .a = 0x0102, .b = 10 },
        Item{ .a = 0x0304, .b = 20 },
        Item{ .a = 0x0506, .b = 30 },
    };
    const generic_slice = c_api.makeSlice(Item, arr[0..].ptr, arr.len);
    const many_ptr: [*]const Item = @ptrCast(@alignCast(generic_slice.ptr));

    for (0..arr.len) |i| {
        const p_i: *const Item = @ptrCast(many_ptr + i);
        try std.testing.expect(p_i == &arr[i]);
    }

    const slice = c_api.toSlice(Item, generic_slice);
    try std.testing.expectEqual(arr.len, slice.len);
    for (0..arr.len) |i| {
        try std.testing.expectEqual(arr[i].a, slice[i].a);
        try std.testing.expectEqual(arr[i].b, slice[i].b);
    }
}

test "parser parses simple source file correctly" {
    const tu: *TranslationUnit = c_api.createTranslationUnit("tests/test_sources/simple.zig").?;
    defer c_api.freeTranslationUnit(tu);

    const expected =
        \\const std = @import("std");
        \\
        \\pub fn main() void {
        \\    std.debug.print("Hello World!", .{});
        \\}
        \\
    ;

    var buf: [1024]u8 = undefined;
    const source: []const u8 = normalize(c_api.toSlice(u8, c_api.getTranslationUnitSource(tu)), &buf);

    try std.testing.expectEqual(c_api.getTranslationUnitTokensCount(tu), 30);
    try std.testing.expectEqual(c_api.getTranslationUnitNodesCount(tu), 14);
    try std.testing.expectEqualStrings(source, normalize(expected, &buf));
    try std.testing.expectEqual(c_api.getTranslationUnitErrorsCount(tu), 0);
}

test "parser parses simple source file with errors" {
    const tu: *TranslationUnit = c_api.createTranslationUnit("tests/test_sources/invalid.zig").?;
    defer c_api.freeTranslationUnit(tu);

    const expected =
        \\const std = @import("std")
        \\
        \\pub fn abc() {
        \\
        \\}
    ;

    var buf: [1024]u8 = undefined;
    const source: []const u8 = normalize(c_api.toSlice(u8, c_api.getTranslationUnitSource(tu)), &buf);

    try std.testing.expectEqualStrings(source, normalize(expected, &buf));
    try std.testing.expectEqual(c_api.getTranslationUnitTokensCount(tu), 15);
    try std.testing.expectEqual(c_api.getTranslationUnitNodesCount(tu), 7);
    try std.testing.expectEqual(c_api.getTranslationUnitErrorsCount(tu), 2);

    const errors: []const ErrorReport = c_api.toSlice(ErrorReport, c_api.getTranslationUnitErrors(tu));
    const error_1 = errors[0];
    const error_2 = errors[1];

    try std.testing.expectEqual(error_1.tag_index, 42);
    try std.testing.expectEqual(error_1.is_note, false);
    try std.testing.expectEqual(error_1.token_is_prev, true);
    try std.testing.expectEqual(error_1.token_index, 6);

    try std.testing.expectEqual(error_2.tag_index, 18);
    try std.testing.expectEqual(error_2.is_note, false);
    try std.testing.expectEqual(error_2.token_is_prev, false);
    try std.testing.expectEqual(error_2.token_index, 12);
}

test "parser parses large source file correctly" {
    const tu: *TranslationUnit = c_api.createTranslationUnit("tests/test_sources/large.zig").?;
    defer c_api.freeTranslationUnit(tu);

    try std.testing.expectEqual(c_api.getTranslationUnitTokensCount(tu), 8323);
    try std.testing.expectEqual(c_api.getTranslationUnitNodesCount(tu), 4433);
    try std.testing.expectEqual(c_api.getTranslationUnitErrorsCount(tu), 0);
}

test "parser parses simple code correctly" {
    const tu = c_api.createTranslationUnitFromSource("pub fn main() void {}").?;
    defer c_api.freeTranslationUnit(tu);
    const expected = "pub fn main() void {}";
    const source: []const u8 = c_api.toSlice(u8, c_api.getTranslationUnitSource(tu));
    const nodes = c_api.toSlice(ASTNode, c_api.getTranslationUnitNodes(tu));

    const fn_node: ASTNode = nodes[1];
    const fn_return_type_node: ASTNode = c_api.getNodeType(tu, fn_node);

    try std.testing.expectEqual(true, c_api.isNodePublic(tu, fn_node));
    try std.testing.expectEqual(false, c_api.isNodeConst(tu, fn_node));
    try std.testing.expectEqual(false, c_api.isNodeContainer(fn_node));
    try std.testing.expectEqualStrings("main", c_api.toSlice(u8, c_api.getNodeSpelling(tu, fn_node)));
    try std.testing.expectEqualStrings("void", c_api.toSlice(u8, c_api.getNodeSpelling(tu, fn_return_type_node)));

    try std.testing.expectEqual(c_api.getTranslationUnitTokensCount(tu), 9);
    try std.testing.expectEqual(c_api.getTranslationUnitNodesCount(tu), 5);
    try std.testing.expectEqualStrings(source, expected);
    try std.testing.expectEqual(c_api.getTranslationUnitErrorsCount(tu), 0);
}

test "parser parses simple nodes correctly" {
    const tu = c_api.createTranslationUnitFromSource(
        \\pub fn testFunc() void {}
        \\test "testname" {}
        \\const var_name: u32 = 15;
        \\pub const structName = struct {};
    ).?;
    defer c_api.freeTranslationUnit(tu);

    const nodes: []const ASTNode = c_api.toSlice(ASTNode, c_api.getTranslationUnitNodes(tu));
    const fn_proto_spelling: []const u8 = c_api.toSlice(u8, c_api.getNodeSpelling(tu, nodes[1]));
    const test_decl_spelling: []const u8 = c_api.toSlice(u8, c_api.getNodeSpelling(tu, nodes[6]));
    const var_decl_spelling: []const u8 = c_api.toSlice(u8, c_api.getNodeSpelling(tu, nodes[8]));
    const var_struct_decl_spelling: []const u8 = c_api.toSlice(u8, c_api.getNodeSpelling(tu, nodes[10]));

    try std.testing.expectEqual(true, c_api.isNodePublic(tu, nodes[1]));
    try std.testing.expectEqual(false, c_api.isNodePublic(tu, nodes[6]));
    try std.testing.expectEqual(false, c_api.isNodePublic(tu, nodes[8]));
    try std.testing.expectEqual(true, c_api.isNodePublic(tu, nodes[10]));

    try std.testing.expectEqual(false, c_api.isNodeConst(tu, nodes[1]));
    try std.testing.expectEqual(false, c_api.isNodeConst(tu, nodes[6]));
    try std.testing.expectEqual(true, c_api.isNodeConst(tu, nodes[8]));
    try std.testing.expectEqual(true, c_api.isNodeConst(tu, nodes[10]));

    try std.testing.expectEqual(false, c_api.isNodeContainer(nodes[1]));
    try std.testing.expectEqual(false, c_api.isNodeContainer(nodes[6]));
    try std.testing.expectEqual(false, c_api.isNodeContainer(nodes[8]));
    try std.testing.expectEqual(false, c_api.isNodeContainer(nodes[10]));
    try std.testing.expectEqual(true, c_api.isNodeContainer(nodes[11]));
    try std.testing.expectEqual(true, c_api.isNodeStruct(tu, nodes[11]));

    try std.testing.expectEqualStrings("testFunc", fn_proto_spelling);
    try std.testing.expectEqualStrings("\"testname\"", test_decl_spelling);
    try std.testing.expectEqualStrings("var_name", var_decl_spelling);
    try std.testing.expectEqualStrings("structName", var_struct_decl_spelling);
}

test "parser parses root nodes correctly" {
    const tu = c_api.createTranslationUnitFromSource(
        \\pub fn testFunc() usize {
        \\  const a: usize = 15;
        \\  return a;
        \\}
        \\pub const ABC = false;
    ).?;
    defer c_api.freeTranslationUnit(tu);
    const indexes: []const u32 = c_api.toSlice(u32, c_api.getTranslationUnitRootNodes(tu));
    try std.testing.expectEqual(indexes.len, 2);

    const func_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[0]);
    const var_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[1]);

    try std.testing.expectEqual(0, c_api.getNodeParamsCount(tu, func_node));
    try std.testing.expectEqual(0, c_api.getNodeParamsCount(tu, var_node));

    try std.testing.expectEqual(true, c_api.isNodePublic(tu, func_node));
    try std.testing.expectEqual(true, c_api.isNodePublic(tu, var_node));

    try std.testing.expectEqual(false, c_api.isNodeConst(tu, func_node));
    try std.testing.expectEqual(true, c_api.isNodeConst(tu, var_node));

    try std.testing.expectEqual(false, c_api.isNodeContainer(func_node));
    try std.testing.expectEqual(false, c_api.isNodeContainer(var_node));

    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_node)), "testFunc");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, var_node)), "ABC");
}

test "parser parses function params correctly" {
    const tu = c_api.createTranslationUnitFromSource(
        \\pub fn testFunc(a: usize, b: usize) usize {
        \\  return a + b;
        \\}
    ).?;
    defer c_api.freeTranslationUnit(tu);
    const indexes: []const u32 = c_api.toSlice(u32, c_api.getTranslationUnitRootNodes(tu));
    try std.testing.expectEqual(indexes.len, 1);

    const func_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[0]);
    const func_return_type_node: ASTNode = c_api.getNodeType(tu, func_node);

    try std.testing.expectEqual(true, c_api.isNodePublic(tu, func_node));
    try std.testing.expectEqual(false, c_api.isNodeConst(tu, func_node));
    try std.testing.expectEqual(false, c_api.isNodeContainer(func_node));
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_node)), "testFunc");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_return_type_node)), "usize");
    try std.testing.expectEqual(2, c_api.getNodeParamsCount(tu, func_node));

    var params: [2]c_api.NodeParam = undefined;
    const got = c_api.getNodeParams(tu, func_node, @ptrCast(&params[0]), params.len);
    try std.testing.expectEqual(2, got);

    try std.testing.expectEqualStrings(c_api.toSlice(u8, params[0].name), "a");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, params[1].name), "b");

    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, params[0].type)), "usize");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, params[1].type)), "usize");
}

test "parser parses node types correctly" {
    const tu = c_api.createTranslationUnitFromSource(
        \\fn testFunc() usize {
        \\  return 1;
        \\}
        \\var abc: i64 = 10;
        \\var abc2 = 1;
        \\const var_align: u32 align(8) = 100;
    ).?;
    defer c_api.freeTranslationUnit(tu);
    const indexes: []const u32 = c_api.toSlice(u32, c_api.getTranslationUnitRootNodes(tu));
    try std.testing.expectEqual(indexes.len, 4);

    const func_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[0]);
    const func_type_node: ASTNode = c_api.getNodeType(tu, func_node);

    const variable1_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[1]);
    const variable1_type_node: ASTNode = c_api.getNodeType(tu, variable1_node);

    const variable2_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[2]);
    const variable2_type_node: ASTNode = c_api.getNodeType(tu, variable2_node);

    const variable_align_node: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[3]);
    const variable_align_type_node: ASTNode = c_api.getNodeType(tu, variable_align_node);

    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_type_node)), "usize");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, variable1_type_node)), "i64");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeAlign(tu, variable_align_node)), "8");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, variable_align_type_node)), "u32");
    try std.testing.expectEqual(c_api.getNodeType(tu, variable2_type_node).index, variable2_node.index);
}

test "parser parses externs correctly" {
    const tu = c_api.createTranslationUnitFromSource(
        \\pub extern fn public_testing(a: usize) void;
        \\extern fn private_testing() usize;
    ).?;
    defer c_api.freeTranslationUnit(tu);
    const indexes: []const u32 = c_api.toSlice(u32, c_api.getTranslationUnitRootNodes(tu));
    try std.testing.expectEqual(indexes.len, 2);

    const func_node_1: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[0]);
    const func_return_type_node_1: ASTNode = c_api.getNodeType(tu, func_node_1);

    const func_node_2: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[1]);
    const func_return_type_node_2: ASTNode = c_api.getNodeType(tu, func_node_2);

    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_return_type_node_1)), "void");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_return_type_node_2)), "usize");

    try std.testing.expectEqual(c_api.isNodePublic(tu, func_node_1), true);
    try std.testing.expectEqual(c_api.isNodePublic(tu, func_node_2), false);

    try std.testing.expectEqual(c_api.isNodeExtern(tu, func_node_1), true);
    try std.testing.expectEqual(c_api.isNodeExtern(tu, func_node_2), true);

    try std.testing.expectEqual(c_api.isNodeExport(tu, func_node_1), false);
    try std.testing.expectEqual(c_api.isNodeExport(tu, func_node_2), false);

    try std.testing.expectEqual(c_api.getNodeParamsCount(tu, func_node_1), 1);
    try std.testing.expectEqual(c_api.getNodeParamsCount(tu, func_node_2), 0);
}

test "parser parses exports correctly" {
    const tu = c_api.createTranslationUnitFromSource(
        \\pub export fn public_testing(a: usize) void {}
        \\export fn private_testing() usize {}
    ).?;
    // todo: add similar tests but use variables instead.
    defer c_api.freeTranslationUnit(tu);
    const indexes: []const u32 = c_api.toSlice(u32, c_api.getTranslationUnitRootNodes(tu));
    try std.testing.expectEqual(indexes.len, 2);

    const func_node_1: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[0]);
    const func_return_type_node_1: ASTNode = c_api.getNodeType(tu, func_node_1);

    const func_node_2: ASTNode = c_api.getTranslationUnitNodeFromIndex(tu, indexes[1]);
    const func_return_type_node_2: ASTNode = c_api.getNodeType(tu, func_node_2);

    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_return_type_node_1)), "void");
    try std.testing.expectEqualStrings(c_api.toSlice(u8, c_api.getNodeSpelling(tu, func_return_type_node_2)), "usize");

    try std.testing.expectEqual(c_api.isNodePublic(tu, func_node_1), true);
    try std.testing.expectEqual(c_api.isNodePublic(tu, func_node_2), false);

    try std.testing.expectEqual(c_api.isNodeExtern(tu, func_node_1), false);
    try std.testing.expectEqual(c_api.isNodeExtern(tu, func_node_2), false);

    try std.testing.expectEqual(c_api.isNodeExport(tu, func_node_1), true);
    try std.testing.expectEqual(c_api.isNodeExport(tu, func_node_2), true);

    try std.testing.expectEqual(c_api.getNodeParamsCount(tu, func_node_1), 1);
    try std.testing.expectEqual(c_api.getNodeParamsCount(tu, func_node_2), 0);
}
