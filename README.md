# Books to Scrape 商品詳細スクレイピング

練習用ECサイト「Books to Scrape」の一覧ページから商品詳細ページへ遷移し、
各商品の **タイトル / 価格 / 通貨 / URL** を取得してCSVに出力するPythonスクリプトです。

## 機能概要

- 一覧ページから商品詳細ページへのリンクを取得
- `next` ボタンを辿り、最終ページまで自動でクロール
- 各商品の詳細ページにアクセスし、以下の項目を取得
  - title
  - price（数値型）
  - currency（GBP）
  - url
- 例外処理
  - 一覧ページ取得時のHTTPエラー
  - 詳細ページ取得時のHTTPエラー
  - 個別商品のパースエラー
  - 一部でエラーが発生しても処理全体は継続
- 取得結果を `books_detail_minimal.csv` として保存

## 使用技術

- Python
- requests
- BeautifulSoup4
- pandas
- 正規表現（価格文字列の抽出）

## 実行方法

```bash
pip install -r requirements.txt
python books_detail_minimal.py
