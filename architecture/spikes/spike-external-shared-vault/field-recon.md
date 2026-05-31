# Field reconnaissance: Shared external vault dir across git worktrees (Windows 11)

**Date**: 2026-05-31
**Target**: One untracked directory shared across all `git worktree`s + main tree of a repo on Windows 11, resolved via absolute config path (`~/.aisdlc/<project>/`), keyed by `git rev-parse --git-common-dir`. Comparison: junction/symlink-into-worktree vs absolute-path-config.
**Assumption under test**: (a) all worktrees reliably R/W one shared external dir via absolute path, no Windows locking/perm/long-path/encoding pitfalls; (b) `--git-common-dir` is a stable per-project key, identical-absolute across main + linked worktrees, distinct between repos; (c) shared mutable store has acceptable concurrent-write semantics for append-style markdown from sequential CLI skills.
**suggested_action**: proceed-with-caveats | **confidence**: high | **source_authority**: mixed (git official docs + multiple official-repo issues; junction/locking detail partly community)

## Findings

### `--git-common-dir` output is NOT uniformly absolute — main tree returns a RELATIVE `.git`
- In the **main worktree**, `git rev-parse --git-common-dir` returns a *relative* path (literally `.git`); in a **linked worktree** it returns an *absolute* path to `main/.git`. — git-scm.com/docs/git-rev-parse (official); git-tower.com (community).
- Fix is documented: `--git-common-dir` honors `--path-format=(absolute|relative)` (Git ≥2.31). `--absolute-git-dir` resolves `$GIT_DIR` (per-worktree private dir in a linked worktree), NOT `$GIT_COMMON_DIR` — so don't use it for the shared key.
- **Implication (b)**: the bare command is NOT identical across main + linked worktrees; the literal assumption is false for the bare form. Correctable: use `git rev-parse --path-format=absolute --git-common-dir` + canonicalize. A real footgun the design MUST handle, not a kill.

### Real tools shipped bugs from confusing worktree-dir vs common-dir
- microsoft/vscode#297786: `revParse` read ref files from the worktree-private gitdir instead of `commonPath` → ENOENT spin-loop in linked worktrees.
- anthropics/claude-code#34437 (filed 2026-03-14): proposed fix is **exactly this mechanism** — key the shared project dir off `git rev-parse --git-common-dir`. #39920 / #31546 / #28248 are the same class.
- **Implication (a)+(b)**: established, recognized prior art — a major tool converged on `--git-common-dir`-keyed shared external state for the identical problem. Warning: read the COMMON dir explicitly; never hand-join `$GIT_DIR`.

### Junction vs symlink fallback — Windows privilege/scope tradeoffs
- **Junctions**: directory-only, local-volume-only, absolute-target-only, **no admin or Developer Mode** required; stable for folder redirection.
- **Symlinks**: require admin **OR** Developer Mode (Win10 1703+); deployment footgun on locked-down corporate Windows.
- **Implication**: if absolute-path-config is rejected, **junction is the safer fallback**. But a link inside each worktree re-introduces an in-repo path that `git status`/realpath may see; absolute-path-config (vault simply not in git, tools read external path) avoids this entirely. No source calls absolute-path-config an anti-pattern.

### Concurrent-write hazards on a shared NTFS dir (assumption c) — THE caveat
- Windows `rename()` returns **EPERM if the target handle is held by another process**, breaking atomic-write-via-temp-then-rename and potentially leaving a truncated file. — npm/write-file-atomic#28, openclaw/openclaw#52093.
- **Directly analogous**: anthropics/claude-code#29153 + #28842 — concurrent writes to `.claude.json` on Windows (amplified by OneDrive/AV holding handles) produced a **corruption cascade / truncation**.
- Append: POSIX `O_APPEND` / Win32 `FILE_APPEND_DATA` (local files only) are non-clobbering; naive read-modify-write has a lost-update window.
- AV/indexer (Defender, OneDrive, Search) hold handles and degrade NTFS small-file ops.
- **Implication (c)**: "sequential developer-driven CLI skills" is load-bearing. Serialized-by-human → low risk. The risk re-enters when two worktrees' skills write the SAME vault file concurrently — moving them to a shared mutable file converts a *loud git merge-conflict* into a *silent lost-update/partial-write*. Mitigation to design + empirically test: per-file advisory lock (`portalocker`/`msvcrt.locking`) or `O_APPEND`/`FILE_APPEND_DATA` for append-logs, plus atomic-write retry-on-EPERM; keep the dir out of OneDrive/aggressive-AV scope.

### Prior-art keying — what real tools use for per-project external state
- **direnv**: abs-path **SHA1 hash + human-readable suffix**; hash present to avoid `~/foo/bar` vs `~/foo-bar` collisions.
- **pre-commit**: single global store `~/.cache/pre-commit` (XDG `PRE_COMMIT_HOME`), keyed per-repo internally.
- **None of direnv/pre-commit/asdf key on `git rev-parse --git-common-dir`** — they key on abs-path (hashed), which would give N keys for N worktrees. The git-common-dir key is the *novel* choice and is correct for the "unify worktrees" goal; claude-code#34437 is the closest precedent.
- **Implication (b)**: canonicalize before hashing (`--path-format=absolute` + realpath; Windows 8.3/case/trailing-slash). Keep the per-project subdir a BOUNDED HASH (direnv pattern), not the full mirrored abs-path. Move-sensitivity: moving the repo changes the key → "project lost its vault" (document; direnv has the same).

### Long-path (assumption a)
- Win32 `MAX_PATH` = 260 unless `longPathAware` opt-in or `\\?\` prefix.
- **Implication (a)**: `~/.aisdlc/<hash>/architecture/...` is typically *shorter* than an in-repo worktree path → this redesign likely *reduces* long-path exposure, provided the keyed subdir is a bounded hash, not a full mirrored abs-path.

## Contradictions surfaced
- **Literal assumption (b) vs git docs**: bare `--git-common-dir` is relative in main / absolute in linked → literal claim false; intent achievable via `--path-format=absolute` + canonicalize. **[This spike VERIFIED the mitigated form returns byte-identical absolute paths from main + the real slice-092 worktree on this machine.]** Flag to `/critique` as a named design requirement.
- No source labels absolute-path-config (vault not in git) an anti-pattern. The only authoritative negative is the concurrent-write/atomic-rename EPERM class — which constrains *how* you write shared files, not *whether* the architecture is valid.

## Sources
- [git-rev-parse (official)](https://git-scm.com/docs/git-rev-parse) · [kernel.org manual](https://www.kernel.org/pub/software/scm/git/docs/git-rev-parse.html) · [git-worktree (official)](https://git-scm.com/docs/git-worktree) · [git-tower rev-parse FAQ](https://www.git-tower.com/learn/git/faq/git-rev-parse)
- [microsoft/vscode#297786](https://github.com/microsoft/vscode/issues/297786) · [claude-code#34437](https://github.com/anthropics/claude-code/issues/34437) · [claude-code#39920](https://github.com/anthropics/claude-code/issues/39920)
- [claude-code#29153 (OneDrive .claude.json corruption)](https://github.com/anthropics/claude-code/issues/29153) · [claude-code#28842](https://github.com/anthropics/claude-code/issues/28842) · [npm/write-file-atomic#28](https://github.com/npm/write-file-atomic/issues/28) · [openclaw#52093](https://github.com/openclaw/openclaw/issues/52093)
- [nullprogram — O_APPEND/FILE_APPEND_DATA](https://nullprogram.com/blog/2016/08/03/) · [File locking — Wikipedia](https://en.wikipedia.org/wiki/File_locking)
- [hy2k.dev — links on Windows (junction = no admin)](https://hy2k.dev/en/blog/2025/11-23-windows-hardlink-symlink-junction/) · [Git for Windows — symbolic links](https://gitforwindows.org/symbolic-links.html)
- [direnv — cache location key](https://github.com/direnv/direnv/wiki/Customizing-cache-location) · [pre-commit — advanced (XDG store)](https://github.com/pre-commit/pre-commit.com/blob/main/sections/advanced.md)
- [Microsoft Learn — MAX_PATH / longPathAware](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)
