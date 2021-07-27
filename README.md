# grouping-manager-bot

'grouping-manager-bot' は、Discord での小グループ活動を促進する Bot です。

# 特徴
grouping-manager-bot は Python (discord.py) で作成されています。

# 使用方法
## マッチング
1. Discord 内で、`+match` コマンドを実行  
→ マッチング希望者を募るメッセージを生成
2. 生成されたメッセージに、2️⃣もしくは 3️⃣にてリアクション  
→ マッチング結果を表示。

## ロール付与
Discord 内で、`+role (引数)` コマンドを実行  
→ 以下の２つが生成される
- 引数に与えた名前を冠したロール
- そのロールの着脱用のメッセージ  

# 必要権限
- Manage Roles
- Manage Channels
- Change Nickname
- View Channels
- Send Messages
- Embed Links
- Read Message History
- Add Reactions

SERVER MEMBERS INTENT: on