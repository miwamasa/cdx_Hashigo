# CJP Converter MVP

`reference/*.md` の仕様に基づいた、ルールベースの中日ピジン(CJP)変換器です。

## 実装

このリポジトリには、性格の異なる2つの実装があります。

- `cjp_converter.py`: 既存の軽量な表層ルール変換器
- `latent_bridge_system.py`: `reference/system_design.md` の理論に沿った、独立した潜在ブリッジ推定システム

`latent_bridge_system.py` は、直接の文字列置換ではなく、次の3層を明示します。

```text
観測文 -> 意味グラフ -> ブリッジ語彙 -> CJP表層文
```

設計メモは `reference/latent_bridge_architecture.md` にあります。

## 使い方

```bash
python cjp_converter.py "私は日本に住んでいます。中国語を勉強したいです。でも発音が違う。"
```

潜在ブリッジ推定システム:

```bash
python latent_bridge_system.py "私は大阪に住んでいて、中国人の友達がほしいです。"
```

出力:

```text
我 live in 大阪。
我 want 中国友。
```

中間層も見る場合:

```bash
python latent_bridge_system.py "我在大阪生活。我想认识日本朋友。" --json
```

## 実装内容

- 文分割（句点ベース）
- 日本語/中国語の簡易パターン変換
- 機能語の英語化（and / but / so / if / same / different）
- 代名詞正規化（私→我, あなた→你）
- false friends の回避（手紙→letter など）
- スタイルモード（basic / meme / clear）

## 例

入力:

> 私は日本に住んでいます。中国語を勉強したいです。でも発音が違う。

出力:

> 我 live in 日本。
> 我 want study 中国語。
> but 発音 different。
