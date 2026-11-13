from enum import Enum

from ._generated_enums import ErrorTag, NodeTag, TokenTag

__all__ = ("ErrorTag", "NodeTag", "TokenTag", "PrimitiveType")


# pylint: disable=invalid-name


class PrimitiveType(Enum):
    """
    Bindings for Zig primitive types.
    Ref: https://ziglang.org/documentation/0.17.1/#Primitive-Types
    """
    i8 = "i8"
    i16 = "i16"
    i32 = "i32"
    i64 = "i64"
    i128 = "i128"

    u8 = "u8"
    u16 = "u16"
    u32 = "u32"
    u64 = "u64"
    u128 = "u128"

    isize = "isize"
    usize = "usize"

    c_char = "c_char"
    c_short = "c_short"
    c_ushort = "c_ushort"

    c_int = "c_int"
    c_uint = "c_uint"
    c_long = "c_long"
    c_ulong = "c_ulong"

    c_longlong = "c_longlong"
    c_ulonglong = "c_ulonglong"
    c_longdouble = "c_longdouble"

    f16 = "f16"
    f32 = "f32"
    f64 = "f64"
    f80 = "f80"
    f128 = "f128"

    bool = "bool"
    anyopaque = "anyopaque"
    void = "void"
    noreturn = "noreturn"
    type = "type"
    anyerror = "anyerror"
    comptime_int = "comptime_int"
    comptime_float = "comptime_float"
