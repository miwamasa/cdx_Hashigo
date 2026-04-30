# CJP Converter MVP (+ Theory Track)

`reference/*.md` の仕様に基づいた、中日ピジン(CJP)変換器です。  
実装は **並列2系統** です。

- `rule` エンジン: 実用重視のルール変換
- `theoretical` エンジン: 意味骨格(JSON) + CJP + denoise trace を同時出力

## 使い方

### 1) ルール変換（通常）

```bash
python cjp_converter.py "私は日本に住んでいます。中国語を勉強したいです。でも発音が違う。" --engine rule
```

### 2) 理論版（並列）

```bash
python cjp_converter.py "我在大阪生活。我想认识日本朋友。" --engine theoretical
```

## 実装内容

- 文分割（句点ベース）
- 日本語/中国語の簡易パターン変換
- 機能語の英語化（and / but / so / if / same / different / because）
- 代名詞正規化（私→我, あなた→你）
- false friends の回避（手紙→letter など）
- スタイルモード（basic / meme / clear）
- 理論版出力:
  - semantic frame
  - CJP surface
  - edit-based denoise trace（拡散風の編集ログ）

## 出力イメージ（theoretical）

```json
{
  "sentences": [
    {
      "semantic_frame": {
        "type": "event",
        "predicate": "live",
        "agent": "我",
        "location": "大阪"
      },
      "cjp": "我 live in 大阪",
      "denoise_trace": [
        {"step": 1, "op": "normalize_lexicon", "value": "我 live in 大阪"},
        {"step": 2, "op": "remove_language_specific_markers", "value": "我 live in 大阪"}
      ]
    }
  ],
  "mode": "basic",
  "engine": "theoretical"
}
```
