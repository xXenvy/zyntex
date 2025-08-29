const std = @import("std");
const structs = @import("structs.zig");

const Ast = std.zig.Ast;
const GPA = std.heap.GeneralPurposeAllocator(.{ .safety = true });

pub const TranslationUnit = @This();

tree: *Ast,
buffer: [:0]const u8,
gpa_allocator: GPA,

errors: []const structs.ErrorReport,
nodes: []const structs.ASTNode,
tokens: []const structs.ASTToken,

pub fn initFromFile(file_path: [*:0]const u8) !TranslationUnit {
    var file = try std.fs.cwd().openFile(std.mem.span(file_path), .{ .mode = .read_only });
    defer file.close();
    const file_stat = try file.stat();

    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const buffer = try file.readToEndAllocOptions(
        allocator,
        file_stat.size,
        null,
        1,
        0,
    );
    return try initFromSource(buffer);
}

pub fn initFromSource(source: [*:0]const u8) !TranslationUnit {
    var tu: TranslationUnit = undefined;
    tu.gpa_allocator = GPA{};
    const allocator = tu.gpa_allocator.allocator();

    // Make a copy on the heap, since AST keeps a reference to the source.
    const heap_source = try allocator.dupeZ(u8, std.mem.span(source));

    const ast_ptr = try allocator.create(std.zig.Ast);
    ast_ptr.* = try std.zig.Ast.parse(allocator, heap_source, .zig);

    const internal_errors: []const std.zig.Ast.Error = ast_ptr.errors;
    const count = internal_errors.len;
    const error_slice = try allocator.alloc(structs.ErrorReport, count);

    for (0..count) |i| {
        const src = internal_errors[i];
        const dest = &error_slice[i];
        dest.* = .{
            .tag_index = @intFromEnum(src.tag),
            .is_note = src.is_note,
            .token_is_prev = src.token_is_prev,
            .token_index = @intCast(src.token),
        };
    }

    const node_count = ast_ptr.nodes.len;
    const node_copy = try allocator.alloc(structs.ASTNode, node_count);
    for (0..node_count) |i| {
        const original_node: Ast.Node = ast_ptr.nodes.get(i);
        node_copy[i] = .{
            .index = @intCast(i),
            .tag_index = @intFromEnum(original_node.tag),
            .main_token = original_node.main_token,
            .lhs = original_node.data.lhs,
            .rhs = original_node.data.rhs,
        };
    }

    const tokens_count = ast_ptr.tokens.len;
    const tokens_copy = try allocator.alloc(structs.ASTToken, tokens_count);
    for (0..tokens_count) |i| {
        const original_token = ast_ptr.tokens.get(i);
        tokens_copy[i] = .{
            .tag_index = @intFromEnum(original_token.tag),
            .start = original_token.start,
        };
    }

    tu.tree = ast_ptr;
    tu.buffer = heap_source;
    tu.errors = error_slice;
    tu.nodes = node_copy;
    tu.tokens = tokens_copy;
    return tu;
}

pub fn deinit(self: *TranslationUnit) void {
    const allocator = self.gpa_allocator.allocator();
    self.tree.deinit(allocator);
    allocator.destroy(self.tree);

    allocator.free(self.buffer);
    if (self.errors.len > 0) allocator.free(self.errors);
    if (self.nodes.len > 0) allocator.free(self.nodes);
    if (self.tokens.len > 0) allocator.free(self.tokens);

    _ = self.gpa_allocator.deinit();
}
