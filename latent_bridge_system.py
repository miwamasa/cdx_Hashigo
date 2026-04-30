"""Latent bridge system for Chinese-Japanese readable interlingua.

This module is intentionally independent from cjp_converter.py.  It models CJP
generation as an inference pipeline:

    observed Japanese/Chinese text -> semantic graph -> bridge lexicon -> surface

The implementation is rule-backed, but the boundaries mirror the theoretical
system in reference/system_design.md so that learned encoders/decoders can later
replace each stage without changing the public interface.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Literal


Language = Literal["ja", "zh", "mixed", "unknown"]


@dataclass(frozen=True)
class Observation:
    """Observed language fragment before bridge inference."""

    text: str
    language: Language


@dataclass(frozen=True)
class Entity:
    """Language-neutral participant or concept."""

    id: str
    concept: str
    text: str | None = None
    attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Event:
    """A small semantic frame recovered from an observation."""

    predicate: str
    agent: str | None = None
    patient: str | None = None
    location: str | None = None
    target: str | None = None
    polarity: Literal["positive", "negative"] = "positive"
    modality: str | None = None


@dataclass(frozen=True)
class SemanticGraph:
    """Readable interlingua latent layer."""

    entities: tuple[Entity, ...] = ()
    events: tuple[Event, ...] = ()
    relations: tuple[dict[str, str], ...] = ()


@dataclass(frozen=True)
class BridgeToken:
    """Token selected for the bridge lexicon layer."""

    role: str
    surface: str
    concept: str | None = None


@dataclass(frozen=True)
class BridgeSentence:
    """Surface-ready bridge sentence."""

    tokens: tuple[BridgeToken, ...]
    score: float = 1.0
    source: str = "rule"

    def render(self) -> str:
        text = " ".join(token.surface for token in self.tokens if token.surface)
        text = re.sub(r"\s+([,.])", r"\1", text)
        return f"{text}。" if text else ""


@dataclass(frozen=True)
class BridgeCandidate:
    """Full posterior-style candidate for p(B | observation)."""

    observation: Observation
    graph: SemanticGraph
    sentences: tuple[BridgeSentence, ...]
    score: float
    trace: tuple[str, ...] = ()

    def render(self) -> str:
        return "\n".join(sentence.render() for sentence in self.sentences if sentence.render())

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


@dataclass(frozen=True)
class FrameRule:
    """Language-specific inverse channel rule."""

    name: str
    languages: tuple[Language, ...]
    pattern: re.Pattern[str]
    build: Callable[[re.Match[str]], Event | Iterable[Event]]
    score: float


PRONOUNS = {
    "私": "speaker",
    "わたし": "speaker",
    "僕": "speaker",
    "ぼく": "speaker",
    "俺": "speaker",
    "おれ": "speaker",
    "我": "speaker",
    "あなた": "addressee",
    "君": "addressee",
    "你": "addressee",
    "彼": "third_male",
    "他": "third_male",
    "彼女": "third_female",
    "她": "third_female",
}

BRIDGE_ENTITY = {
    "speaker": "我",
    "addressee": "你",
    "third_male": "他",
    "third_female": "她",
}

LEXICON = {
    "live": "live",
    "want": "want",
    "study": "study",
    "know": "know",
    "like": "like",
    "read": "read",
    "speak": "speak",
    "write": "write",
    "think": "think",
    "be": "is",
    "can": "can",
    "cannot": "cannot",
    "same": "same",
    "different": "different",
    "difficult": "difficult",
    "convenient": "便利",
    "friend": "友",
    "language_ja": "日本語",
    "language_zh": "中国語",
    "pronunciation": "発音",
    "kanji": "漢字",
    "conversation": "会話",
    "text_exchange": "文字交流",
    "exchange": "交流",
}

NOUNS = {
    "中国語": "中国語",
    "中文": "中国語",
    "日语": "日本語",
    "日本語": "日本語",
    "中国人の友達": "中国友",
    "中国朋友": "中国友",
    "日本朋友": "日本友",
    "日本人の友達": "日本友",
    "漢字": "漢字",
    "发音": "発音",
    "発音": "発音",
    "会話": "会話",
    "对话": "会話",
    "交流": "交流",
}

FALSE_FRIENDS = {
    "手紙": "letter",
    "勉強": "study",
    "汽車": "train",
    "愛人": "lover",
    "娘": "daughter",
    "丈夫": "strong_or_husband",
    "経理": "accounting_or_management",
}


def normalize_subject(text: str | None) -> str:
    if not text:
        return "speaker"
    return PRONOUNS.get(text.strip(), text.strip())


def normalize_noun(text: str | None) -> str | None:
    if text is None:
        return None
    value = text.strip()
    value = re.sub(r"^(そして|それで|また|でも|しかし|但|但是|还有|然后|而且|,|、)+", "", value)
    value = re.sub(r"^(は|が|を|に|で|と|の)+", "", value)
    value = re.sub(r"(です|ます|だ|了|的|です。?)$", "", value)
    for src, dst in NOUNS.items():
        value = value.replace(src, dst)
    for src, dst in FALSE_FRIENDS.items():
        value = value.replace(src, dst)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def detect_language(text: str) -> Language:
    has_kana = bool(re.search(r"[\u3040-\u30ff]", text))
    has_cjk = bool(re.search(r"[\u4e00-\u9fff]", text))
    has_zh_markers = bool(re.search(r"(我|你|他|她|在|想|喜欢|可以|不能|因为|所以|如果|但是)", text))
    if has_kana and has_zh_markers:
        return "mixed"
    if has_kana:
        return "ja"
    if has_cjk and has_zh_markers:
        return "zh"
    if has_cjk:
        return "mixed"
    return "unknown"


def split_observations(text: str) -> tuple[str, ...]:
    cleaned = text.replace("\n", " ")
    cleaned = re.sub(r"(住んでいて、|住んでいて,|住んでいて)", "住んでいる。", cleaned)
    cleaned = re.sub(r"(していて、|していて,|していて)", "している。", cleaned)
    parts = re.split(r"[。！？!?；;]", cleaned)
    return tuple(part.strip() for part in parts if part.strip())


def event(predicate: str, **kwargs: str | None) -> Event:
    return Event(predicate=predicate, **kwargs)


FRAME_RULES = (
    FrameRule(
        "ja-live",
        ("ja", "mixed"),
        re.compile(r"(?:(.+?)は)?(.+?)(?:に|で)住(?:んでいる|んでいます|んでる|む|みます|んで)?"),
        lambda m: event("live", agent=normalize_subject(m.group(1)), location=normalize_noun(m.group(2))),
        0.92,
    ),
    FrameRule(
        "zh-live",
        ("zh", "mixed"),
        re.compile(r"(?:(我|你|他|她))?在(.+?)(?:生活|住)"),
        lambda m: event("live", agent=normalize_subject(m.group(1)), location=normalize_noun(m.group(2))),
        0.92,
    ),
    FrameRule(
        "ja-want-noun",
        ("ja", "mixed"),
        re.compile(r"(?:(.+?)は)?(.+?)(?:が|を)?ほしい"),
        lambda m: event("want", agent=normalize_subject(m.group(1)), patient=normalize_noun(m.group(2))),
        0.88,
    ),
    FrameRule(
        "zh-want-noun",
        ("zh", "mixed"),
        re.compile(r"(?:(我|你|他|她))?想(?:要|认识)?(.+)"),
        lambda m: event("want", agent=normalize_subject(m.group(1)), patient=normalize_noun(m.group(2))),
        0.86,
    ),
    FrameRule(
        "ja-want-study",
        ("ja", "mixed"),
        re.compile(r"(?:(.+?)は)?(.+?)を勉強し?たい"),
        lambda m: event(
            "study",
            agent=normalize_subject(m.group(1)),
            patient=normalize_noun(m.group(2)),
            modality="want",
        ),
        0.83,
    ),
    FrameRule(
        "zh-study",
        ("zh", "mixed"),
        re.compile(r"(?:(我|你|他|她))?(?:在)?(?:学习|學習)(.+)"),
        lambda m: event("study", agent=normalize_subject(m.group(1)), patient=normalize_noun(m.group(2))),
        0.83,
    ),
    FrameRule(
        "ja-like",
        ("ja", "mixed"),
        re.compile(r"(?:(.+?)は)?(.+?)が好き"),
        lambda m: event("like", agent=normalize_subject(m.group(1)), patient=normalize_noun(m.group(2))),
        0.78,
    ),
    FrameRule(
        "zh-like",
        ("zh", "mixed"),
        re.compile(r"(?:(我|你|他|她))?喜欢(.+)"),
        lambda m: event("like", agent=normalize_subject(m.group(1)), patient=normalize_noun(m.group(2))),
        0.78,
    ),
    FrameRule(
        "same-different",
        ("ja", "zh", "mixed"),
        re.compile(r"(.+?)(?:は|也|都)?(?:同じ|相同).*(?:しかし|でも|但是|但).+?(?:違う|不同)"),
        lambda m: (
            event("be", patient=normalize_noun(m.group(1)), target="same"),
            event("be", patient="発音", target="different"),
        ),
        0.7,
    ),
    FrameRule(
        "difficult",
        ("ja", "zh", "mixed"),
        re.compile(r"(.+?)(?:が|は|很|非常)?(?:難しい|难|困難|困难)"),
        lambda m: event("be", patient=normalize_noun(m.group(1)), target="difficult"),
        0.68,
    ),
    FrameRule(
        "different",
        ("ja", "zh", "mixed"),
        re.compile(r"(.+?)(?:が|は)?(?:違う|違います|不同)"),
        lambda m: event("be", patient=normalize_noun(m.group(1)), target="different"),
        0.68,
    ),
)


class SemanticParser:
    """Inverse noisy-channel parser from observation to semantic graph."""

    def parse(self, observation: Observation) -> tuple[SemanticGraph, float, tuple[str, ...]]:
        events: list[Event] = []
        trace: list[str] = []
        scores: list[float] = []
        for rule in FRAME_RULES:
            if observation.language not in rule.languages and "mixed" not in rule.languages:
                continue
            match = rule.pattern.search(observation.text)
            if not match:
                continue
            built = rule.build(match)
            if isinstance(built, Event):
                events.append(built)
            else:
                events.extend(built)
            scores.append(rule.score)
            trace.append(f"{rule.name}:{rule.score:.2f}")
            break

        if not events:
            normalized = normalize_noun(observation.text) or observation.text
            events.append(Event(predicate="say", patient=normalized))
            scores.append(0.35)
            trace.append("fallback-say:0.35")

        entities = self._entities_from_events(events)
        graph = SemanticGraph(entities=tuple(entities), events=tuple(events))
        return graph, sum(scores) / len(scores), tuple(trace)

    def _entities_from_events(self, events: Iterable[Event]) -> list[Entity]:
        seen: dict[str, Entity] = {}
        for current in events:
            for value in (current.agent, current.patient, current.location, current.target):
                if not value:
                    continue
                if value in seen or value in LEXICON:
                    continue
                seen[value] = Entity(id=value, concept=value, text=value)
        return list(seen.values())


class BridgeLexicalizer:
    """Maps semantic graph concepts to a readable CJP bridge lexicon."""

    def lexicalize(self, graph: SemanticGraph) -> tuple[BridgeSentence, ...]:
        return tuple(self._lexicalize_event(item) for item in graph.events)

    def _lexicalize_event(self, item: Event) -> BridgeSentence:
        if item.predicate == "want" and item.patient == "study":
            tokens = (
                self._entity("agent", item.agent),
                BridgeToken("predicate", "want", "want"),
                BridgeToken("object", "study", "study"),
            )
            return BridgeSentence(tokens=self._compact(tokens))

        if item.modality == "want":
            tokens = (
                self._entity("agent", item.agent),
                BridgeToken("modality", "want", "want"),
                BridgeToken("predicate", LEXICON.get(item.predicate, item.predicate), item.predicate),
                self._entity("object", item.patient),
            )
            return BridgeSentence(tokens=self._compact(tokens))

        if item.predicate == "live":
            tokens = (
                self._entity("agent", item.agent),
                BridgeToken("predicate", "live", "live"),
                BridgeToken("relation", "in", "location"),
                self._entity("location", item.location),
            )
            return BridgeSentence(tokens=self._compact(tokens))

        if item.predicate in {"want", "study", "like", "read", "speak", "write", "think"}:
            tokens = (
                self._entity("agent", item.agent),
                BridgeToken("predicate", LEXICON[item.predicate], item.predicate),
                self._entity("object", item.patient),
            )
            return BridgeSentence(tokens=self._compact(tokens))

        if item.predicate == "be":
            target = LEXICON.get(item.target or "", item.target or "")
            tokens = (
                self._entity("subject", item.patient),
                BridgeToken("copula", "is", "be"),
                BridgeToken("complement", target, item.target),
            )
            return BridgeSentence(tokens=self._compact(tokens))

        tokens = (
            self._entity("subject", item.agent),
            BridgeToken("predicate", LEXICON.get(item.predicate, item.predicate), item.predicate),
            self._entity("object", item.patient),
        )
        return BridgeSentence(tokens=self._compact(tokens), score=0.35, source="fallback")

    def _entity(self, role: str, concept: str | None) -> BridgeToken:
        if concept is None:
            return BridgeToken(role, "")
        surface = BRIDGE_ENTITY.get(concept) or LEXICON.get(concept) or normalize_noun(concept) or concept
        return BridgeToken(role, surface, concept)

    def _compact(self, tokens: Iterable[BridgeToken]) -> tuple[BridgeToken, ...]:
        return tuple(token for token in tokens if token.surface)


class LatentBridgeSystem:
    """Facade for posterior-style bridge inference."""

    def __init__(self) -> None:
        self.parser = SemanticParser()
        self.lexicalizer = BridgeLexicalizer()

    def infer(self, text: str) -> BridgeCandidate:
        observations = tuple(
            Observation(fragment, detect_language(fragment)) for fragment in split_observations(text)
        )
        graphs: list[SemanticGraph] = []
        sentences: list[BridgeSentence] = []
        scores: list[float] = []
        trace: list[str] = []

        for observation in observations:
            graph, score, local_trace = self.parser.parse(observation)
            graphs.append(graph)
            sentences.extend(self.lexicalizer.lexicalize(graph))
            scores.append(score)
            trace.extend(f"{observation.language}:{item}" for item in local_trace)

        merged_entities: dict[str, Entity] = {}
        for graph in graphs:
            for entity in graph.entities:
                merged_entities.setdefault(entity.id, entity)
        merged = SemanticGraph(
            entities=tuple(merged_entities.values()),
            events=tuple(item for graph in graphs for item in graph.events),
        )
        language = detect_language(text)
        observation = Observation(text=text, language=language)
        score = sum(scores) / len(scores) if scores else 0.0
        return BridgeCandidate(
            observation=observation,
            graph=merged,
            sentences=tuple(sentences),
            score=score,
            trace=tuple(trace),
        )


def infer_bridge(text: str) -> str:
    """Convenience API returning the surface bridge notation only."""

    return LatentBridgeSystem().infer(text).render()


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer latent CJP bridge representation")
    parser.add_argument("text", help="Japanese/Chinese observation")
    parser.add_argument("--json", action="store_true", help="print all inferred layers")
    args = parser.parse_args()

    candidate = LatentBridgeSystem().infer(args.text)
    if args.json:
        print(candidate.to_json())
    else:
        print(candidate.render())


if __name__ == "__main__":
    main()
