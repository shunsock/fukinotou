import os
import tempfile
import pytest

from fukinotou import TextFileLoader


def test_text_file_loader_init_and_load() -> None:
    """TextFileLoaderの初期化とloadメソッドのテスト

    テキストファイルが正しく読み込まれるかを確認する
    """
    # Arrange - 一時ファイルを作成
    test_content = "This is a test file content"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(test_content)
        temp_path = temp_file.name

    try:
        # Act - ローダーを初期化してファイルを読み込む
        loader = TextFileLoader(temp_path)
        result = loader.load()

        # Assert - 期待する結果と比較
        assert result == test_content
    finally:
        # Cleanup - テストファイルを削除
        os.unlink(temp_path)


def test_text_file_loader_init_file_not_found() -> None:
    """TextFileLoaderの初期化で存在しないファイルを指定するとFileNotFoundErrorが発生するか確認する"""
    # Arrange - 存在しないパス
    non_existent_path = "/path/that/does/not/exist.txt"

    # Act & Assert - FileNotFoundErrorが発生するか確認
    with pytest.raises(FileNotFoundError):
        TextFileLoader(non_existent_path)


def test_text_file_loader_init_directory_path() -> None:
    """TextFileLoaderの初期化でディレクトリパスを指定するとValueErrorが発生するか確認する"""
    # Arrange - 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        # Act & Assert - ValueErrorが発生するか確認
        with pytest.raises(ValueError):
            TextFileLoader(temp_dir)
