const GenericSlice = @import("../src/c_api.zig").GenericSlice;

pub const ErrorReport = extern struct {
    tag_index: u32,
    is_note: bool,
    token_is_prev: bool,
    token_index: u32,
};

pub const ASTNode = extern struct {
    index: u32,
    tag_index: u32,
    main_token: u32,
};

pub const ASTToken = extern struct {
    tag_index: u32,
    start: u32,
};

pub const NodeParam = extern struct {
    name: GenericSlice,
    type: ASTNode,
    is_comptime: bool,
};
