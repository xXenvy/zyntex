pub fn publicTestFunc() usize {
    return 1;
}

fn privateTestFunc(x: usize) usize {
    return x;
}

pub extern fn publicExternTest(a: usize) !void;
extern fn privateExternTest() usize;

pub export fn publicExportTest(a: ?*u32, b: *myStruct) void {
    _ = a;
    _ = b;
}
export fn privateExportTest() usize {}

const myStruct = struct {};

fn testFuncParams(abc: ?usize, comptime len: u32) !void {}