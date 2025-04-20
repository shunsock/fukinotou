from pathlib import Path


class TextFileLoader:
    """テキストファイルローダークラス

    テキストファイルを読み込むためのシンプルなローダークラス
    """

    def __init__(self, path: str | Path) -> None:
        """初期化

        Args:
            path: 読み込むファイルのパス

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: ファイルのパスがディレクトリである場合
        """
        self.file_path = Path(path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"Input path is directory path: {self.file_path}")

    def load(self) -> str:
        """テキストファイルを読み込む

        Returns:
            読み込んだテキストデータ
        """

        with open(self.file_path, "r", encoding="utf-8") as f:
            return f.read()
