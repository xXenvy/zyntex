const std = @import("std");
pub const publicVariable: comptime_int = 10;
pub var publicOptionalVariable: ?usize = null;

extern const externPrivateVariable: ?*[2]usize;
pub extern var externPublicVariable: *?*void;

pub export var exportPublicVariable: u32 = 15;
export const exportPrivateVariable: i32 = -25;