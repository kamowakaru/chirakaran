# チラカラン（手動記事運用版）

**ズボラでも、ちゃんと散らからん。**

初期検証用のAPIなし版です。OpenAI APIキーは不要です。

## 普段の運用

1. ChatGPTで記事を作る
2. `content/articles/` にMarkdownファイルを追加する
3. GitHubへコミットする
4. GitHub Actionsの `Build Chirakaran` が記事ページ・一覧・カテゴリ・タグ・サムネを自動生成する

記事を書く作業だけ手動で、サイトへの組み込みは自動です。

## 記事ファイルの形式

`content/articles/_template.md` をコピーして使います。

- `title`: 記事タイトル
- `date`: YYYY-MM-DD
- `category`: tidy / clean / laundry / kitchen / bathroom / living
- `tags`: `data/tags.json` に登録済みのslug
- `description`: 検索結果にも使う短い説明
- `x_post`: 将来のX投稿用。空でもOK
- `related_products`: 将来のアフィリエイト商品検索語。空でもOK

## サムネイル

`assets/images/thumbnail-source/<category>/` に生活シーン画像を入れると、ビルド時に文字なし・高画質の写真サムネイルWebPを生成します。画像内にタイトルやロゴは焼き込みません。

## 入っているもの

- 初期記事10本
- 6カテゴリ
- 記事一覧・カテゴリ・タグ・検索
- 関連記事
- 関連商品欄の土台
- サムネ自動生成
- X自動投稿の土台（使わなければ動きません）

## 初期100記事までの方針

OpenAI APIによるCSV自動記事生成は入れていません。まずChatGPTで記事品質を固め、100記事前後を目安に検索データを確認してから半自動化へ移行する想定です。

## アフィリエイト連携（楽天 / Amazon / Yahoo!ショッピング）

記事ごとには `related_products` に商品名・検索キーワードだけを書きます。

```yaml
related_products:
  - "詰め替えそのまま シャンプー ポンプ"
  - "浴室 浮かせる収納 マグネット"
```

ショップごとのURLは `data/affiliate-shops.json` で一括管理します。初期状態では3ショップとも `enabled: false` です。

将来、楽天・Amazon・Yahoo!ショッピングのアフィリエイト設定が済んだら、該当ショップの `url_template` を設定して `enabled: true` にします。テンプレート内の `{query}` はURLエンコード済み検索語、`{query_raw}` はそのままの検索語に置換されます。

この方式なら、既存の記事Markdownを1本ずつ修正せずにショップボタンを追加・停止できます。ショップを追加したい場合も `affiliate-shops.json` に1件追加するだけです。

※ 実際のアフィリエイトURL形式・パラメータは各サービスで取得した正規のリンク仕様に合わせて設定してください。認証情報や秘密キーを記事・リポジトリへ直接書かないでください。


## v8 UI consistency
- 「このサイトについて」「記事一覧」などの上部ナビをTOPと同じものに統一
- ロゴを背景なしの緑の家アイコンに統一
- 下層ページの水色背景をTOPに合わせた淡いクリーム/黄色へ変更
