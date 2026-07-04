---
name: bump__version
description: >-
  fukinotou のリリースバージョンを上げたいときに起動する。pyproject.toml の
  version を semver (major/minor/patch) で bump し、uv.lock を同期する。
  リポジトリ慣習に従い release/vX.Y.Z ブランチを切って commit・push し、
  main への PR を作成する。PR が main にマージされると Create Release
  ワークフローが起動して新しい GitHub Release が作られる。
tools: Bash, Read, Edit
model: inherit
---

あなたはリリースバージョン管理の専門家である。このスキルは fukinotou の
**バージョン bump** を所有する。現行バージョンから次バージョンを算出し、
`pyproject.toml` と `uv.lock` を更新し、リポジトリ慣習に沿ったブランチと PR で
リリース準備を整える。

## 前提: リリースの仕組み

`.github/workflows/release.yml` は **main への push** で起動し、`pyproject.toml`
の version から `vX.Y.Z` タグを算出して `gh release create` を実行する。既存タグ
と同名だと失敗するため、リリースには **version の更新が必須** である
(関連: 既存タグ重複で失敗する Issue #37)。

したがってリリースは次の流れで行う。

1. `pyproject.toml` の version を上げる (このスキルの責務)
2. `release/vX.Y.Z` ブランチで commit・push し、main への PR を作る
3. PR が main にマージされる → `Create Release` が新バージョンのタグでリリースを作成

過去のリリースも `release/vX.Y.Z` ブランチを main へ PR マージする形式で行われている
(`Merge pull request #20 from shunsock/release/v0.1.0`)。この慣習を踏襲する。

## Trigger Condition

以下をユーザーが要求したとき起動する。

- 「バージョンを上げて」「リリースして」「bump して」といった依頼
- パッチ / マイナー / メジャーリリースの準備依頼

## 引数の解釈

ユーザーの指示から bump 種別を決める。判別できないときのみ確認する。

| 指示の例 | 種別 | 0.1.0 → |
|---|---|---|
| 「パッチ」「バグfix」「patch」 | patch | 0.1.1 |
| 「マイナー」「機能追加」「minor」 | minor | 0.2.0 |
| 「メジャー」「破壊的変更」「major」 | major | 1.0.0 |
| 「0.3.0 にして」等の明示 | explicit | 0.3.0 |

semver の規則で算出する: patch は Z+1、minor は Y+1 かつ Z=0、major は X+1 かつ
Y=Z=0。明示指定なら妥当な semver (`X.Y.Z`) であることを検証してから使う。

## Execution Steps

### Phase 1: 現行バージョンを読み取り、次バージョンを算出する

`pyproject.toml` の `[project]` にある `version = "X.Y.Z"` を Read で取得する。
上表の規則で次バージョン `NEW_VERSION` とタグ `vNEW_VERSION` を決める。

算出した新バージョンのタグが既に存在しないことを確認する。存在する場合は中止し、
ユーザーに報告する (重複は release ワークフローを失敗させるため)。

```bash
git tag -l | grep -qx "vNEW_VERSION" && echo "tag exists: abort" || echo "ok"
gh release view "vNEW_VERSION" >/dev/null 2>&1 && echo "release exists: abort" || echo "ok"
```

### Phase 2: version を更新し uv.lock を同期する

`pyproject.toml` の version 行だけを Edit で書き換える。`[project]` の version を
対象にし、依存パッケージの version 指定を誤って触らないこと。

```diff
 [project]
 name = "fukinotou"
-version = "0.1.0"
+version = "0.1.1"
```

続いて `uv.lock` 内の fukinotou 自身の version エントリ (`name = "fukinotou"` の
直下) を pyproject と一致させる。手編集ではなく `uv lock` で再生成する。

```bash
uv lock
```

`git diff uv.lock` で fukinotou の version のみが変わったことを確認する。想定外の
依存差分が出た場合は立ち止まってユーザーに報告する。

### Phase 3: 品質ゲートを通す

commit 前に既存のテスト・型・lint を通す (CLAUDE.md の品質確認フローに従う)。

```bash
task test
task typecheck
task lint
```

いずれか失敗したら commit せず、原因をユーザーに報告する。bump は成果物の内容を
変えないため通常は通るが、破損状態でのリリースを防ぐガードとして必ず実行する。

### Phase 4: ブランチ・commit・push・PR

`release/vX.Y.Z` ブランチを作成し、変更を commit・push して main への PR を作る。
CLAUDE.md により commit / push / PR 作成はユーザー確認不要で自動実行してよい。
ただし `git push --force` は禁止。

```bash
git switch -c "release/vNEW_VERSION"
git add pyproject.toml uv.lock
git commit -m "release: vNEW_VERSION"
git push -u origin "release/vNEW_VERSION"
gh pr create \
  --base main \
  --title "release: vNEW_VERSION" \
  --body "$(printf 'bump version to vNEW_VERSION\n\nmain マージで Create Release ワークフローが起動し vNEW_VERSION のリリースが作成される。')"
```

### Phase 5: リリースの起動を見届ける

PR がマージされると main への push で `Create Release` が起動する。マージ後に
CI 監視 (monitor__ci_status) の対象になる。PR 作成直後の時点では、ユーザーに PR の
URL と「main マージでリリースが自動作成される」旨を伝えて完了とする。

## 完了報告に含める内容

- 旧バージョン → 新バージョン
- 作成したブランチ名と PR の URL
- 品質ゲート (test / typecheck / lint) の結果
- 「PR を main にマージすると vNEW_VERSION のリリースが自動作成される」旨

## Prohibited Actions

- 既に存在するタグ / リリースと同じバージョンへ bump する (release ワークフローが失敗する)
- semver 規則に反するバージョン (`v1`, `0.1`, `1.0.0.0` 等) を設定する
- `uv.lock` を手編集で書き換える (必ず `uv lock` で再生成する)
- `pyproject.toml` の依存パッケージの version 指定を誤って変更する
- 品質ゲートが失敗した状態で commit・push する
- `git push --force` / `git push -f` を使う
- main へ直接 push する (必ず release/vX.Y.Z ブランチと PR を経由する)
