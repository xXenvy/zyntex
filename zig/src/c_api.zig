const std = @import("std");
const structs = @import("structs.zig");
const TranslationUnit = @import("translation_unit.zig");

const allocator = std.heap.page_allocator;
const Ast = std.zig.Ast;
const Tag = Ast.Node.Tag;

pub const ErrorReport = structs.ErrorReport;
pub const ASTNode = structs.ASTNode;
pub const ASTToken = structs.ASTToken;
pub const NodeParam = structs.NodeParam;

// A generic slice struct used for FFI-compatible data transfer.
pub const GenericSlice = extern struct {
    ptr: ?*const anyopaque,
    len: usize,
};

// Converts a typed pointer and length into a GenericSlice for FFI.
pub fn makeSlice(comptime T: type, ptr: [*]const T, len: usize) GenericSlice {
    return .{
        .ptr = @ptrCast(ptr),
        .len = len,
    };
}

// Converts a GenericSlice back to a typed Zig slice.
// Assumes the pointer is properly aligned for type T.
pub fn toSlice(comptime T: type, gs: GenericSlice) []const T {
    const T_temp: [*]const T = @ptrCast(@alignCast(gs.ptr));
    return T_temp[0..gs.len];
}

pub export fn createTranslationUnit(file_path: [*:0]const u8) callconv(.C) ?*TranslationUnit {
    const unit_ptr = allocator.create(TranslationUnit) catch return null;
    unit_ptr.* = TranslationUnit.initFromFile(file_path) catch return null;
    return unit_ptr;
}

pub export fn createTranslationUnitFromSource(source: [*:0]const u8) callconv(.C) ?*TranslationUnit {
    const unit_ptr = allocator.create(TranslationUnit) catch return null;
    unit_ptr.* = TranslationUnit.initFromSource(source) catch return null;
    return unit_ptr;
}

pub export fn getTranslationUnitNodesCount(unit: *TranslationUnit) callconv(.C) usize {
    return unit.nodes.len;
}

pub export fn getTranslationUnitNodes(unit: *TranslationUnit) callconv(.C) GenericSlice {
    return makeSlice(ASTNode, unit.nodes.ptr, unit.nodes.len);
}

pub export fn getTranslationUnitRootNodes(unit: *TranslationUnit) callconv(.C) GenericSlice {
    const indexes = unit.tree.rootDecls();
    return makeSlice(u32, indexes.ptr, indexes.len);
}

pub export fn getTranslationUnitNodeFromIndex(unit: *TranslationUnit, index: u32) callconv(.C) ASTNode {
    return unit.nodes[index];
}

pub export fn getTranslationUnitTokensCount(unit: *TranslationUnit) callconv(.C) usize {
    return unit.tokens.len;
}

pub export fn getTranslationUnitTokens(unit: *TranslationUnit) callconv(.C) GenericSlice {
    return makeSlice(ASTToken, unit.tokens.ptr, unit.tokens.len);
}

pub export fn getTranslationUnitErrorsCount(unit: *TranslationUnit) callconv(.C) usize {
    return unit.errors.len;
}

pub export fn getTranslationUnitErrors(unit: *TranslationUnit) callconv(.C) GenericSlice {
    return makeSlice(ErrorReport, unit.errors.ptr, unit.errors.len);
}

pub export fn getTranslationUnitSource(unit: *TranslationUnit) callconv(.C) GenericSlice {
    return makeSlice(u8, unit.tree.source.ptr, unit.tree.source.len);
}

pub export fn freeTranslationUnit(unit: *TranslationUnit) callconv(.C) void {
    unit.deinit();
    allocator.destroy(unit);
}

pub export fn getNodeSpelling(unit: *TranslationUnit, node: ASTNode) callconv(.C) GenericSlice {
    const tag: Tag = @enumFromInt(node.tag_index);
    const token_index = switch (tag) {
        .fn_proto_simple,
        .fn_proto_multi,
        .fn_proto_one,
        .fn_proto,
        .fn_decl,
        .global_var_decl,
        .local_var_decl,
        .simple_var_decl,
        .aligned_var_decl,
        => node.main_token + 1,

        .test_decl,
        .call_one,
        .call_one_comma,
        .async_call_one,
        .async_call_one_comma,
        .call,
        .call_comma,
        .async_call,
        .async_call_comma,
        => node.lhs,
        else => node.main_token,
    };
    const spelling = unit.tree.tokenSlice(token_index);
    return makeSlice(u8, spelling.ptr, spelling.len);
}

pub export fn getNodeSource(unit: *TranslationUnit, node_index: u32) callconv(.C) GenericSlice {
    const source: []const u8 = unit.tree.getNodeSource(node_index);
    return makeSlice(u8, source.ptr, source.len);
}

pub export fn getNodeType(unit: *TranslationUnit, node: ASTNode) callconv(.C) ASTNode {
    const tag: Tag = @enumFromInt(node.tag_index);
    switch (tag) {
        .simple_var_decl,
        => {
            if (node.lhs == 0) return node;
            return getTranslationUnitNodeFromIndex(unit, node.lhs);
        },
        .local_var_decl,
        .global_var_decl,
        => {
            const extra = unit.tree.extraData(node.lhs, Ast.Node.LocalVarDecl);
            return getTranslationUnitNodeFromIndex(unit, extra.type_node);
        },
        .fn_proto,
        .fn_proto_one,
        .fn_proto_multi,
        .fn_proto_simple,
        => return getTranslationUnitNodeFromIndex(unit, node.rhs),
        .fn_decl => {
            const fn_proto = unit.tree.nodes.items(.data)[node.lhs];
            return getTranslationUnitNodeFromIndex(unit, fn_proto.rhs);
        },
        else => return node,
    }
}

pub export fn getNodeAlign(unit: *TranslationUnit, node: ASTNode) callconv(.C) GenericSlice {
    const tag: Tag = @enumFromInt(node.tag_index);
    switch (tag) {
        .local_var_decl, .global_var_decl => {
            const extra = unit.tree.extraData(node.lhs, Ast.Node.LocalVarDecl);
            return getNodeSource(unit, extra.align_node);
        },
        else => return .{ .ptr = null, .len = 0 },
    }
}

pub export fn getNodeBody(unit: *TranslationUnit, node: ASTNode) callconv(.C) GenericSlice {
    const tag: Tag = @enumFromInt(node.tag_index);
    switch (tag) {
        .fn_decl => {
            return getNodeSource(unit, node.rhs);
        },
        else => return .{ .ptr = null, .len = 0 },
    }
}

pub export fn getNodeParamsCount(unit: *TranslationUnit, node: ASTNode) callconv(.C) usize {
    var buffer: [1]Ast.Node.Index = undefined;
    const full_fn_proto = unit.tree.fullFnProto(&buffer, node.index) orelse return 0;
    return full_fn_proto.ast.params.len;
}

pub export fn getNodeParams(
    unit: *TranslationUnit,
    node: ASTNode,
    out: [*]NodeParam,
    capacity: usize,
) callconv(.C) usize {
    var buffer: [1]Ast.Node.Index = undefined;
    const full_fn_proto = unit.tree.fullFnProto(&buffer, node.index) orelse return 0;

    var i: usize = 0;
    for (full_fn_proto.ast.params) |param_index| {
        if (i >= capacity) break;
        const param_node = getTranslationUnitNodeFromIndex(unit, param_index);
        const param_name = unit.tree.tokenSlice(param_node.main_token - 2);

        out[i] = .{
            .name = makeSlice(u8, param_name.ptr, param_name.len),
            .type = param_node,
        };
        i += 1;
    }
    return i;
}

pub export fn isNodeExtern(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    const tag: Tag = @enumFromInt(node.tag_index);
    const token = switch (tag) {
        .root => return false,
        .fn_proto_simple,
        .fn_proto_multi,
        .fn_proto_one,
        .fn_proto,
        .fn_decl,
        .global_var_decl,
        .local_var_decl,
        .simple_var_decl,
        .aligned_var_decl,
        => if (node.main_token > 0) node.main_token - 1 else node.main_token,
        else => node.main_token,
    };
    return std.mem.eql(u8, unit.tree.tokenSlice(token), "extern");
}

pub export fn isNodeExport(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    const tag: Tag = @enumFromInt(node.tag_index);
    const token = switch (tag) {
        .root => return false,
        .fn_proto_simple,
        .fn_proto_multi,
        .fn_proto_one,
        .fn_proto,
        .fn_decl,
        .global_var_decl,
        .local_var_decl,
        .simple_var_decl,
        .aligned_var_decl,
        => if (node.main_token > 0) node.main_token - 1 else node.main_token,
        else => node.main_token,
    };
    return std.mem.eql(u8, unit.tree.tokenSlice(token), "export");
}

pub export fn isNodePublic(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    const tag: Tag = @enumFromInt(node.tag_index);
    var token: u32 = node.main_token;

    switch (tag) {
        .root => return false,
        .fn_proto_simple,
        .fn_proto_multi,
        .fn_proto_one,
        .fn_proto,
        .fn_decl,
        .global_var_decl,
        .local_var_decl,
        .simple_var_decl,
        .aligned_var_decl,
        => {
            if (isNodeExport(unit, node) or isNodeExtern(unit, node)) {
                if (token > 1) token -= 2;
            } else if (token > 0) token -= 1;
        },
        else => {},
    }
    return std.mem.eql(u8, unit.tree.tokenSlice(token), "pub");
}

pub export fn isNodeConst(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    const tag: Tag = @enumFromInt(node.tag_index);
    const token_index = switch (tag) {
        .identifier => if (node.main_token > 0) node.main_token - 1 else node.main_token,
        else => node.main_token,
    };
    return std.mem.eql(u8, unit.tree.tokenSlice(token_index), "const");
}

pub export fn isNodeContainer(node: ASTNode) callconv(.C) bool {
    const tag: Tag = @enumFromInt(node.tag_index);
    return switch (tag) {
        .container_decl,
        .container_decl_trailing,
        .container_decl_two,
        .container_decl_two_trailing,
        => true,
        else => false,
    };
}

pub export fn isNodeStruct(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "struct");
}

pub export fn isNodeUnion(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "union");
}

pub export fn isNodeOpaque(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "opaque");
}

pub export fn isNodeEnum(unit: *TranslationUnit, node: ASTNode) callconv(.C) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "enum");
}
