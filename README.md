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
