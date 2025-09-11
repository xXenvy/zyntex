const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const targets = [_]std.Target.Query{
        .{ .cpu_arch = .x86_64, .os_tag = .linux, .abi = .gnu },
        .{ .cpu_arch = .x86_64, .os_tag = .windows, .abi = .msvc },
        .{ .cpu_arch = .x86_64, .os_tag = .macos, .abi = .none },
    };

    for (targets) |target| {
        const module = b.createModule(.{
            .target = b.resolveTargetQuery(target),
            .optimize = optimize,
            .root_source_file = .{
                .src_path = .{ .owner = b, .sub_path = "src/c_api.zig" },
            },
        });
        const lib = b.addLibrary(.{
            .name = "clib",
            .linkage = .dynamic,
            .root_module = module,
        });
        b.installArtifact(lib);
    }

    const tests_module = b.createModule(.{
        .root_source_file = .{
            .src_path = .{ .owner = b, .sub_path = "tests_runner.zig" },
        },
        .target = b.standardTargetOptions(.{}),
        .optimize = optimize,
    });
    const unit_tests = b.addTest(.{
        .name = "tests",
        .root_module = tests_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("test", "Run unit tests");

    test_step.dependOn(&run_unit_tests.step);
    b.installArtifact(unit_tests);
}
