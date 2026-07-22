from __future__ import annotations
import glob, os, re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Binding:
    kind: str
    modifiers: str
    key: str
    dispatcher: str
    argument: str
    source: str
    line: int
    comment: str
    @property
    def shortcut(self) -> str:
        return " + ".join(x.strip().replace("$mainMod", "SUPER") for x in (self.modifiers, self.key) if x.strip())
    @property
    def identity(self) -> tuple[str, str, str]:
        return self.kind, self.modifiers.strip().lower(), self.key.strip().lower()

BIND_TYPES={"bind", "bindm", "bindl", "bindel", "bindr", "binde", "bindle"}

def expand(value: str) -> str:
    return os.path.expandvars(os.path.expanduser(value.strip().strip('"')))

def config_files(entry: Path, visited: set[Path] | None=None) -> list[Path]:
    visited=visited or set(); entry=entry.expanduser().resolve()
    if entry in visited or not entry.is_file(): return []
    visited.add(entry); files=[entry]
    try: lines=entry.read_text(errors="replace").splitlines()
    except OSError: return files
    for line in lines:
        clean=line.split("#", 1)[0].strip()
        if not clean.startswith("source") or "=" not in clean: continue
        pattern=expand(clean.split("=", 1)[1])
        if not Path(pattern).is_absolute(): pattern=str(entry.parent / pattern)
        for child in sorted(glob.glob(pattern)): files.extend(config_files(Path(child), visited))
    return files

def category(dispatcher: str, argument: str) -> str:
    text=(dispatcher+" "+argument).lower()
    if any(word in text for word in ("workspace", "movetoworkspace", "togglespecial")): return "Workspaces"
    if any(word in text for word in ("focus", "move", "fullscreen", "killactive", "togglefloating", "pin")): return "Windows"
    if any(word in text for word in ("volume", "brightness", "playerctl", "audio", "mute")): return "Media"
    if any(word in text for word in ("exec", "exit", "reload", "lock", "suspend", "poweroff")): return "System"
    return "Other"

def parse(entry: str | Path) -> list[Binding]:
    result=[]
    for path in config_files(Path(entry)):
        for number, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
            code, _, comment=raw.partition("#"); code=code.strip()
            if "=" not in code: continue
            name, value=(part.strip() for part in code.split("=", 1))
            if name not in BIND_TYPES: continue
            fields=[part.strip() for part in value.split(",")]
            if len(fields)<3: continue
            modifiers, key, dispatcher=fields[:3]
            argument=",".join(fields[3:]).strip()
            result.append(Binding(name, modifiers, key, dispatcher, argument, str(path), number, comment.strip()))
    return result
