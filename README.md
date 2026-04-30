# Reservation Manager

FastAPI / React / TypeScript を使用した、会議室予約管理システムのポートフォリオです。

バックエンドAPIとフロントエンド画面を実装しています。  
業務システムを想定し、ユーザー管理、会議室管理、予約管理、認証・認可、予約時間の重複チェック、テスト、Reactによる画面操作を実装しています。

## 作成目的

業務システム開発で必要となる基本的な設計・実装・テストの流れを確認するために作成したポートフォリオです。

## 使用技術

### バックエンド

- Python
- FastAPI
- SQLAlchemy
- MySQL
- asyncmy
- Pydantic
- JWT
- passlib / bcrypt
- pytest
- httpx

### フロントエンド

- React
- TypeScript
- Vite
- React Router
- Axios
- CSS

### インフラ / 開発環境

- Docker
- Docker Compose
- Git / GitHub
- Visual Studio Code

## 主な機能

### 認証・認可

- JWTログイン認証
- Bearer Token によるログイン中ユーザー取得
- role による権限制御
- admin / user の権限分離

### ユーザー管理

- ユーザー一覧取得
- ユーザー詳細取得
- ユーザー登録
- ユーザー更新
- ユーザー無効化
- メールアドレス重複チェック
- 論理削除

### 会議室管理

- 会議室一覧取得
- 会議室詳細取得
- 会議室登録
- 会議室更新
- 会議室無効化
- 会議室名重複チェック
- 論理削除

### 予約管理

- 予約一覧取得
- 予約詳細取得
- 予約登録
- 予約更新
- 予約無効化
- 存在しないユーザーでの予約防止
- 無効ユーザーでの予約防止
- 存在しない会議室での予約防止
- 無効会議室での予約防止
- 予約開始日時・終了日時のバリデーション
- 同一会議室での予約時間重複チェック
- 隣接する予約時間の許可

## 権限設計

| 機能 | admin | user |
|---|---:|---:|
| ユーザー一覧取得 | ○ | × |
| ユーザー登録・更新・無効化 | ○ | × |
| 会議室一覧取得 | ○ | ○ |
| 会議室詳細取得 | ○ | ○ |
| 会議室登録・更新・無効化 | ○ | × |
| 予約一覧取得 | ○ | ○ |
| 予約詳細取得 | ○ | ○ |
| 予約登録 | ○ | ○ |
| 自分の予約更新・無効化 | ○ | ○ |
| 他人の予約更新・無効化 | ○ | × |

## ディレクトリ構成

```text
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── Dockerfile
├── pytest.ini
└── requirements.txt

frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── meetingRooms/
│   │   └── reservations/
│   ├── routes/
│   ├── types/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── Dockerfile
├── package.json
└── vite.config.ts
```

### フロントエンド

- ログイン画面
- JWTアクセストークンの保存
- ログイン後の画面遷移
- 会議室一覧表示
- admin向けの会議室登録・更新・無効化
- user向けの会議室参照
- 予約一覧表示
- 予約登録
- 予約のリスト表示 / カレンダー表示切り替え
- 予約の月別カレンダー表示
- 予約の無効化
- 権限に応じた操作ボタンの表示制御

## 認証・認可について

本プロジェクトでは、JWT を用いたログイン認証を実装しています。

ログイン成功時にアクセストークンを発行し、以降のAPIリクエストでは `Authorization: Bearer <token>` によりログイン中ユーザーを特定します。

また、ユーザーの `role` により、管理者のみ実行可能なAPIを制御しています。

- `admin`: ユーザー管理、会議室管理が可能
- `user`: 会議室参照、予約操作が可能

## 論理削除について

ユーザー、会議室、予約は物理削除せず、`is_active = false` に更新する論理削除を採用しています。

業務システムでは、過去の予約履歴や関連データとの紐づきを保持する必要があるため、データを完全に削除せず、無効状態として管理する設計にしています。

ただし、テストデータについては業務データではないため、テスト終了後に物理削除しています。


## 起動方法

### 1. リポジトリをクローン

```bash
git https://github.com/yfumimotopg-hub/reservation-manager.git
cd reservation-manager
```

### 2. Dockerで起動

```bash
docker compose up --build
```

### 3. 画面確認

フロントエンド画面：
```text
http://localhost:5173
```

Swagger UI：
```text
http://localhost:8000/docs
```

Swagger UI からAPIを確認できます。

## 初期ユーザー

開発環境では、以下の初期ユーザーを作成しています。

| role | email | password |
|---|---|---|
| admin | admin@example.com | password |
| user | user@example.com | password |

## 主なAPI

### 認証

| Method | Endpoint | 説明 |
|---|---|---|
| POST | `/api/v1/auth/login` | ログイン |
| GET | `/api/v1/auth/me` | ログイン中ユーザー取得 |

### ユーザー管理

| Method | Endpoint | 説明 |
|---|---|---|
| GET | `/api/v1/users` | ユーザー一覧取得 |
| GET | `/api/v1/users/{user_id}` | ユーザー詳細取得 |
| POST | `/api/v1/users` | ユーザー登録 |
| PUT | `/api/v1/users/{user_id}` | ユーザー更新 |
| DELETE | `/api/v1/users/{user_id}` | ユーザー無効化 |

### 会議室管理

| Method | Endpoint | 説明 |
|---|---|---|
| GET | `/api/v1/meeting-rooms` | 会議室一覧取得 |
| GET | `/api/v1/meeting-rooms/{meeting_room_id}` | 会議室詳細取得 |
| POST | `/api/v1/meeting-rooms` | 会議室登録 |
| PUT | `/api/v1/meeting-rooms/{meeting_room_id}` | 会議室更新 |
| DELETE | `/api/v1/meeting-rooms/{meeting_room_id}` | 会議室無効化 |

### 予約管理

| Method | Endpoint | 説明 |
|---|---|---|
| GET | `/api/v1/reservations` | 予約一覧取得 |
| GET | `/api/v1/reservations/{reservation_id}` | 予約詳細取得 |
| POST | `/api/v1/reservations` | 予約登録 |
| PUT | `/api/v1/reservations/{reservation_id}` | 予約更新 |
| DELETE | `/api/v1/reservations/{reservation_id}` | 予約無効化 |

## テスト実行

```bash
docker compose exec backend pytest
```

現在、以下の観点でテストを作成しています。

- 会議室APIの正常系・異常系
- users API の認可テスト
- reservations API の業務ルールテスト
- 未認証時の 401
- 権限不足時の 403
- 存在しないデータ指定時の 404
- 重複登録・重複予約時の 409
- 不正な入力値の 422
- テストデータの後処理

## CI

GitHub Actions により、`main` ブランチへの push および pull request 作成時にバックエンドテストを自動実行します。

CIでは Docker Compose を使用して MySQL と FastAPI を起動し、バックエンドが起動完了したことを確認してから pytest を実行します。

```bash
docker compose exec -T backend pytest
```

## 今後の改善予定

- Alembic によるマイグレーション管理
- エラーレスポンス形式の統一
- 予約一覧の検索・日付絞り込み
- 予約の更新画面
- カレンダーの日付クリックによる予約フォーム自動入力