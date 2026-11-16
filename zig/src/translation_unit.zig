const std = @import("std");
const structs = @import("structs.zig");

const Ast = std.zig.Ast;

pub const TranslationUnit = @This();

tree: *Ast,
buffer: [:0]const u8,
arena: std.heap.ArenaAllocator,

errors: []const structs.ErrorReport,
tokens: []const structs.ASTToken,
nodes: []const structs.ASTNode,

pub fn initFromFile(backing_allocator: std.mem.Allocator, file_path: []const u8) !TranslationUnit {
    var io_backend = std.Io.Threaded.init(backing_allocator, .{});
    defer io_backend.deinit();
    const buffer = try std.Io.Dir.cwd().readFileAllocOptions(
        io_backend.io(),
        file_path,
        backing_allocator,
        .unlimited,
        .of(u8),
        0,
    );
    defer backing_allocator.free(buffer);
    return try initFromSource(backing_allocator, buffer);
}

pub fn initFromSource(backing_allocator: std.mem.Allocator, source: []const u8) !TranslationUnit {
    var arena = std.heap.ArenaAllocator.init(backing_allocator);
    errdefer arena.deinit();
    const arena_allocator = arena.allocator();

    // Make a copy on the heap, since AST keeps a reference to the source.
    const heap_source = try arena_allocator.dupeSentinel(u8, source, 0);

    const ast_ptr = try arena_allocator.create(std.zig.Ast);
    ast_ptr.* = try std.zig.Ast.parse(arena_allocator, heap_source, .{ .mode = .zig });

    const internal_errors: []const std.zig.Ast.Error = ast_ptr.errors;
    const count = internal_errors.len;
    const error_slice = try arena_allocator.alloc(structs.ErrorReport, count);

    for (0..count) |i| {
        const src = internal_errors[i];
        const dest = &error_slice[i];
        dest.* = .{
            .tag_index = @backingInt(src.tag),
            .is_note = src.is_note,
            .token_is_prev = src.token_is_prev,
            .token_index = @intCast(src.token),
        };
    }

    const tokens_count = ast_ptr.tokens.len;
    const tokens_copy = try arena_allocator.alloc(structs.ASTToken, tokens_count);
    for (0..tokens_count) |i| {
        const original_token = ast_ptr.tokens.get(i);
        tokens_copy[i] = .{
            .tag_index = @backingInt(original_token.tag),
            .start = original_token.start,
        };
    }

    const node_count = ast_ptr.nodes.len;
    const node_copy = try arena_allocator.alloc(structs.ASTNode, node_count);
    for (0..node_count) |i| {
        const original_node: Ast.Node = ast_ptr.nodes.get(i);
        node_copy[i] = .{
            .index = @intCast(i),
            .tag_index = @backingInt(original_node.tag),
            .main_token = original_node.main_token,
        };
    }

    return .{
        .arena = arena,
        .tree = ast_ptr,
        .buffer = heap_source,
        .errors = error_slice,
        .tokens = tokens_copy,
        .nodes = node_copy,
    };
}

pub fn deinit(self: *TranslationUnit) void {
    self.arena.deinit();
    self.* = undefined;
}
