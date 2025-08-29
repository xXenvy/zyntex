from zyntex import SourceModule
from pathlib import Path


class TestSourceModule:

    def test_basic_usage(self):
        module = SourceModule(dir_path=str(self.path_to_test_sources / "test_module"))
        files = module.files
        assert len(files) == 2
        assert files[0].path == str(self.path_to_test_sources / "test_module" / "src.zig")
        assert files[1].path == str(self.path_to_test_sources / "test_module" / "inside" / "src2.zig")

    @property
    def path_to_test_sources(self) -> Path:
        return Path(__file__).resolve().parent / "test_sources"
