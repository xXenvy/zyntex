// Valid function: 2 params, snake_case
fn add_numbers(a: i32, b: i32) i32 {
    return a + b;
}

// Valid: exactly 6 params
fn six_params(a: i32, b: i32, c: i32, d: i32, e: i32, f: i32) i32 {
    return a + b + c + d + e + f;
}

// Invalid: 7 parameters (exceeds max), camelCase (invalid name)
fn sevenParams(a: i32, b: i32, c: i32, d: i32, e: i32, f: i32, g: i32) i32 {
    return a + b + c + d + e + f + g;
}

// Valid: snake_case, 3 params
fn multiply_three(a: i32, b: i32, c: i32) i32 {
    return a * b * c;
}
