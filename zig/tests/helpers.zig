// Normalize line endings: removes all '\r'
pub fn normalize(input: []const u8, output: []u8) []const u8 {
    var out_idx: usize = 0;

    for (input) |c| {
        if (c != '\r') {
            output[out_idx] = c;
            out_idx += 1;
        }
    }
    return output[0..out_idx];
}
