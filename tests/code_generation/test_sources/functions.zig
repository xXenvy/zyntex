pub fn publicTestFunc() usize {
    return 1;
}

fn privateTestFunc(x: usize) usize {
    return x;
}

pub extern fn publicExternTest(a: usize) void;
extern fn privateExternTest() usize;

pub export fn publicExportTest(a: ?*u32, b: **u32) void {
    _ = a;
    _ = b;
}
export fn privateExportTest() usize {}
