from typing import cast

from zyntex.parsing.syntax import ComptimeBlock, VariableDeclaration
from zyntex.parsing import SourceCode


class TestComptimeBlock:

    def test_multiline_comptime_block(self):
        code = SourceCode("""
comptime {
    // Keep formatting.
    var suma: usize = 0;
    suma += 1;
}
""".strip())
        assert code.errors == []
        assert len(code.content) == 1
        comptime_block: ComptimeBlock = cast(ComptimeBlock, code.content[0])
        assert comptime_block.body == """
{
    // Keep formatting.
    var suma: usize = 0;
    suma += 1;
}
""".strip()

    def test_nested_comptime_block(self):
        code = SourceCode('comptime { const text = "za\u017c\u00f3\u0142\u0107"; if (true) { _ = text; } }')
        assert code.errors == []
        assert len(code.content) == 1
        comptime_block: ComptimeBlock = cast(ComptimeBlock, code.content[0])
        assert comptime_block.body == '{ const text = "za\u017c\u00f3\u0142\u0107"; if (true) { _ = text; } }'

    def test_lazy_comptime_block(self):
        code = SourceCode("comptime { var suma: usize = 0; suma += 1; }", lazy_parsing=True)
        assert code.errors == []
        assert len(code.content) == 1
        comptime_block: ComptimeBlock = cast(ComptimeBlock, code.content[0])
        assert comptime_block.body == "{ var suma: usize = 0; suma += 1; }"
        assert comptime_block.body == "{ var suma: usize = 0; suma += 1; }"

    def test_comptime_blocks_declaration_order(self):
        code = SourceCode("const before = 1; comptime {} const after = 2; comptime {}")
        assert code.errors == []
        assert len(code.content) == 4
        assert isinstance(code.content[0], VariableDeclaration)
        assert isinstance(code.content[1], ComptimeBlock)
        assert isinstance(code.content[2], VariableDeclaration)
        assert isinstance(code.content[3], ComptimeBlock)
