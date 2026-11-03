#!/usr/bin/env python3
"""Tailor the master resume to a job description through the LiteLLM proxy.

The model only proposes edits (title, summary, skill order, bullet rewrites and
order). Every edit is validated against the original text before it is applied,
so the model cannot add numbers, LaTeX commands or facts that are not already
in the resume. Usage is wrapped by tailor.sh.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "Jose Alberto Tupayachi Silva"

SYSTEM_PROMPT = r"""You tailor a resume to a job description.

Hard rules:
- Only rephrase, reorder and emphasize facts that already appear in the resume.
- Never add employers, tools, skills, certifications, metrics, numbers, dates or
  responsibilities that the resume does not state. If the job asks for something
  the resume does not show, put it in "gaps" instead of writing it in.
- Keep every number in a bullet exactly as written. Do not invent new ones.
- Keep each rewritten bullet within about 20% of its original length.
- Keep the LaTeX markup style: \m{...} is bold. Write & % $ # as \& \% \$ \#.
- Use the job description's vocabulary where it truthfully matches the resume.

Return ONLY one JSON object, no prose, with these keys:
{
  "title": "headline under the name, at most 8 words, plain text",
  "summary": "4 plain-text sentences, about as long as the current summary, no metrics, aimed at this job",
  "skills_order": ["exact skill row names, most relevant first"],
  "bullets": {"B7": "rewritten bullet text (LaTeX)", "...": "..."},
  "bullet_order": {"J2": ["B9", "B7", "B8"], "...": []},
  "gaps": ["job requirements the resume does not show"]
}
Rewrite at most 12 bullets, only where it clearly helps. Omit keys you do not change."""


# ---------------------------------------------------------------- flattening
TOKEN = re.compile(r"\\(if[a-zA-Z]*|else|fi)(?![a-zA-Z])")


def resolve_conditionals(body: str, teaching: bool) -> str:
    """Resolve \\ifteaching branches; keep any other \\if...\\fi verbatim."""
    out, stack, pos = [], [], 0

    def emitting():
        return stack[-1]["emit"] if stack else True

    for m in TOKEN.finditer(body):
        if emitting():
            out.append(body[pos:m.start()])
        tok, end = m.group(1), m.end()
        is_teaching_tok = tok == "ifteaching" or (tok in ("else", "fi") and stack and stack[-1]["kind"] == "t")
        if tok == "ifteaching":
            stack.append({"kind": "t", "parent": emitting(), "emit": emitting() and teaching})
        elif tok.startswith("if"):
            if emitting():
                out.append(m.group(0))
            stack.append({"kind": "o", "parent": emitting(), "emit": emitting()})
        elif tok == "else":
            frame = stack[-1]
            if frame["kind"] == "t":
                frame["emit"] = frame["parent"] and not teaching
            elif emitting():
                out.append(m.group(0))
        else:  # fi
            frame = stack.pop()
            if frame["kind"] == "o" and frame["parent"]:
                out.append(m.group(0))
        # TeX swallows one space after a control word
        if is_teaching_tok and end < len(body) and body[end] == " ":
            end += 1
        pos = end
    out.append(body[pos:])
    return "".join(out)


def read_group(s: str, i: int):
    """Return (content, index_after) for the brace group starting at s[i] == '{'."""
    assert s[i] == "{", s[i:i + 20]
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError("unbalanced braces")


def expand_auto(body: str, teaching: bool) -> str:
    out, pos = [], 0
    while True:
        i = body.find(r"\auto{", pos)
        if i < 0:
            out.append(body[pos:])
            return "".join(out)
        out.append(body[pos:i])
        a, j = read_group(body, i + 5)
        b, j = read_group(body, j)
        c, j = read_group(body, j)
        out.append(c if teaching else rf"\textbf{{{a}}} {b}")
        pos = j


def flatten(tex: str, teaching: bool):
    head, body = tex.split(r"\begin{document}", 1)
    body = resolve_conditionals(expand_auto(body, teaching), teaching)
    return head + r"\begin{document}", body


# ------------------------------------------------------------------ parsing
def plain(latex: str) -> str:
    t = re.sub(r"\\(m|textbf|textit|emph|nolinkurl)\{", "{", latex)
    t = re.sub(r"\\link\{[^}]*\}", "", t)
    t = re.sub(r"\\'\{?([aeiouAEIOU])\}?", lambda m: m.group(1).translate(str.maketrans("aeiouAEIOU", "áéíóúÁÉÍÓÚ")), t)
    t = re.sub(r"\\~\{?n\}?", "ñ", t)
    t = t.replace("\\ ", " ")
    t = t.replace("{", "").replace("}", "")
    t = re.sub(r"\\([&%$#_])", r"\1", t)
    t = t.replace(r"\ $\cdot$\ ", " | ").replace("$\\cdot$", "|").replace("--", "-")
    return re.sub(r"\s+", " ", t).strip()


def sections(body: str):
    """Yield (name, start, end) for every \\sect in the body."""
    marks = [(m.start(), m) for m in re.finditer(r"\\sect(\[[^\]]*\])?\{", body)]
    for k, (start, m) in enumerate(marks):
        name, _ = read_group(body, m.end() - 1)
        end = marks[k + 1][0] if k + 1 < len(marks) else len(body)
        yield plain(name), start, end


def parse(body: str):
    units = {"jobs": [], "bullets": {}, "skills": []}
    t = re.search(r"(\{\\normalsize\\bfseries\s*)(.*?)(\}\\\\\[3pt\])", body)
    units["title"] = t.group(2) if t else None
    s = re.search(r"\\sect\{Summary\}\n(.*?)\n\s*(?:\n|%)", body, re.S)
    units["summary"] = s.group(1).strip() if s else None
    for m in re.finditer(r"^\\skill\{", body, re.M):
        name, _ = read_group(body, m.end() - 1)
        units["skills"].append(name)
    b = 0
    for name, start, end in sections(body):
        if name not in ("Experience", "Teaching Experience", "Projects"):
            continue
        chunk = body[start:end]
        for jm in re.finditer(r"\\job\{", chunk):
            g1, k = read_group(chunk, jm.end() - 1)
            g2, k = read_group(chunk, k)
            nxt = re.search(r"\\job\{|\\sect", chunk[k:])
            stop = k + nxt.start() if nxt else len(chunk)
            items = re.findall(r"^\\item (.+)$", chunk[k:stop], re.M)
            jid = f"J{len(units['jobs']) + 1}"
            ids = []
            for it in items:
                b += 1
                bid = f"B{b}"
                units["bullets"][bid] = it
                ids.append(bid)
            units["jobs"].append({"id": jid, "header": plain(f"{g1} | {g2}"), "bullets": ids})
    return units


# --------------------------------------------------------------- LLM call
def litellm_key() -> str:
    key = os.environ.get("LITELLM_API_KEY", "")
    if key:
        return key
    cfg = Path(os.environ.get("LITELLM_CONFIG", "~/litellm/config.yaml")).expanduser()
    if cfg.exists():
        m = re.search(r"master_key:\s*[\"']?([^\s\"']+)", cfg.read_text())
        if m:
            return m.group(1)
    return ""


def call_llm(prompt: str, base: str, model: str) -> str:
    url = base.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }
    headers = {"Content-Type": "application/json"}
    key = litellm_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    for attempt in (1, 2):
        req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
        try:
            with urllib.request.urlopen(req, timeout=int(os.environ.get("TAILOR_TIMEOUT", "900"))) as r:
                return json.load(r)["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if attempt == 1 and e.code in (400, 422) and "response_format" in payload:
                payload.pop("response_format")  # backend without JSON mode
                continue
            sys.exit(f"LLM request failed: HTTP {e.code}: {detail}")
        except urllib.error.URLError as e:
            sys.exit(f"Cannot reach LiteLLM at {base} ({e.reason}).\n"
                     f"Start it with:  litellm --config ~/litellm/config.yaml --port 4000\n"
                     f"or set LITELLM_BASE_URL to a running proxy.")
    sys.exit("LLM request failed")


def parse_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j < 0:
        raise ValueError("no JSON object in model output")
    return json.loads(text[i:j + 1])


# --------------------------------------------------------------- validation
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers(s: str):
    return {n.replace(",", "").rstrip(".") for n in NUM.findall(s)}


def escape_plain(s: str) -> str:
    s = re.sub(r"\*\*|__", "", s)
    s = re.sub(r"\\([&%$#_])", r"\1", s).replace("\\", "")
    for ch in "&%$#_":
        s = s.replace(ch, "\\" + ch)
    return re.sub(r"\s+", " ", s).strip()


def check_bullet(new: str, old: str):
    """Return None if acceptable, else the reason it was rejected."""
    if not new or not isinstance(new, str):
        return "empty"
    extra = numbers(new) - numbers(old)
    if extra:
        return f"new numbers {sorted(extra)}"
    allowed = set(re.findall(r"\\([a-zA-Z]+)", old)) | {"m", "textbf", "textit"}
    bad = set(re.findall(r"\\([a-zA-Z]+)", new)) - allowed
    if bad:
        return f"new LaTeX commands {sorted(bad)}"
    if re.search(r"(?<!\\)[&%#]", new):
        return "unescaped & % or #"
    if new.count("{") != new.count("}"):
        return "unbalanced braces"
    if len(re.findall(r"(?<!\\)\$", new)) != len(re.findall(r"(?<!\\)\$", old)):
        return "math $ changed"
    if not 0.5 <= len(new) / max(len(old), 1) <= 1.6:
        return "length changed too much"
    return None


def apply_edits(body: str, units: dict, edits: dict, report: list):
    if isinstance(edits.get("title"), str) and units["title"]:
        new = escape_plain(edits["title"])
        if numbers(new) <= numbers(body) and 0 < len(new) <= 90:
            body = body.replace(units["title"], new, 1)
            report.append(f"Title: {plain(new)}")
        else:
            report.append("Title: rejected (new numbers or too long), kept original")
    if isinstance(edits.get("summary"), str) and units["summary"]:
        new = escape_plain(edits["summary"])
        ratio = len(new) / max(len(units["summary"]), 1)
        if not numbers(new) <= numbers(body):
            report.append("Summary: rejected (added numbers), kept original")
        elif not 0.75 <= ratio <= 1.3:
            report.append(f"Summary: rejected ({ratio:.0%} of original length), kept original")
        else:
            body = body.replace(units["summary"], new, 1)
            report.append(f"Summary: {plain(new)}")

    order = edits.get("skills_order")
    if isinstance(order, list) and units["skills"]:
        known = {plain(n).lower(): n for n in units["skills"]}
        wanted = [known[plain(str(x)).lower()] for x in order if plain(str(x)).lower() in known]
        wanted = list(dict.fromkeys(wanted)) + [n for n in units["skills"] if n not in wanted]
        lines = {}
        for m in re.finditer(r"^\\skill\{.*$", body, re.M):
            name, _ = read_group(m.group(0), len(r"\skill"))
            lines[name] = m.group(0)
        block = [lines[n] for n in units["skills"]]
        start = body.index(block[0])
        end = body.index(block[-1]) + len(block[-1])
        if all(line in body[start:end] for line in block):
            body = body[:start] + "\n".join(lines[n] for n in wanted) + body[end:]
            report.append("Skills order: " + ", ".join(plain(n) for n in wanted))

    new_text = dict(units["bullets"])
    for bid, new in (edits.get("bullets") or {}).items():
        old = units["bullets"].get(bid)
        if old is None:
            continue
        reason = check_bullet(new, old)
        if reason:
            report.append(f"{bid}: rejected ({reason}), kept original")
        else:
            new_text[bid] = new.strip()
            report.append(f"{bid}: {plain(new)}")

    orders = edits.get("bullet_order") or {}
    for job in units["jobs"]:
        ids = job["bullets"]
        want = orders.get(job["id"])
        if not (isinstance(want, list) and sorted(want) == sorted(ids)):
            want = ids
        if want != ids:
            report.append(f"{job['id']} ({job['header']}): bullets reordered {', '.join(want)}")
        old_block = "\n".join(r"\item " + units["bullets"][b] for b in ids)
        new_block = "\n".join(r"\item " + new_text[b] for b in want)
        if old_block in body:
            body = body.replace(old_block, new_block, 1)
        else:  # bullets not contiguous: replace one by one in place
            for b in ids:
                body = body.replace(r"\item " + units["bullets"][b], r"\item " + new_text[b], 1)
    return body


# -------------------------------------------------------------------- build
def compile_pdf(tex_path: Path) -> bool:
    for _ in (1, 2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                           cwd=tex_path.parent, capture_output=True, text=True)
        if r.returncode != 0:
            return False
    return True


def pages(pdf: Path) -> str:
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    m = re.search(r"Pages:\s+(\d+)", r.stdout)
    return m.group(1) if m else "?"


def check_proxy(base: str):
    """Fail fast, before the user pastes anything, if the proxy is down."""
    req = urllib.request.Request(base.rstrip("/") + "/v1/models")
    key = litellm_key()
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        urllib.request.urlopen(req, timeout=5).close()
    except urllib.error.HTTPError:
        pass  # reachable; auth or route problems surface on the real call
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Cannot reach LiteLLM at {base} ({getattr(e, 'reason', e)}).\n"
                 f"Start it in another terminal with:  litellm --config ~/litellm/config.yaml --port 4000\n"
                 f"or set LITELLM_BASE_URL to a running proxy.")


def read_pasted() -> str:
    """Read a pasted job description from the terminal.

    Canonical terminal input on macOS drops pasted lines over 1024 bytes, so
    read in non-canonical mode and stop on Ctrl-D or a line containing END.
    """
    if not sys.stdin.isatty():
        return sys.stdin.read()
    import termios
    print("\nPaste the job description, then press Ctrl-D (or type END on its own line).")
    print("Tip: press Ctrl-D right away to use the text already in your clipboard.\n", flush=True)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] &= ~termios.ICANON
    new[6][termios.VMIN], new[6][termios.VTIME] = 1, 0
    buf = b""
    try:
        termios.tcsetattr(fd, termios.TCSANOW, new)
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            if b"\x04" in chunk:
                buf += chunk.split(b"\x04", 1)[0]
                break
            buf += chunk
            lines = buf.replace(b"\r", b"\n").split(b"\n")
            if len(lines) >= 2 and lines[-1] == b"" and lines[-2].strip() == b"END":
                buf = b"\n".join(lines[:-2])
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    print()
    out = []
    for ch in buf.decode(errors="replace").replace("\r", "\n"):
        if ch in "\x7f\x08":
            if out:
                out.pop()
        else:
            out.append(ch)
    text = "".join(out)
    if not text.strip():
        clip = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout if shutil.which("pbpaste") else ""
        if clip.strip():
            print(f"Using the clipboard ({len(clip.split())} words).")
            text = clip
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jd", help="job description file, or - to paste/pipe it")
    ap.add_argument("kind", choices=["industry", "teaching"])
    ap.add_argument("--src", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()

    base = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
    model = os.environ.get("LITELLM_MODEL", "qwen3")
    check_proxy(base)

    jd = read_pasted() if a.jd == "-" else Path(a.jd).read_text()
    if len(jd.strip()) < 50:
        sys.exit("Job description is empty or too short.")
    teaching = a.kind == "teaching"
    head, body = flatten(Path(a.src).read_text(), teaching)
    units = parse(body)

    listing = [f"TITLE: {plain(units['title'] or '')}",
               f"SUMMARY: {plain(units['summary'] or '')}",
               "SKILL ROWS: " + " | ".join(plain(n) for n in units["skills"]), "", "BULLETS:"]
    for job in units["jobs"]:
        listing.append(f"{job['id']}: {job['header']}")
        listing += [f"  {b}: {units['bullets'][b]}" for b in job["bullets"]]
    prompt = (f"Resume version: {a.kind}.\n\nJOB DESCRIPTION:\n{jd.strip()}\n\n"
              f"RESUME:\n" + "\n".join(listing) + "\n\nReturn the JSON object now. /no_think")

    print(f"Tailoring the {a.kind} resume with {model} (this can take a minute) ...", flush=True)
    raw = call_llm(prompt, base, model)

    suffix = "Teaching" if teaching else "ind"
    work = ROOT / "resumes" / "tailored"
    work.mkdir(parents=True, exist_ok=True)
    (work / f"job_description_{suffix}.txt").write_text(jd.strip() + "\n")
    (work / f"llm_response_{suffix}.txt").write_text(raw)
    try:
        edits = parse_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        sys.exit(f"Model did not return valid JSON ({e}). Raw output: {work / f'llm_response_{suffix}.txt'}")

    report = []
    new_body = apply_edits(body, units, edits, report)
    stem = f"{NAME} - Resume-{a.tag}_{suffix}_tay"
    tex = work / f"{stem}.tex"
    tex.write_text(head + new_body)
    if not compile_pdf(tex):
        report.append("LaTeX failed with the model's bullet edits; rebuilt with title, summary and skill order only.")
        safe = dict(edits, bullets={}, bullet_order={})
        tex.write_text(head + apply_edits(body, units, safe, []))
        if not compile_pdf(tex):
            sys.exit(f"LaTeX failed; see {tex.with_suffix('.log')}")
    for ext in (".aux", ".log", ".out"):
        tex.with_suffix(ext).unlink(missing_ok=True)
    pdf = ROOT / "resumes" / f"{stem}.pdf"
    tex.with_suffix(".pdf").replace(pdf)

    gaps = [str(g) for g in edits.get("gaps") or []]
    lines = [f"# Tailored resume ({a.kind})", "", f"PDF: resumes/{pdf.name} ({pages(pdf)} pages)", "",
             "## Changes", *([f"- {r}" for r in report] or ["- none"]), "",
             "## Gaps (in the job description, not in your resume; not added)", *([f"- {g}" for g in gaps] or ["- none"])]
    (work / f"report_{suffix}.md").write_text("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))
    print(f"\nTailored PDF: {pdf}")


if __name__ == "__main__":
    main()
