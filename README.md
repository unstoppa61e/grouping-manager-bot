# grouping-manager-bot

'grouping-manager-bot' は、Discord での小グループ活動を促進する Bot です。
以下の2つの機能があります。
1. マッチング機能：マッチング希望者を、2人、もしくは3人を基本とした小グループに分ける
2. ロール付与機能：任意の名前のロールを作成し、リアクションによってロールを on/off する

## 開発環境
Python 3.9.6


## 機能概要
### マッチング
1. Discord サーバーにて`+match` コマンドを実行  
→ マッチング希望者を募るメッセージを生成します。
2. 生成されたメッセージに、2️⃣もしくは 3️⃣にてリアクション  
→ マッチング結果を表示します。

### ロール付与
Discord サーバーにて`+role (引数)` コマンドを実行  
→ 以下の２つが生成されます。
- 引数に与えた名前を冠したロール
- そのロールの着脱用のメッセージ

※ロールの削除は、リアクションだけでなく、`+rm (引数)`コマンドでも行えます。

## 利用方法

### DiscordのApplicationの作成

https://discordapp.com/developers/applications/

Botの設定

- Developer Portal から Bot を作成し、Token を環境変数に設定
- SERVER MEMBERS INTENT を ON にする
- OAuth2 の Scope から Bot をチェックし、必要権限にチェックする
- 発行された URL から Bot をサーバーに招待する

### 必要権限
- Manage Roles
- Manage Channels
- Change Nickname
- View Channels
- Send Messages
- Embed Links
- Read Message History
- Add Reactions

### 環境変数の設定

| 環境変数名            | 説明                                      |
| --------------------- | ----------------------------------------- |
| TOKEN     | BotのToken                                |

### 起動方法
Heroku: Procfile が存在するので、特別な設定は不要です。  
ローカル: `python launcher.py`で Bot をオンライン状態に立ち上げることができます。