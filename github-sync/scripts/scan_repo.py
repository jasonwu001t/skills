#!/usr/bin/env python3
"""github-sync pre-push scanner.

Scans every git-tracked file in a repo for secrets and personal information
before it can be pushed to a (public) GitHub remote. This is a safety net, not
a guarantee — treat any finding as "stop and check", and prefer removing
sensitive data over allowlisting it.

Exit codes:
  0  clean (or every finding suppressed by the allowlist)
  2  one or more findings — caller must NOT push
  1  usage / internal error

Usage: scan_repo.py <repo-path>
Allowlist (optional, per-user, gitignored): <skill-dir>/secret-scan-allow.txt
  One regex per line; a finding is suppressed if the regex matches either the
  matched text or "relpath:lineno". Lines starting with # are comments.
"""
import os
import re
import subprocess
import sys

SECRET_PATTERNS = [
    ("private-key-block",
     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws-access-key-id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("aws-secret-access-key",
     re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("gcp-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("github-token",
     re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b"
                r"|\bgithub_pat_[A-Za-z0-9_]{22,}")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("stripe-secret-key", re.compile(r"\b(?:sk|rk)_live_[0-9a-zA-Z]{20,}\b")),
    ("ai-provider-key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}\b")),
    ("google-oauth-secret", re.compile(r"\bGOCSPX-[A-Za-z0-9_\-]{20,}\b")),
    ("jwt",
     re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")),
    ("secret-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret(?:[_-]?key)?|access[_-]?token|"
        r"auth[_-]?token|client[_-]?secret|private[_-]?key|passwd|password|pwd)"
        r"\b\s*[:=]\s*['\"]?([^\s'\"]{6,})")),
]

PII_PATTERNS = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("phone",
     re.compile(r"(?<!\d)(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")),
    ("street-address", re.compile(
        r"(?i)\b\d{1,6}\s+(?:[A-Za-z0-9.]+\s){1,4}"
        r"(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|"
        r"court|ct|way|place|pl|terrace|ter|circle|cir)\b\.?")),
]

# Obvious non-secrets: docs/templates/placeholders. Keeps the scanner from
# crying wolf on example config and instructional text.
PLACEHOLDER = re.compile(
    r"(?i)(example\.(?:com|org|net)|\byour[_-]|<[^>]{1,40}>|\$\{[^}]+\}|"
    r"\bx{3,}\b|placeholder|changeme|change-me|redacted|\bdummy\b|\bsample\b|"
    r"noreply@|\buser@host\b|foo@bar|\bn/?a\b|insert[_-]?your)")

MAX_BYTES = 2_000_000


def git_tracked_files(repo):
    out = subprocess.run(["git", "-C", repo, "ls-files", "-z"],
                          capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("scan: '%s' is not a git repo (%s)" % (repo, out.stderr.strip()))
    return [p for p in out.stdout.split("\0") if p]


def load_allowlist(skill_dir):
    path = os.path.join(skill_dir, "secret-scan-allow.txt")
    rules = []
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    rules.append(re.compile(line))
                except re.error:
                    rules.append(re.compile(re.escape(line)))
    return rules


def redact(s):
    s = s.strip()
    if len(s) <= 6:
        return s[0] + "***"
    return s[:4] + "…" + s[-2:]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: scan_repo.py <repo-path>")
    repo = os.path.realpath(sys.argv[1])
    skill_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    allow = load_allowlist(skill_dir)
    self_path = os.path.realpath(__file__)

    findings = []
    for rel in git_tracked_files(repo):
        full = os.path.join(repo, rel)
        # Never scan the scanner's own definitions or the allowlist files —
        # their pattern strings would self-flag.
        base = os.path.basename(rel)
        if os.path.realpath(full) == self_path or base.startswith("secret-scan-allow"):
            continue
        try:
            if not os.path.isfile(full) or os.path.getsize(full) > MAX_BYTES:
                continue
            raw = open(full, "rb").read()
            if b"\x00" in raw:  # binary
                continue
            text = raw.decode("utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), 1):
            for sev, groups in (("SECRET", SECRET_PATTERNS), ("PII", PII_PATTERNS)):
                for label, pat in groups:
                    for m in pat.finditer(line):
                        hit = m.group(0)
                        if PLACEHOLDER.search(line):
                            continue
                        loc = "%s:%d" % (rel, lineno)
                        if any(r.search(hit) or r.search(loc) for r in allow):
                            continue
                        findings.append((sev, label, loc, hit))

    if not findings:
        print("scan: clean — no secrets or personal info in tracked files.")
        return 0

    print("scan: BLOCKED — %d potential disclosure(s) in tracked files:\n"
          % len(findings))
    for sev, label, loc, hit in findings:
        print("  [%s] %-22s %s  →  %s" % (sev, label, loc, redact(hit)))
    print("\nThis repo may be public. Remove the data, or — only if a finding")
    print("is a confirmed false positive — add a regex to")
    print("  %s/secret-scan-allow.txt" % skill_dir)
    print("and re-run. Do not allowlist a real secret to force a push.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
