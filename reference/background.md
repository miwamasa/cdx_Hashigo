以下では、この方式を仮に 「中日ピジン」、もう少し仕様名らしく CJP: Chinese–Japanese Pidgin-like Bridge Notation と呼びます。

目的は、自然な中国語・日本語を完全翻訳することではなく、中国語話者・日本語話者が文字上で意味を推測しやすい、漢字＋英語機能語ベースの中間表現に変換することです。

⸻

中日ピジン変換機 実装仕様案

1. 目的

1.1 目的

日本語または中国語の入力文を、以下のような中間表現に変換する。

我 live in 日本。
我 want 中国朋友。
漢字 same, but 発音 different。
English words can help 交流。

この中間表現は、次の3要素で構成される。

要素	役割
漢字語	意味の中心を担う
英語の機能語・基本動詞	文法関係を補う
最小限の固有語	必要に応じて補助する

⸻

2. 基本方針

2.1 翻訳ではなく「可読な中間表現」への変換

通常の翻訳では、

私は大阪に住んでいます。

を中国語にするなら、

我住在大阪。

となる。

しかし中日ピジンでは、

我 live in 大阪。

とする。

つまり、日本語にも中国語にも寄せきらず、漢字語と英語を混ぜたブリッジ表現にする。

⸻

3. 入出力仕様

3.1 入力

入力言語は以下。

入力言語	対応
日本語	対応
簡体字中国語	対応
繁体字中国語	対応予定
日中混在文	対応可能
英語混在文	そのまま保持または正規化

3.2 出力

出力は、1文または複数文からなる中日ピジン文。

例：

入力：

私は日本でAIとデータサイエンスを研究しています。中国の研究者とも交流したいです。

出力：

我 study AI and data science in 日本。
我 want 交流 with 中国研究者。

⸻

4. 中日ピジンの設計原則

4.1 内容語は漢字を優先する

名詞・動詞語幹・形容詞語幹・抽象概念は、可能な限り漢字で表す。

日本語	中国語	中日ピジン
研究する	研究	study / 研究
交流する	交流	交流
便利	方便 / 便利	便利
重要	重要	重要
友達	朋友 / 友人	友 / 朋友
言語	语言	言語 / 语言

原則として、日本語話者・中国語話者の双方に推測されやすい語を選ぶ。

⸻

4.2 文法関係は英語で表す

助詞・介詞・接続詞・副詞は、英語の基本語で置き換える。

機能	日本語	中国語	中日ピジン
並列	と	和	and
逆接	しかし	但是	but
理由	だから	所以 / 因为	so / because
条件	もし	如果	if
場所	に / で	在	in / at
方向	へ / に	到	to
起点	から	从	from
所有	の	的	of
可能	できる	能 / 可以	can
希望	したい	想 / 要	want
強調	とても	很 / 非常	very
比較	より	比	more / than
否定	ない	不 / 没	not / no

⸻

4.3 文は短く分割する

複雑な文は、意味単位で分割する。

入力：

私は中国語を勉強していますが、発音が難しいので、漢字を使った交流の方が便利だと思います。

出力：

我 study 中国語。
But 発音 difficult。
So 漢字交流 more 便利。
我 think this good。

⸻

4.4 語順は英語寄りの SVO を基本にする

中日ピジンでは、文法的な曖昧さを減らすため、基本語順を英語風にする。

Subject + Verb/Function + Object + Modifier

例：

入力	出力
私は中国の友達がほしい	我 want 中国友
私は大阪に住んでいる	我 live in 大阪
中国語の発音は難しい	中国語発音 is difficult
漢字が同じなら便利	if 漢字 same, then 便利

ただし、is は省略可能。

中国語発音 difficult。
漢字 same but 発音 different。

⸻

5. 変換パイプライン

5.1 全体構成

入力文
  ↓
言語判定
  ↓
文分割
  ↓
形態素解析・構文解析
  ↓
意味単位抽出
  ↓
中核語の漢字化
  ↓
機能語の英語化
  ↓
語順正規化
  ↓
短文化・簡略化
  ↓
中日ピジン出力

⸻

5.2 モジュール構成

モジュール	役割
LanguageDetector	日本語・中国語・混在文の判定
SentenceSplitter	文単位に分割
MorphAnalyzer	単語・品詞・語幹の抽出
DependencyAnalyzer	主語・述語・目的語・修飾語の推定
LexicalMapper	日本語・中国語語彙を中日ピジン語彙に変換
FunctionWordMapper	助詞・介詞・接続詞を英語機能語に変換
Simplifier	長文を短文に分割
WordOrderNormalizer	SVO寄りに語順変換
Renderer	表記を整えて出力

⸻

6. 変換ルール

6.1 代名詞

日本語	中国語	中日ピジン
私 / 僕 / 俺	我	我
あなた	你	你
彼	他	他
彼女	她	她 / 他
私たち	我们 / 我們	我們
彼ら	他们 / 他們	他們

日本語入力では、主語が省略されやすいので、文脈から推定する。

例：

大阪に住んでいます。

出力候補：

我 live in 大阪。

ただし、主語が不明な場合は省略してもよい。

live in 大阪。

⸻

6.2 存在・所在

入力パターン	出力
XはYにいる	X is in Y
XはYにある	X is in Y
X在Y	X is in Y
YにXがある	X exists in Y

例：

日本語：

私は日本にいます。

出力：

我 is in 日本。

より自然な中日ピジン：

我 in 日本。

中国語：

我在大阪。

出力：

我 in 大阪。

⸻

6.3 希望・欲求

入力パターン	出力
Xしたい	want X
Xがほしい	want X
想X	want X
要X	want X

例：

中国人の友達がほしい。

出力：

我 want 中国友。

我想认识日本朋友。

出力：

我 want know 日本友。

または簡略化して、

我 want 日本友。

⸻

6.4 好き・関心

入力パターン	出力
Xが好き	like X
Xに興味がある	interested in X
喜欢X	like X
对X感兴趣	interested in X

例：

私は車とバイクが好きです。

出力：

我 like 車 and 二輪車。

⸻

6.5 能力・可能

入力パターン	出力
Xできる	can X
Xできない	cannot X
可以X	can X
不能X	cannot X

例：

漢字は読めるが、中国語は話せない。

出力：

我 can read 漢字。
But 我 cannot speak 中国語。

⸻

6.6 理由・結果

入力パターン	出力
AなのでB	because A, B
AだからB	because A, so B
因为A，所以B	because A, so B
A, 所以B	A, so B

例：

発音が違うので、会話は難しい。

出力：

発音 different, so conversation difficult。

⸻

6.7 条件

入力パターン	出力
もしAならB	if A, B
AならB	if A, B
如果A，就B	if A, then B

例：

漢字の発音が同じなら、交流はもっと便利になる。

出力：

if 漢字発音 same, 交流 more 便利。

⸻

6.8 逆接

入力パターン	出力
AだがB	A, but B
AけれどB	A, but B
虽然A，但是B	A, but B
A但是B	A, but B

例：

漢字は同じだが、発音は違う。

出力：

漢字 same, but 発音 different。

⸻

6.9 比較

入力パターン	出力
AよりBの方がX	B more X than A
A比B更X	A more X than B

例：

文字の交流は音声より便利です。

出力：

文字交流 more 便利 than 音声交流。

⸻

7. 語彙マッピング仕様

7.1 共通漢字語辞書

中日ピジンでは、語彙を次の優先順位で選ぶ。

1. 日中で意味が近い漢字語
2. 中国語側にも推測しやすい日本語漢字語
3. 日本語側にも推測しやすい中国語漢字語
4. 英語基本語
5. 原語保持

例：

概念	日本語	中国語	CJP推奨
language	言語	语言	言語 / 语言
pronunciation	発音	发音	発音 / 发音
grammar	文法	语法	文法 / 语法
friend	友達 / 友人	朋友	友 / 朋友
exchange	交流	交流	交流
convenient	便利	方便	便利
difficult	難しい	难	difficult
different	違う	不同	different
same	同じ	相同	same
understand	理解する	理解	understand / 理解
read	読む	读	read
speak	話す	说	speak
write	書く	写	write

⸻

7.2 和製漢語・中日同形異義語への注意

同じ漢字でも意味がずれる語は、そのまま使わない。

語	日本語意味	中国語意味	推奨CJP
手紙	letter	toilet paper	letter
勉強	study	reluctantly / force	study
汽車	steam train	car	train / 車
愛人	lover / mistress	spouse / lover depending context	partner / lover
娘	daughter / girl	mother / young woman in compounds	daughter / girl
丈夫	strong	husband	strong / husband
経理	accounting	manager / operation	accounting / management

実装上は、false friend 辞書を持つ。

⸻

8. 文字変換仕様

8.1 日本語入力の場合

日本語入力では、以下を行う。

ひらがな助詞 → 英語機能語
活用語尾 → 削除または英語化
漢字語 → 原則保持
カタカナ外来語 → 英語または原語保持

例：

私は大阪で中国語を勉強しています。

変換過程：

私 → 我
は → subject marker, outputなし
大阪 → 大阪
で → in
中国語 → 中国語
を → object marker, outputなし
勉強しています → study

出力：

我 study 中国語 in 大阪。

⸻

8.2 中国語入力の場合

中国語入力では、以下を行う。

我/你/他 → 原則保持
在/从/到/和/但是/因为/所以/如果 → 英語機能語
内容語 → 原則保持または日中共通漢字へ変換
簡体字 → 必要に応じて日本漢字または繁体字へ正規化

例：

我在大阪学习日语。

変換過程：

我 → 我
在 → in
大阪 → 大阪
学习 → study
日语 → 日本語

出力：

我 study 日本語 in 大阪。

⸻

8.3 漢字正規化

オプションとして、出力漢字のスタイルを選べる。

モード	説明	例
jp	日本漢字寄り	発音, 言語, 勉強
zh-cn	簡体字寄り	发音, 语言, 学习
mixed	入力に近い表記を保持	発音 / 发音
bridge	日中推測しやすさ重視	発音, 文法, 交流

推奨は bridge。

⸻

9. 出力スタイル

9.1 basic モード

最も素朴な出力。

入力：

私は日本に住んでいます。中国語は少し読めますが、話すのは難しいです。

出力：

我 live in 日本。
我 can read 中国語 little。
But speak difficult。

⸻

9.2 meme モード

SNSポスト風。文法の雑さをあえて残す。

出力：

我 in 日本。
我 can read 中国語 little。
But speak very difficult。
我 悲。

⸻

9.3 clear モード

中日双方に読みやすくするため、少し英語を増やす。

出力：

我 live in 日本。
我 can read 中国語 a little。
But speaking 中国語 is difficult for me。

⸻

9.4 kanji-heavy モード

漢字を多めに残す。

出力：

我 在 日本。
我 can read 中国語 少少。
But 発話 difficult。

⸻

10. 実装方式

10.1 ルールベース MVP

最初の実装は、ルールベースで十分可能。

構成

1. 言語判定
2. 文分割
3. 形態素解析
4. パターンマッチ
5. 辞書変換
6. 出力整形

使用候補

処理	日本語	中国語
形態素解析	SudachiPy, MeCab, GiNZA	jieba, pkuseg, HanLP
依存構造解析	GiNZA, spaCy	HanLP, spaCy Chinese
文字変換	jaconv, OpenCC	OpenCC
辞書	独自JSON/YAML	独自JSON/YAML

⸻

10.2 LLM補助方式

ルールベースで難しい部分は、LLMを使って補う。

LLMの役割

処理	LLM利用
主語補完	有効
長文分割	有効
意味単位抽出	有効
同形異義語回避	有効
文体調整	有効
低レベル形態素解析	ルールベース推奨

推奨構成

Rule-based preprocessing
  ↓
LLM semantic simplification
  ↓
Dictionary-based CJP rendering
  ↓
Validation

LLMに完全生成させるより、中間表現 JSON を作らせてからレンダリングする方が安定する。

⸻

11. 中間表現仕様

11.1 Semantic Unit JSON

入力文をいきなり中日ピジンにせず、まず意味単位に分解する。

例：

入力：

私は大阪に住んでいて、中国人の友達がほしいです。

中間表現：

{
  "sentences": [
    {
      "subject": "我",
      "predicate": "live",
      "object": null,
      "complements": [
        {
          "role": "location",
          "value": "大阪"
        }
      ]
    },
    {
      "subject": "我",
      "predicate": "want",
      "object": "中国友",
      "complements": []
    }
  ]
}

レンダリング結果：

我 live in 大阪。
我 want 中国友。

⸻

11.2 Relation Types

role	出力
location	in
source	from
destination	to
companion	with
reason	because
result	so
condition	if
contrast	but
topic	原則出力しない
object	語順で表現
possession	of

⸻

12. 変換例

12.1 日本語から

入力：

私は東京でAIを研究しています。中国の研究者とも交流したいです。

出力：

我 study AI in 東京。
我 want 交流 with 中国研究者。

⸻

入力：

日本語と中国語は漢字を共有していますが、発音と文法はかなり違います。

出力：

日本語 and 中国語 share 漢字。
But 発音 and 文法 very different。

⸻

入力：

もし漢字の読み方が同じだったら、もっと簡単に交流できるのにと思います。

出力：

If 漢字発音 same, 交流 more easy。
我 think this very good。

⸻

12.2 中国語から

入力：

我在大阪生活，我想认识日本朋友。

出力：

我 live in 大阪。
我 want know 日本友。

より自然な meme モード：

我 in 大阪。
我 want 日本友。

⸻

入力：

中文和日文有很多相同的汉字，但是语法和发音完全不同。

出力：

中国語 and 日本語 have many same 漢字。
But 文法 and 発音 completely different。

⸻

入力：

如果我们使用英语的小词，交流会更方便。

出力：

If 我們 use English small words, 交流 more 便利。

⸻

13. 実装用プロンプト仕様

LLMを使う場合のプロンプトは、次のようにする。

You are a converter from Japanese or Chinese into CJP:
Chinese-Japanese Pidgin-like Bridge Notation.
Rules:
- Preserve shared Kanji words when they are understandable to both Japanese and Chinese readers.
- Replace grammatical particles, conjunctions, auxiliaries, and relation markers with simple English words.
- Prefer short sentences.
- Use 我, 你, 他, 我們 for pronouns.
- Use English function words such as in, from, to, with, and, but, so, because, if, can, want, like, not, more, very.
- Avoid Japanese kana particles and Chinese function words where possible.
- Avoid false friends such as 手紙, 勉強, 汽車, 愛人, 丈夫.
- Output only CJP text.

日本語で指示する場合：

次の日本語または中国語を、中日ピジン風の中間表現に変換してください。
ルール:
- 意味の中心になる語は、できるだけ漢字で残す。
- 助詞、接続詞、介詞、副詞、助動詞は、英語の基本語に置き換える。
- 文は短くする。
- 主語は必要に応じて 我, 你, 他, 我們 を使う。
- in, from, to, with, and, but, so, because, if, can, want, like, not, more, very を優先する。
- 日本語の助詞や中国語の機能語はなるべく避ける。
- 日中同形異義語は避ける。
- 出力は中日ピジン文のみ。

⸻

14. 疑似コード

def convert_to_cjp(text: str, mode: str = "basic") -> str:
    lang = detect_language(text)
    sentences = split_sentences(text, lang)
    cjp_sentences = []
    for sent in sentences:
        tokens = analyze_morphology(sent, lang)
        deps = analyze_dependencies(sent, lang)
        semantic_units = extract_semantic_units(tokens, deps, lang)
        for unit in semantic_units:
            normalized = normalize_semantic_unit(unit)
            mapped = map_lexicon(normalized)
            rendered = render_cjp(mapped, mode)
            cjp_sentences.append(rendered)
    return format_output(cjp_sentences)

⸻

15. 辞書ファイル例

15.1 function_words.yaml

ja:
  は: ""
  が: ""
  を: ""
  に: "in"
  で: "in"
  へ: "to"
  から: "from"
  と: "and"
  でも: "but"
  しかし: "but"
  だから: "so"
  ので: "because"
  もし: "if"
  より: "than"
zh:
  在: "in"
  从: "from"
  到: "to"
  和: "and"
  但是: "but"
  可是: "but"
  所以: "so"
  因为: "because"
  如果: "if"
  比: "than"

15.2 predicate_map.yaml

ja:
  住む: "live"
  暮らす: "live"
  勉強する: "study"
  学ぶ: "study"
  研究する: "study"
  読む: "read"
  書く: "write"
  話す: "speak"
  好き: "like"
  欲しい: "want"
  したい: "want"
  できる: "can"
  違う: "different"
  同じ: "same"
zh:
  住: "live"
  生活: "live"
  学习: "study"
  學習: "study"
  研究: "study"
  读: "read"
  讀: "read"
  写: "write"
  寫: "write"
  说: "speak"
  說: "speak"
  喜欢: "like"
  喜歡: "like"
  想: "want"
  要: "want"
  可以: "can"
  能: "can"
  不同: "different"
  相同: "same"

15.3 false_friends.yaml

手紙:
  avoid: true
  ja_meaning: "letter"
  zh_meaning: "toilet paper"
  cjp: "letter"
勉強:
  avoid: true
  ja_meaning: "study"
  zh_meaning: "reluctantly"
  cjp: "study"
汽車:
  avoid: true
  ja_meaning: "steam train"
  zh_meaning: "car"
  cjp: "train_or_car"
愛人:
  avoid: true
  cjp: "lover_or_partner"
丈夫:
  avoid: true
  cjp: "strong_or_husband"

⸻

16. 評価指標

この変換機は、通常の翻訳品質ではなく、以下で評価する。

指標	内容
日中可読性	日本語話者・中国語話者が意味を推測できるか
漢字保持率	内容語が漢字として残っているか
機能語英語化率	助詞・介詞・接続詞が英語化されているか
短文化率	長文が適切に分割されているか
誤解回避率	同形異義語を避けられているか
meme感	元ポスト風の面白さが残っているか

特に重要なのは、

完全な文法性ではなく、推測可能性

です。

⸻

17. MVPの最小仕様

最初に作るなら、ここまでで十分です。

17.1 対応入力

* 日本語の平文
* 簡体字中国語の平文
* 1〜5文程度の短文

17.2 対応変換

* 私／我 → 我
* あなた／你 → 你
* 日本語／中文／日文 → 日本語 / 中国語
* 住む／在 → live in
* 好き／喜欢 → like
* 欲しい／想要 → want
* できる／可以 → can
* しかし／但是 → but
* だから／所以 → so
* もし／如果 → if
* 同じ／相同 → same
* 違う／不同 → different
* と／和 → and

17.3 出力例

入力：

私は日本に住んでいます。中国語を勉強したいです。でも発音が難しいです。

出力：

我 live in 日本。
我 want study 中国語。
But 発音 difficult。

⸻

18. 発展仕様

将来的には、以下を追加できる。

機能	内容
双方向変換	CJPから日本語・中国語に戻す
可読性スコア	日本語話者・中国語話者別に推測しやすさを評価
漢字選択最適化	日中共通度が高い漢字語を自動選択
SNSモード	あえて雑で面白い文体にする
学習モード	CJP、元日本語、元中国語を並べる
発音注釈	必要に応じてピンイン・ふりがなを追加
false friend警告	誤解されやすい語を警告する

⸻

19. まとめ

この変換機の本質は、次のように整理できます。

日本語・中国語の文
  ↓
意味を担う漢字語を抽出
  ↓
文法を担う部分を英語の基本語に置換
  ↓
短いSVO風文に整形
  ↓
日中双方が推測しやすい文字コミュニケーションへ

中日ピジンは、自然言語として正しいというより、

漢字を意味の圧縮表現として使い、英語を文法の接着剤として使う、日中間の視覚的ブリッジ言語

と考えると実装しやすいです。