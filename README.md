# ClaUrd

A skill that lets Claude Code grep its own past. Urd is the Norn of what has been;
this is her well, for Claude.

After compaction, Claude remembers *that* it built a self-extracting archive, but not
the command or its options. The transcript still has them. ClaUrd searches it and
hands back only the matching turns, **verbatim**, with line numbers.

- **Two steps.** `find` locates the turns; `show` reads the lines around them,
  commands and results included.
- **Conversation and commands.** Both are searched. Tool names rarely appear in the
  conversation; they live in the commands.
- **No index, no LLM, no extra files, no MCP server.** One Python file reads the
  transcript that Claude Code already keeps.

## Why not plain grep

What we measured before writing it (Claude Code 2.1.289, Windows 11, one session of
seven weeks):

- The transcript was **277 MB**, of which the conversation was about 2 million
  characters, roughly 2%. The rest is tool output, images, file history and thinking.
- Plain `grep 7zr` returned **230 lines** for a tool that had never been used. All of
  them were chance matches inside base64 (images, tool output, thinking signatures).
  Short alphanumeric words always hit this.
- The same word also matches compaction summaries and anything a hook pasted back, so
  one remark comes back several times.
- For `clasp`, the conversation had 20 matches and the commands had 110. Searching the
  conversation alone misses most of what was actually done.
- Reading all 277 MB and keeping only conversation and commands takes **about one
  second**. An index would not pay for itself.

## Install

```bash
claude plugin marketplace add fmtowns3/ClaUrd
claude plugin install claurd@claurd
```

Restart Claude Code. Requires Python 3.8 or later on `PATH`.

## Use

Claude calls it on its own when it needs something compaction dropped. You can also
ask: "ClaUrd で 7zr を引いて".

```
$ python claurd.py find 7zr
== bbbb2222（このセッション） 当たり 2 件
* L1 [user 2026-01-02 10:00] 7zr で自己解凍型にして
  L2 [asst 2026-01-02 10:01] 作ります。
* L2 [cmd 2026-01-02 10:01] Bash: 7zr a -sfx out.exe src/

$ python claurd.py show 1 3
L1 [user 2026-01-02 10:00] 7zr で自己解凍型にして
L2 [asst 2026-01-02 10:01] 作ります。
  L2 [cmd 2026-01-02 10:01] Bash: 7zr a -sfx out.exe src/
    L3 [out 2026-01-02 10:02] Everything is Ok
```

| | |
|---|---|
| `find PATTERN` | regex, case-insensitive. `-F` fixed string, `-w talk,cmd,out` where to look, `-C N` neighbouring turns, `--since/--until YYYY-MM-DD`, `--max N`, `-s all\|current\|<id prefix>` |
| `show START [END]` | lines of the transcript, in order. `--full` to stop truncating |
| `list` | the transcripts in scope |

## Scope

By default: the current session, plus every other session started from the same
folder. The current session is found through `CLAUDE_CODE_SESSION_ID`; its siblings
are the other `.jsonl` files beside it. `-s current` narrows to this session alone.

Left out of the search: compaction summaries, system reminders, subagent turns, what
hooks added, and ClaUrd's own calls.

## Limits

- Words, not meaning. "tiger on a screen" will not find "the estimate assumes local
  equipment". For that, use a semantic search such as
  [lore](https://github.com/hyunjae-labs/lore).
- Claude Code deletes transcripts that have not been written to for 30 days
  (`cleanupPeriodDays`, judged by the file's modification time). What is gone is
  gone. ClaUrd keeps no copy of its own; to keep more, raise the setting in
  `~/.claude/settings.json`, for example `"cleanupPeriodDays": 3650`. A session you
  keep using is never deleted, however long ago it began.

## Tested on

Windows 11, Claude Code 2.1.289, Python 3.12, Git Bash. Nothing else yet.

It is one Python file with no dependencies, so it should run on macOS and Linux, but
nobody has tried. If you do, please open an issue and say whether it worked. A report
that it simply works is as welcome as a bug.

Also untested: several real sessions in one folder (only synthetic ones so far).

## Related

[cortex-praefrontalis](https://github.com/fmtowns3/cortex-praefrontalis) hands back
the latest 10,000 characters without being asked. ClaUrd reaches further back, when
asked.

## License

MIT

---

# 日本語

Claude Code が自分の過去を grep するための skill です。ウルズ（Urd）は、過ぎ去ったものを
司る北欧のノルン。その泉を、Claude に。

圧縮のあと、Claude は自己解凍型のアーカイブを作った「こと」は覚えていても、そのときの
コマンドとオプションは覚えていません。transcript には残っています。ClaUrd はそれを
検索し、当たった発言だけを、**原文のまま**、行番号つきで返します。

- **二段で使います。** `find` で場所を見つけ、`show` で前後を読みます。コマンドと結果も
  並びます。
- **会話とコマンドの両方を探します。** 道具の名前は会話にはあまり出ません。コマンドの
  中に残っています。
- **索引なし、LLM なし、中間ファイルなし、MCP サーバーなし。** Claude Code がすでに
  残している transcript を、Python 1 ファイルが読むだけです。

## なぜ素の grep では足りないか

作る前に測ったこと（Claude Code 2.1.289、Windows 11、7 週間続いた 1 セッション）:

- transcript は **277 MB**。そのうち会話は約 200 万字で、全体の 2% ほどでした。残りは
  ツールの出力、画像、ファイル履歴、thinking です。
- 素の `grep 7zr` は、一度も使っていない道具なのに **230 行**当たりました。すべて
  base64（画像、ツール出力、thinking の署名）の中の偶然の一致です。短い英数字の語は、
  必ずこれを踏みます。
- 同じ語は、圧縮の要約にも、hook が貼り戻した文にも当たります。1 つの発言が何度も
  返ってきます。
- `clasp` では、会話に 20 件、コマンドに 110 件ありました。会話だけを探すと、実際に
  やったことの大半を見落とします。
- 277 MB を全部読み、会話とコマンドだけを残すのに、**約 1 秒**です。索引を作っても
  元が取れません。

## インストール

```bash
claude plugin marketplace add fmtowns3/ClaUrd
claude plugin install claurd@claurd
```

Claude Code を再起動してください。`PATH` に Python 3.8 以上が必要です。

## 使い方

圧縮で落ちたものが要るとき、Claude が自分で呼びます。頼むこともできます:
「ClaUrd で 7zr を引いて」。

```
$ python claurd.py find 7zr
== bbbb2222（このセッション） 当たり 2 件
* L1 [user 2026-01-02 10:00] 7zr で自己解凍型にして
  L2 [asst 2026-01-02 10:01] 作ります。
* L2 [cmd 2026-01-02 10:01] Bash: 7zr a -sfx out.exe src/

$ python claurd.py show 1 3
L1 [user 2026-01-02 10:00] 7zr で自己解凍型にして
L2 [asst 2026-01-02 10:01] 作ります。
  L2 [cmd 2026-01-02 10:01] Bash: 7zr a -sfx out.exe src/
    L3 [out 2026-01-02 10:02] Everything is Ok
```

| | |
|---|---|
| `find PATTERN` | 正規表現、大文字小文字は区別しません。`-F` そのままの文字列、`-w talk,cmd,out` 探す場所、`-C N` 前後の発言数、`--since/--until YYYY-MM-DD`、`--max N`、`-s all\|current\|<IDの頭>` |
| `show START [END]` | transcript の行を順番どおりに。`--full` で切らずに全文 |
| `list` | 対象になる transcript |

## 対象

既定では、いまのセッションと、同じフォルダから起動したほかの全セッションです。
いまのセッションは `CLAUDE_CODE_SESSION_ID` で見つけ、その隣にある `.jsonl` を
仲間として扱います。`-s current` で、いまのセッションだけに絞れます。

探す対象に入れないもの: 圧縮の要約、system-reminder、サブエージェントの行、hook が
足したもの、ClaUrd 自身の呼び出し。

## 限界

- 言葉で探します。意味では探せません。「屏風の虎」で「積算は現地の機材を前提に
  している」は出ません。それには [lore](https://github.com/hyunjae-labs/lore) のような
  意味検索を使ってください。
- Claude Code は、30 日書き込みのない transcript を消します（`cleanupPeriodDays`。
  ファイルの更新日時で判定）。消えたものは戻りません。ClaUrd は写しを持ちません。
  長く残すには、`~/.claude/settings.json` の値を大きくしてください（例:
  `"cleanupPeriodDays": 3650`）。使い続けているセッションは、いつ始めたものでも
  消えません。

## 動作確認

Windows 11、Claude Code 2.1.289、Python 3.12、Git Bash。ほかはまだです。

依存のない Python 1 ファイルなので、macOS と Linux でも動くはずですが、誰も試して
いません。試した方は、動いたかどうかを issue で教えてください。「普通に動いた」の
報告も、不具合の報告と同じくらい歓迎します。

未確認がもう 1 つ: 同じフォルダに本物のセッションが複数ある場合（作り物でしか
試していません）。

## 関連

[cortex-praefrontalis](https://github.com/fmtowns3/cortex-praefrontalis) は、直前の
1 万字を、頼まれなくても渡します。ClaUrd は、頼まれたときに、もっと前まで手を
伸ばします。

## ライセンス

MIT
