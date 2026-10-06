---
name: claurd
description: Before asking the user to repeat something or working it out again, search this session's own transcript. Use when a detail that came up earlier is no longer in your context after compaction, such as an exact command and its options, a file path, a number, a decision, or when the user says "we talked about this before" / 「前に話した」「あのときのコマンド」. Returns the matching turns verbatim, with transcript line numbers. Not for things that were never said here.
---

# ClaUrd

圧縮で失った自分の過去を、transcript から言葉で引く。要約ではなく、当時の発言と、当時打ったコマンドがそのまま返る。

スクリプトはこの skill のベースディレクトリにある `claurd.py`（Python 3.8 以上、標準ライブラリのみ）。

## 二段で使う

**1. find で場所を見つける**

```bash
python "<ベースディレクトリ>/claurd.py" find "7zr"
```

- 会話の本文と、コマンドの入力（ツール呼び出しの引数）の両方を探す。道具の名前は会話に出ず、コマンドにだけ残っていることが多い
- 当たった行には `*` が付く。種類は `user` / `asst` / `cmd` / `out`
- 各行の頭の `L12345` が transcript の行番号

**2. show で前後を読む**

```bash
python "<ベースディレクトリ>/claurd.py" show 12340 12360
```

- その範囲の発言、コマンド、結果の頭を、順番どおりに返す
- 終わりの行を省くと、前後 40 行
- 切られた箇所の全文が要るときだけ `--full`。範囲を狭めてから付ける

## find の主な引数

| 引数 | 意味 |
|---|---|
| `-w talk,cmd` | 探す場所。`talk`＝会話、`cmd`＝コマンドの入力、`out`＝ツールの出力、`all`。既定は `talk,cmd` |
| `-C 1` | 前後に添える発言の数 |
| `--since` / `--until` | `YYYY-MM-DD` で期間を絞る |
| `--max 20` | 返す当たりの上限。新しい側から数える |
| `-s all` | `all`＝同じフォルダから起動した全セッション、`current`＝いまのセッションだけ、またはセッションIDの頭 |
| `-F` | 正規表現でなく、そのままの文字列として探す |

`list` で、対象になる transcript を確かめられる。

## 心得

- 語は具体的に。道具の名前、ファイル名、固有名詞、数字が効く。意味では探せない
- 当たりが多いときは、`--since` で絞るか、語を足す（`"clasp.*push"`）
- `out` は量が多い。コマンドの結果そのものを探すときだけ足す
- 返ってきたのは当時の記録。ファイルやコマンドがいまも同じとは限らないので、使う前に確かめる
- 30日書き込みのない transcript は Claude Code が消す（`cleanupPeriodDays`）。古い話が当たらないときは、消えた可能性をユーザーに伝える。設定は自分では変えない
- 圧縮の要約、system-reminder、サブエージェントの行、ClaUrd 自身の呼び出しは、探す対象に入っていない
