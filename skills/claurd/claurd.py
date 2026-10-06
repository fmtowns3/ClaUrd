#!/usr/bin/env python3
"""ClaUrd: 圧縮で失った自分の過去を、transcript から言葉で引く。

find  会話の本文とコマンドの入力を検索し、行番号つきで返す。
show  行番号の範囲を、発言・コマンド・結果の頭まで含めて返す。
list  対象になる transcript を並べる。

索引は作らない。呼ばれるたびに transcript を読む。標準ライブラリだけで動く。
"""
import argparse
import bisect
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

TALK_CUT, CMD_CUT, OUT_CUT = 300, 1500, 200
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
TALK = ("user", "asst")
WHERE = {"talk": TALK, "cmd": ("cmd",), "out": ("out",)}


def transcripts(which):
    """いまのセッションの transcript と、同じフォルダ（同じ起動パス）の transcript。"""
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    cur = next(iter(root.glob("*/%s.jsonl" % sid)), None) if sid else None
    folder = cur.parent if cur else root / re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if cur is None and files:
        cur = files[0]
    if which == "current":
        return [cur] if cur else [], cur
    if which != "all":
        files = [p for p in files if p.stem.startswith(which)]
    return files, cur


def local(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    except (AttributeError, ValueError):
        return None


def items(path, with_out):
    """(行番号, 種類, 日時, 本文) を順に返す。種類は user / asst / cmd / out。

    圧縮の要約、メタ行、サブエージェントの行、system-reminder は返さない。
    ClaUrd 自身の呼び出しとその結果も返さない（引くたびに当たりが増えるのを防ぐ）。
    """
    own = set()
    with open(path, "rb") as f:
        for no, raw in enumerate(f, 1):
            if b'"type":"user"' not in raw and b'"type":"assistant"' not in raw:
                continue
            try:
                d = json.loads(raw)
            except ValueError:
                continue
            who = {"user": "user", "assistant": "asst"}.get(d.get("type"))
            if not who or d.get("isCompactSummary") or d.get("isMeta") or d.get("isSidechain"):
                continue
            content = (d.get("message") or {}).get("content")
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            when = local(d.get("timestamp"))
            for b in content or []:
                if not isinstance(b, dict):
                    continue
                kind = b.get("type")
                if kind == "text":
                    text = REMINDER.sub("", b.get("text") or "").strip()
                    if text and not text.startswith("<task-notification>"):
                        yield no, who, when, text
                elif kind == "tool_use":
                    inp = b.get("input") or {}
                    cmd = inp.get("command")
                    if not isinstance(cmd, str):
                        cmd = json.dumps(inp, ensure_ascii=False)
                    if "claurd.py" in cmd:
                        own.add(b.get("id"))
                    else:
                        yield no, "cmd", when, "%s: %s" % (b.get("name"), cmd)
                elif kind == "tool_result" and with_out and b.get("tool_use_id") not in own:
                    res = b.get("content")
                    if isinstance(res, list):
                        res = "\n".join(x.get("text") or "" for x in res
                                        if isinstance(x, dict) and x.get("type") == "text")
                    if isinstance(res, str) and res.strip():
                        yield no, "out", when, res.strip()


def cut(text, limit, flat=True):
    if flat:
        text = " / ".join(s.strip() for s in text.splitlines() if s.strip())
    return text if len(text) <= limit else "%s …(全%d字)" % (text[:limit], len(text))


def line(mark, item, body):
    no, kind, when, _ = item
    return "%sL%d [%s %s] %s" % (mark, no, kind, when.strftime("%Y-%m-%d %H:%M") if when else "-", body)


def around(text, m):
    a, b = max(0, m.start() - 120), min(len(text), m.end() + 280)
    return ("…" if a else "") + cut(text[a:b], 10 ** 9) + ("…" if b < len(text) else "")


def head(path, cur, note):
    print("== %s%s %s" % (path.stem[:8], "（このセッション）" if path == cur else "", note))


def find(a):
    pat = re.compile(re.escape(a.pattern) if a.fixed else a.pattern, 0 if a.case else re.I)
    kinds = tuple(k for w in a.where.split(",") for k in (WHERE[w] if w in WHERE else sum(WHERE.values(), ())))
    files, cur = transcripts(a.session)
    if not files:
        print("transcript が見つかりません。")
    for path in files:
        seq = list(items(path, "out" in kinds))
        talk = [i for i, it in enumerate(seq) if it[1] in TALK]
        hits = []
        for i, it in enumerate(seq):
            day = it[2].strftime("%Y-%m-%d") if it[2] else ""
            if it[1] in kinds and (not a.since or day >= a.since) and (not a.until or day <= a.until) \
                    and pat.search(it[3]):
                hits.append(i)
        older = max(0, len(hits) - a.max)
        head(path, cur, "当たり %d 件%s" % (len(hits), "（古い %d 件は省略。--since/--until か --max で絞る）" % older if older else ""))
        hit, near = set(hits[older:]), set()
        for i in hit:
            p = bisect.bisect_left(talk, i)
            near.update(talk[max(0, p - a.context):p] + talk[p + (i in talk):][:a.context])
        last = None
        for j in sorted(hit | near):
            if last is not None and j > last + 1:
                print("  --")
            last = j
            text = seq[j][3]
            print(line("* " if j in hit else "  ", seq[j], around(text, pat.search(text)) if j in hit else cut(text, 120)))


def show(a):
    files, cur = transcripts(a.session if a.session != "all" else "current")
    if not files:
        print("transcript が見つかりません。")
        return
    lo, hi = (a.start, a.end) if a.end else (a.start - 40, a.start + 40)
    head(files[0], cur, "L%d〜L%d" % (max(1, lo), hi))
    for it in items(files[0], True):
        if it[0] > hi:
            break
        if it[0] < lo:
            continue
        if it[1] in TALK:
            print(line("", it, it[3] if a.full else cut(it[3], TALK_CUT)))
        elif it[1] == "cmd":
            print(line("  ", it, it[3] if a.full else cut(it[3], CMD_CUT, flat=False)))
        else:
            print(line("    ", it, it[3] if a.full else cut(it[3], OUT_CUT)))


def listing(a):
    files, cur = transcripts("all")
    for p in files:
        st = p.stat()
        head(p, cur, "%s 更新 / %.1f MB / %s" % (datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                                              st.st_size / 1e6, p))


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="claurd", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    f = sub.add_parser("find", help="会話とコマンドを検索する")
    f.add_argument("pattern", help="正規表現（大文字小文字は区別しない）")
    f.add_argument("-F", "--fixed", action="store_true", help="正規表現でなく、そのままの文字列として探す")
    f.add_argument("--case", action="store_true", help="大文字小文字を区別する")
    f.add_argument("-C", "--context", type=int, default=1, help="前後に添える発言の数（既定 1）")
    f.add_argument("-w", "--where", default="talk,cmd", help="talk,cmd,out,all の組み合わせ（既定 talk,cmd）")
    f.add_argument("--since", help="YYYY-MM-DD 以降")
    f.add_argument("--until", help="YYYY-MM-DD 以前")
    f.add_argument("--max", type=int, default=20, help="transcript ごとに返す当たりの上限。新しい側から（既定 20）")
    f.add_argument("-s", "--session", default="all", help="all / current / セッションIDの頭（既定 all＝同じ起動パスの全部）")
    f.set_defaults(run=find)
    s = sub.add_parser("show", help="行番号の範囲を返す")
    s.add_argument("start", type=int)
    s.add_argument("end", type=int, nargs="?", help="省くと start の前後 40 行")
    s.add_argument("--full", action="store_true", help="切らずに全文を返す")
    s.add_argument("-s", "--session", default="current", help="current / セッションIDの頭（既定 current）")
    s.set_defaults(run=show)
    sub.add_parser("list", help="対象の transcript を並べる").set_defaults(run=listing)
    a = ap.parse_args()
    a.run(a)


if __name__ == "__main__":
    main()
