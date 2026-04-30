# CJP Converter MVP

`reference/*.md` の仕様に基づいた、ルールベースの中日ピジン(CJP)変換器です。

## 使い方

```bash
python cjp_converter.py "私は日本に住んでいます。中国語を勉強したいです。でも発音が違う。"
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
