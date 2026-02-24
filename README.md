# MusicApp

4つの音楽系ニッチ機能を1つに統合した Web アプリケーション。

## デモ

> デプロイ後にURLを追記

## 機能一覧

### コード譜（JPop Chord）
J-POP のコード進行を検索・閲覧できるビューア。
- インクリメンタル検索（曲名・アーティスト名・かな対応）
- カポ/キー変換（12音階の半音計算をクライアントサイドで即時反映）
- 自動スクロール（速度調整 0.5x〜3.0x）
- お気に入り登録

### 練習記録（GuitarLog）
ギター練習のモチベーションを維持するトラッカー。
- 練習タイマー（開始/一時停止/停止 → セッション保存）
- クイック記録（15/30/45/60分プリセット）
- 練習曲管理（ステータス: 練習中/弾ける/お休み）
- 連続練習ストリーク表示
- 週間練習時間グラフ

### ライブ記録（LiveLog）
ライブ・コンサートの思い出と費用を管理するダイアリー。
- イベント CRUD（アーティスト/公演名/日付/会場）
- セットリスト入力（HTMX で動的追加・削除）
- チケット情報・感想（★5段階評価）
- 費用記録（カテゴリ別集計・月次グラフ）
- 次のライブまでのカウントダウン

### 作曲管理（SongDiary）
作曲プロジェクトの進捗とアイデアを記録するノート。
- プロジェクト管理（7段階ステータス: アイデア → 完成）
- テキストメモ（HTMX インライン追加）
- 音声録音（MediaRecorder API でブラウザから直接録音）
- 写真メモアップロード
- タイムライン表示

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| バックエンド | Python 3.13 / Django 5.2 LTS |
| 認証 | django-allauth（メール + パスワード） |
| データベース | PostgreSQL 16 |
| フロントエンド | HTMX 2.0 / Alpine.js 3 / TailwindCSS (CDN) |
| グラフ | Chart.js 4 |
| 静的ファイル | WhiteNoise |
| WSGI | Gunicorn |
| デプロイ | Render |

## 技術的なこだわり

### HTMX + Alpine.js によるビルドレス SPA 風 UX
React/Vue 等のフレームワークを使わず、Django テンプレート + HTMX + Alpine.js でページ遷移なしの部分更新を実現。検索のデバウンス、セトリの動的編集、お気に入りトグルなどがすべてサーバーサイドレンダリングのまま動作します。JS のビルドステップが不要なため、開発・デプロイがシンプルです。

### クライアントサイドのコード変換ロジック
カポ位置やキー変更による転調を、サーバーへのリクエストなしにブラウザ上で即座に計算・反映。12音階の半音計算、♯/♭の正規化、コードサフィックス（m, 7, maj7 等）の保持など、音楽理論に基づいた変換ロジックを JavaScript で実装しています。

### Web API の積極活用
- **MediaRecorder API**: 外部ライブラリなしでブラウザ音声録音を実装
- **Wake Lock API**: コード譜の自動スクロール中に画面スリープを防止
- **requestAnimationFrame**: 滑らかな自動スクロールアニメーション

### Django App 分割アーキテクチャ
4つの独立したドメイン（コード譜・練習・ライブ・作曲）をそれぞれ Django App として分離。モデル・ビュー・URL は各アプリが独自に管理しつつ、認証・テンプレート・静的ファイルは共通基盤として共有する設計です。

### Settings 分割による環境管理
`base.py` / `development.py` / `production.py` の3層構成で、環境変数 + `dj-database-url` によりデプロイ先に依存しない設定を実現しています。

## ローカル開発

### 前提条件
- Python 3.13+
- PostgreSQL 16+（Docker 推奨）

### セットアップ

```bash
cd musicapp

# 仮想環境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# PostgreSQL（Docker）
docker run -d --name musicapp-db \
  -e POSTGRES_USER=musicapp \
  -e POSTGRES_PASSWORD=musicapp123 \
  -e POSTGRES_DB=musicapp_dev \
  -p 5434:5432 postgres:16-alpine

# 環境変数
cp .env.example .env  # または手動で .env を作成

# マイグレーション＆シードデータ
python manage.py migrate
python manage.py seed_songs
python manage.py createsuperuser

# 起動
python manage.py runserver
```

### 環境変数（.env）

```
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://musicapp:musicapp123@localhost:5434/musicapp_dev
```

## ライセンス

This project is for portfolio purposes.
