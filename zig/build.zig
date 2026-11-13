const std = @import("std");
const builtin = @import("builtin");

comptime {
    if (!std.mem.eql(u8, builtin.zig_version_string, "0.17.1")) {
        @compileError("Zyntex requires Zig 0.17.1; AST bindings depend on the compiler version.");
    }
}

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const targets = [_]std.Target.Query{
        .{ .cpu_arch = .x86_64, .os_tag = .linux, .abi = .gnu },
        .{ .cpu_arch = .x86_64, .os_tag = .windows, .abi = .msvc },
        .{ .cpu_arch = .x86_64, .os_tag = .macos, .abi = .none },
    };

    const bindings_generator = b.addExecutable(.{
        .name = "generate-bindings",
        .root_module = b.createModule(.{
            .root_source_file = b.path("tools/generate_bindings.zig"),
            .target = b.graph.host,
        }),
    });
    const generate = b.addRunArtifact(bindings_generator);
    generate.has_side_effects = true;
    generate.setCwd(b.path("."));
    generate.addArgs(&.{ "--update", "../zyntex/parsing/bindings/_generated_enums.py" });
    b.step("bindings", "Check Python AST enums and generate if needed").dependOn(&generate.step);

    const check_bindings = b.addRunArtifact(bindings_generator);
    check_bindings.has_side_effects = true;
    check_bindings.setCwd(b.path("."));
    check_bindings.addArgs(&.{ "--check", "../zyntex/parsing/bindings/_generated_enums.py" });

    for (targets) |target| {
        const module = b.createModule(.{
            .target = b.resolveTargetQuery(target),
            .optimize = optimize,
            .root_source_file = b.path("src/c_api.zig"),
        });
        const lib = b.addLibrary(.{
            .name = "clib",
            .linkage = .dynamic,
            .root_module = module,
        });
        b.installArtifact(lib);
    }

    const tests_module = b.createModule(.{
        .root_source_file = b.path("tests_runner.zig"),
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
    test_step.dependOn(&check_bindings.step);
}
