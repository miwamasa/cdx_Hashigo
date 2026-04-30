import argparse
import json
import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

PRONOUN_MAP = {
    "私": "我", "わたし": "我", "僕": "我", "ぼく": "我", "俺": "我", "おれ": "我", "我": "我",
    "あなた": "你", "君": "你", "你": "你",
    "彼": "他", "他": "他", "她": "她", "彼女": "她",
}

FUNCTION_REPLACE = {
    "しかし": "but", "でも": "but", "但是": "but", "可是": "but",
    "だから": "so", "所以": "so", "ので": "because", "因为": "because",
    "もし": "if", "如果": "if", "なら": "if",
    "と": "and", "和": "and",
    "同じ": "same", "相同": "same",
    "違う": "different", "不同": "different",
}

NOUN_NORMALIZE = {
    "中国語": "中国語", "中文": "中国語", "日语": "日本語", "日文": "日本語", "日本語": "日本語",
    "中国人の友達": "中国友", "中国朋友": "中国友", "日本朋友": "日本友",
}

FALSE_FRIENDS = {"手紙": "letter", "勉強": "study", "汽車": "train", "愛人": "lover", "丈夫": "strong_or_husband"}


@dataclass
class SemanticUnit:
    subject: str
    predicate: str
    obj: Optional[str] = None
    location: Optional[str] = None
    relation: Optional[str] = None


def map_subject(s: str) -> str:
    return PRONOUN_MAP.get(s.strip(), s.strip())


def normalize_text(text: str) -> str:
    out = text.strip()
    for k, v in NOUN_NORMALIZE.items():
        out = out.replace(k, v)
    for k, v in FALSE_FRIENDS.items():
        out = out.replace(k, v)
    return out


def split_sentences(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"[。！？!?]", text.replace("\n", "")) if p.strip()]


def extract_semantic_unit(sent: str) -> SemanticUnit:
    s = normalize_text(sent)

    m = re.search(r"(.+?)は(.+?)に住[んみ]?で?います?", s)
    if m:
        return SemanticUnit(subject=map_subject(m.group(1)), predicate="live", location=m.group(2))

    m = re.search(r"(我|你|他|她)?在(.+?)(生活|住)", s)
    if m:
        return SemanticUnit(subject=m.group(1) or "我", predicate="live", location=m.group(2))

    m = re.search(r"(.+?)を勉強し?たい", s)
    if m:
        return SemanticUnit(subject="我", predicate="want_study", obj=m.group(1))

    m = re.search(r"(.+?)がほしい", s)
    if m:
        return SemanticUnit(subject="我", predicate="want", obj=m.group(1))

    m = re.search(r"(我|你|他|她)?想(认识)?(.+?)$", s)
    if m:
        return SemanticUnit(subject=m.group(1) or "我", predicate="want", obj=m.group(3))

    # fallback: function-word normalized relation sentence
    for k, v in FUNCTION_REPLACE.items():
        if k in s:
            return SemanticUnit(subject="", predicate="raw", obj=s.replace(k, f" {v} "), relation=v)

    return SemanticUnit(subject="", predicate="raw", obj=s)


def render_basic(unit: SemanticUnit) -> str:
    if unit.predicate == "live":
        return f"{unit.subject} live in {unit.location}"
    if unit.predicate == "want_study":
        return f"{unit.subject} want study {unit.obj}"
    if unit.predicate == "want":
        return f"{unit.subject} want {unit.obj}"
    return re.sub(r"\s+", " ", (unit.obj or "").strip())


def render_theoretical(unit: SemanticUnit) -> Dict[str, object]:
    if unit.predicate == "live":
        cjp = f"{unit.subject} live in {unit.location}"
        frame = {"type": "event", "predicate": "live", "agent": unit.subject, "location": unit.location}
    elif unit.predicate == "want_study":
        cjp = f"{unit.subject} want study {unit.obj}"
        frame = {"type": "event", "predicate": "want", "agent": unit.subject, "object": {"action": "study", "target": unit.obj}}
    elif unit.predicate == "want":
        cjp = f"{unit.subject} want {unit.obj}"
        frame = {"type": "event", "predicate": "want", "agent": unit.subject, "object": unit.obj}
    else:
        cjp = re.sub(r"\s+", " ", (unit.obj or "").strip())
        frame = {"type": "raw", "surface": unit.obj}

    denoise_steps = [
        {"step": 1, "op": "normalize_lexicon", "value": cjp},
        {"step": 2, "op": "remove_language_specific_markers", "value": cjp},
    ]
    return {"semantic_frame": frame, "cjp": cjp, "denoise_trace": denoise_steps}


def convert_to_cjp(text: str, mode: str = "basic", engine: str = "rule") -> str:
    units = [extract_semantic_unit(s) for s in split_sentences(text)]
    if engine == "theoretical":
        payload = {"sentences": [render_theoretical(u) for u in units], "mode": mode, "engine": engine}
        return json.dumps(payload, ensure_ascii=False, indent=2)

    lines = [render_basic(u) for u in units]
    if mode == "meme":
        lines = [ln.replace(" live in ", " in ") for ln in lines]
    elif mode == "clear":
        lines = [ln.replace(" difficult", " is difficult") for ln in lines]
    return "\n".join(f"{ln}。" for ln in lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Japanese/Chinese text to CJP bridge notation")
    parser.add_argument("text", help="input text")
    parser.add_argument("--mode", default="basic", choices=["basic", "meme", "clear"])
    parser.add_argument("--engine", default="rule", choices=["rule", "theoretical"])
    args = parser.parse_args()
    print(convert_to_cjp(args.text, args.mode, args.engine))
