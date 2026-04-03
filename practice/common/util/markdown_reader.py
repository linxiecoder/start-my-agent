

from pathlib import Path
from typing import Optional


class MarkdownReader:
    """读取 Markdown 文件的工具类"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化读取器

        Args:
            base_dir: 基准目录，默认为当前脚本所在目录
        """
        if base_dir is None:
            self.base_dir = Path(__file__).parent
        else:
            self.base_dir = Path(base_dir)

        self._cache = {}  # 缓存 {file_path: content}

    def read(self, relative_path: str, use_cache: bool = True) -> str:
        """
        读取指定相对路径的 Markdown 文件

        Args:
            relative_path: 相对于 base_dir 的文件路径，例如 "Prompt/system_prompt.md"
            use_cache: 是否使用缓存

        Returns:
            文件内容字符串，若读取失败则返回空字符串并打印错误
        """
        file_path = self.base_dir / relative_path

        if use_cache and file_path in self._cache:
            return self._cache[file_path]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if use_cache:
                self._cache[file_path] = content
            return content
        except FileNotFoundError:
            print(f"错误：文件不存在 - {file_path}")
            return ""
        except Exception as e:
            print(f"读取文件失败：{e}")
            return ""

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()