const std = @import("std");
const builtin = @import("builtin");
const structs = @import("structs.zig");
const TranslationUnit = @import("translation_unit.zig");

const backing_allocator = if (builtin.is_test) std.testing.allocator else std.heap.smp_allocator;
const Ast = std.zig.Ast;
const Tag = Ast.Node.Tag;

pub const ErrorReport = structs.ErrorReport;
pub const NodeParam = structs.NodeParam;
pub const ASTToken = structs.ASTToken;
pub const ASTNode = structs.ASTNode;

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

pub export fn createTranslationUnit(file_path: [*:0]const u8) callconv(.c) ?*TranslationUnit {
    const unit_ptr = backing_allocator.create(TranslationUnit) catch return null;
    unit_ptr.* = TranslationUnit.initFromFile(backing_allocator, std.mem.span(file_path)) catch {
        backing_allocator.destroy(unit_ptr);
        return null;
    };
    return unit_ptr;
}

pub export fn createTranslationUnitFromSource(source: [*:0]const u8) callconv(.c) ?*TranslationUnit {
    const unit_ptr = backing_allocator.create(TranslationUnit) catch return null;
    unit_ptr.* = TranslationUnit.initFromSource(backing_allocator, std.mem.span(source)) catch {
        backing_allocator.destroy(unit_ptr);
        return null;
    };
    return unit_ptr;
}

pub export fn getTranslationUnitNodesCount(unit: *TranslationUnit) callconv(.c) usize {
    return unit.tree.nodes.len;
}

pub export fn getTranslationUnitNodes(unit: *TranslationUnit) callconv(.c) GenericSlice {
    return makeSlice(ASTNode, unit.nodes.ptr, unit.nodes.len);
}

pub export fn getTranslationUnitRootNodes(unit: *TranslationUnit) callconv(.c) GenericSlice {
    const indexes = unit.tree.rootDecls();
    return makeSlice(Ast.Node.Index, indexes.ptr, indexes.len);
}

pub export fn getTranslationUnitNodeFromIndex(unit: *TranslationUnit, index: u32) callconv(.c) ASTNode {
    return unit.nodes[index];
}

pub export fn getTranslationUnitTokensCount(unit: *TranslationUnit) callconv(.c) usize {
    return unit.tokens.len;
}

pub export fn getTranslationUnitTokens(unit: *TranslationUnit) callconv(.c) GenericSlice {
    return makeSlice(ASTToken, unit.tokens.ptr, unit.tokens.len);
}

pub export fn getTranslationUnitErrorsCount(unit: *TranslationUnit) callconv(.c) usize {
    return unit.errors.len;
}

pub export fn getTranslationUnitErrors(unit: *TranslationUnit) callconv(.c) GenericSlice {
    return makeSlice(ErrorReport, unit.errors.ptr, unit.errors.len);
}

pub export fn getTranslationUnitSource(unit: *TranslationUnit) callconv(.c) GenericSlice {
    return makeSlice(u8, unit.tree.source.ptr, unit.tree.source.len);
}

pub export fn freeTranslationUnit(unit: *TranslationUnit) callconv(.c) void {
    unit.deinit();
    backing_allocator.destroy(unit);
}

pub export fn getNodeSpelling(unit: *TranslationUnit, node: ASTNode) callconv(.c) GenericSlice {
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
    var token_index = node.main_token;

    switch (tag) {
        .fn_proto_simple,
        .fn_proto_multi,
        .fn_proto_one,
        .fn_proto,
        .fn_decl,
        .global_var_decl,
        .local_var_decl,
        .simple_var_decl,
        .aligned_var_decl,
        => token_index += 1,

        .test_decl => {
            const node_data = unit.tree.nodeData(@fromBackingInt(node.index));
            if (node_data.opt_token_and_node[0].unwrap()) |position| {
                token_index = position;
            }
        },
        else => {},
    }
    const spelling = unit.tree.tokenSlice(token_index);
    return makeSlice(u8, spelling.ptr, spelling.len);
}

pub export fn getNodeSource(unit: *TranslationUnit, node_index: u32) callconv(.c) GenericSlice {
    const source: []const u8 = unit.tree.getNodeSource(@fromBackingInt(node_index));
    return makeSlice(u8, source.ptr, source.len);
}

pub export fn getNodeType(unit: *TranslationUnit, node: ASTNode) callconv(.c) GenericSlice {
    const missing: GenericSlice = .{ .ptr = null, .len = 0 };
    const index: Ast.Node.Index = @fromBackingInt(node.index);

    if (unit.tree.fullVarDecl(index)) |decl| {
        const type_node = decl.ast.type_node.unwrap() orelse return missing;
        return getNodeSource(unit, @backingInt(type_node));
    }

    var buffer: [1]Ast.Node.Index = undefined;
    if (unit.tree.fullFnProto(&buffer, index)) |proto| {
        const return_type = proto.ast.return_type.unwrap() orelse return missing;
        const first = unit.tree.firstToken(return_type);
        const source = unit.tree.getNodeSource(return_type);

        // Zig stores an inferred error set's ! before the return expression.
        if (first > 0 and unit.tree.tokenTag(first - 1) == .bang) {
            const start = unit.tree.tokenStart(first - 1);
            const end = unit.tree.tokenStart(first) + source.len;
            const annotated_type = unit.tree.source[start..end];
            return makeSlice(u8, annotated_type.ptr, annotated_type.len);
        }
        return makeSlice(u8, source.ptr, source.len);
    }
    const data = unit.tree.nodeData(index);
    const type_index: Ast.Node.Index = switch (unit.tree.nodeTag(index)) {
        .array_type => data.node_and_node[1],
        .optional_type => data.node,
        .ptr_type_aligned => data.opt_node_and_node[1],
        else => return missing,
    };
    return getNodeSource(unit, @backingInt(type_index));
}

pub export fn getNodeAlign(unit: *TranslationUnit, node: ASTNode) callconv(.c) GenericSlice {
    const decl = unit.tree.fullVarDecl(@fromBackingInt(node.index)) orelse
        return .{ .ptr = null, .len = 0 };
    const align_node = decl.ast.align_node.unwrap() orelse
        return .{ .ptr = null, .len = 0 };
    return getNodeSource(unit, @backingInt(align_node));
}

pub export fn getNodeBody(unit: *TranslationUnit, node: ASTNode) callconv(.c) GenericSlice {
    if (unit.tree.fullVarDecl(@fromBackingInt(node.index))) |decl| {
        const init_node = decl.ast.init_node.unwrap() orelse
            return .{ .ptr = null, .len = 0 };
        return getNodeSource(unit, @backingInt(init_node));
    }
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
    switch (tag) {
        .fn_decl => {
            const node_data = unit.tree.nodeData(@fromBackingInt(node.index)).node_and_node;
            return getNodeSource(unit, @backingInt(node_data[1]));
        },
        .test_decl => {
            const node_data = unit.tree.nodeData(@fromBackingInt(node.index)).opt_token_and_node;
            return getNodeSource(unit, @backingInt(node_data[1]));
        },
        .@"comptime" => {
            const body = unit.tree.nodeData(@fromBackingInt(node.index)).node;
            return getNodeSource(unit, @backingInt(body));
        },
        .array_type => {
            const node_data = unit.tree.nodeData(@fromBackingInt(node.index)).node_and_node;
            return getNodeSource(unit, @backingInt(node_data[0]));
        },
        else => return .{ .ptr = null, .len = 0 },
    }
}

pub export fn getNodeParamsCount(unit: *TranslationUnit, node: ASTNode) callconv(.c) usize {
    var buffer: [1]Ast.Node.Index = undefined;
    const full_fn_proto = unit.tree.fullFnProto(&buffer, @fromBackingInt(node.index)) orelse return 0;
    var params = full_fn_proto.iterate(unit.tree);
    var count: usize = 0;
    while (params.next() != null) count += 1;
    return count;
}

pub export fn getNodeParams(
    unit: *TranslationUnit,
    node: ASTNode,
    out: [*]NodeParam,
    capacity: usize,
) callconv(.c) usize {
    var buffer: [1]Ast.Node.Index = undefined;
    const full_fn_proto = unit.tree.fullFnProto(&buffer, @fromBackingInt(node.index)) orelse return 0;

    var i: usize = 0;
    var params = full_fn_proto.iterate(unit.tree);
    while (params.next()) |param| {
        if (i >= capacity) break;
        const param_type = if (param.type_expr) |type_expr|
            unit.tree.getNodeSource(type_expr)
        else
            unit.tree.tokenSlice(param.anytype_ellipsis3.?);
        const param_name = if (param.name_token) |name|
            unit.tree.tokenSlice(name)
        else
            "";
        const modifier = if (param.comptime_noalias) |token| unit.tree.tokenTag(token) else null;
        out[i] = .{
            .name = makeSlice(u8, param_name.ptr, param_name.len),
            .type = makeSlice(u8, param_type.ptr, param_type.len),
            .is_comptime = modifier == .keyword_comptime,
            .is_noalias = modifier == .keyword_noalias,
        };
        i += 1;
    }
    return i;
}

pub export fn isNodeExtern(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
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

pub export fn isNodeExport(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
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

pub export fn isNodePublic(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
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

pub export fn isNodeConst(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
    const token_index = switch (tag) {
        .identifier => if (node.main_token > 0) node.main_token - 1 else node.main_token,
        else => node.main_token,
    };
    return std.mem.eql(u8, unit.tree.tokenSlice(token_index), "const");
}

pub export fn isNodeContainer(node: ASTNode) callconv(.c) bool {
    const tag: Tag = @fromBackingInt(@intCast(node.tag_index));
    return switch (tag) {
        .container_decl,
        .container_decl_trailing,
        .container_decl_two,
        .container_decl_two_trailing,
        => true,
        else => false,
    };
}

pub export fn isNodeStruct(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "struct");
}

pub export fn isNodeUnion(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "union");
}

pub export fn isNodeOpaque(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "opaque");
}

pub export fn isNodeEnum(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    if (!isNodeContainer(node)) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token), "enum");
}

pub export fn isNodeErrorUnion(unit: *TranslationUnit, node: ASTNode) callconv(.c) bool {
    if (node.main_token < 1) return false;
    return std.mem.eql(u8, unit.tree.tokenSlice(node.main_token - 1), "!");
}
