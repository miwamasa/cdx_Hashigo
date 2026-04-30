# Latent Bridge System Architecture

`latent_bridge_system.py` は、既存の `cjp_converter.py` とは独立した実験的システムです。
目的は、表層的な文字列変換ではなく、`reference/system_design.md` の理論に沿って、観測文から可読インターリンガを逆推定することです。

## 基本モデル

日本語文 `J`、中国語文 `C`、ブリッジ表現 `B` について、次の生成過程を仮定します。

```text
B -> J
B -> C
```

観測された `J` または `C` から、もっとも自然な `B` を推定します。

```text
B* = argmax_B p(B | observation)
```

現在の実装は学習モデルではなくルールベースですが、各ルールには信頼度スコアと trace を持たせ、将来の noisy channel model / VAE / denoising model に置き換えやすい境界にしています。

## 3層構造

### 1. Observation

入力文を文・節単位に分け、言語を推定します。

```json
{
  "text": "私は大阪に住んでいる",
  "language": "ja"
}
```

### 2. SemanticGraph

観測文から、言語に依存しにくい意味イベントを復元します。

```json
{
  "events": [
    {
      "predicate": "live",
      "agent": "speaker",
      "location": "大阪"
    }
  ]
}
```

この層が、理論上の潜在変数にもっとも近い部分です。

### 3. BridgeLexicon / Surface

意味イベントを、日中双方から読みやすいブリッジ語彙へ写像し、CJP表層文として出力します。

```text
我 live in 大阪。
```

## 既存変換との差分

`cjp_converter.py` は、入力文字列に正規表現を直接当てて CJP 表層文へ変換します。

`latent_bridge_system.py` は、次のように中間表現を明示します。

```text
observed text
  -> Observation
  -> SemanticGraph
  -> BridgeSentence
  -> rendered CJP
```

このため、以下を個別に改善できます。

- 日本語・中国語の逆生成チャネル
- 意味役割の推定
- ブリッジ語彙選択
- 表層レンダリング
- 候補スコアリング

## 初期実装の範囲

対応している意味フレームは、まず小さく保っています。

- live
- want
- study
- like
- be same / different / difficult
- fallback say

この範囲でも、`B = semantic graph + bridge lexicon + surface bridge sentence` という設計の骨格を検証できます。
