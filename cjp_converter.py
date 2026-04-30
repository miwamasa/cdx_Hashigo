import re
from dataclasses import dataclass
from typing import List

PRONOUN_MAP = {
    "私": "我", "わたし": "我", "僕": "我", "ぼく": "我", "俺": "我", "おれ": "我", "我": "我",
    "あなた": "你", "君": "你", "你": "你",
    "彼": "他", "他": "他", "她": "她", "彼女": "她",
}

JA_PATTERNS = [
    (re.compile(r"(.+?)は(.+?)に住[んみ]?で?います?"), lambda m: f"{map_subject(m.group(1))} live in {m.group(2)}"),
    (re.compile(r"(.+?)は(.+?)にいます?"), lambda m: f"{map_subject(m.group(1))} in {m.group(2)}"),
    (re.compile(r"(.+?)を勉強し?たい"), lambda m: f"我 want study {normalize_noun(m.group(1))}"),
    (re.compile(r"(.+?)がほしい"), lambda m: f"我 want {normalize_noun(m.group(1))}"),
]

ZH_PATTERNS = [
    (re.compile(r"(我|你|他|她)?在(.+?)(生活|住)"), lambda m: f"{m.group(1) or '我'} live in {m.group(2)}"),
    (re.compile(r"(我|你|他|她)?想(认识)?(.+?)"), lambda m: f"{m.group(1) or '我'} want {normalize_noun(m.group(3))}"),
]

FUNCTION_REPLACE = {
    "しかし": "but", "でも": "but", "但是": "but",
    "だから": "so", "所以": "so",
    "もし": "if", "如果": "if",
    "と": "and", "和": "and",
    "同じ": "same", "相同": "same",
    "違う": "different", "不同": "different",
}

NOUN_NORMALIZE = {
    "中国語": "中国語", "中文": "中国語", "日语": "日本語", "日本語": "日本語",
    "中国人の友達": "中国友", "中国朋友": "中国友", "日本朋友": "日本友",
}

FALSE_FRIENDS = {"手紙": "letter", "勉強": "study", "汽車": "train", "愛人": "lover", "丈夫": "strong_or_husband"}


def map_subject(s: str) -> str:
    s = s.strip()
    return PRONOUN_MAP.get(s, s)


def normalize_noun(n: str) -> str:
    n = n.strip()
    for k, v in NOUN_NORMALIZE.items():
        n = n.replace(k, v)
    for k, v in FALSE_FRIENDS.items():
        n = n.replace(k, v)
    return n


def split_sentences(text: str) -> List[str]:
    text = text.replace("\n", "")
    parts = re.split(r"[。！？!?]", text)
    return [p.strip() for p in parts if p.strip()]


def convert_sentence(sent: str) -> str:
    for pat, rep in JA_PATTERNS:
        m = pat.search(sent)
        if m:
            return rep(m)
    for pat, rep in ZH_PATTERNS:
        m = pat.search(sent)
        if m:
            return rep(m)

    out = sent
    for k, v in FUNCTION_REPLACE.items():
        out = out.replace(k, f" {v} ")
    out = normalize_noun(out)
    out = re.sub(r"\s+", " ", out).strip()
    out = out.replace("私は", "我 ").replace("我在", "我 in ")
    return out


def convert_to_cjp(text: str, mode: str = "basic") -> str:
    sentences = split_sentences(text)
    converted = [convert_sentence(s) for s in sentences]
    if mode == "meme":
        converted = [s.replace(" live in ", " in ") for s in converted]
    elif mode == "clear":
        converted = [s.replace(" difficult", " is difficult") for s in converted]
    return "\n".join(f"{s}。" for s in converted)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert Japanese/Chinese text to CJP bridge notation")
    parser.add_argument("text", help="input text")
    parser.add_argument("--mode", default="basic", choices=["basic", "meme", "clear"])
    args = parser.parse_args()
    print(convert_to_cjp(args.text, args.mode))
