from typing import cast
from pathlib import Path

from zyntex import SourceFile
from zyntex.syntax import FunctionDeclaration
from zyntex.bindings import PrimitiveType


class TestSourceFile:

    def test_basic_usage(self):
        file = SourceFile(file_path=str(self.path_to_test_sources / "basic.zig"))
        assert file.path == str(self.path_to_test_sources / "basic.zig")
        assert len(file.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, file.content[0])
        assert function_decl.name == "testing"
        assert function_decl.public is False
        assert function_decl.body == "{}"

        assert function_decl.return_type.is_type()
        assert not function_decl.return_type.is_const()
        assert function_decl.return_type.absolute_type == PrimitiveType.void

    @property
    def path_to_test_sources(self) -> Path:
        return Path(__file__).resolve().parent / "test_sources"
