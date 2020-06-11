# INIT.ENGINEER DISCORD BOT

本機器人是以 [discord_bot.py](https://github.com/AlexFlipnote/discord_bot.py) 作為模板上的延伸。

# 如何使用它？

1. 在[此處](https://discordapp.com/developers/applications/me)建立機器人，並取得機器人的 Token。
2. 將根目錄下的 `config.json.example` 檔案重新命名為 `config.json`，然後填寫所需的資訊，例如 token、prefix 和 game。
3. 要安裝應用程式所需要的套件，請執行 `pip install -r requirements.txt`，如果上面沒辦法正常執行的話，請執行 `python -m pip install -r requirements.txt`，要注意的是這可能需要使用 `Administrator/sudo` 來執行。
4. 透過 `cmd/terminal` 終端機來啟動應用程式，你必須移動到該應用程式的資料夾，並且輸入 `python index.py` 來啟動。

## config.json內容說明

* ``token`` : 上面取得的Token
* ``prefix`` : 指令前綴
* ``owners`` : 陣列，內容為開發者的ID
* ``botserver`` : discord伺服器邀請連結，使用指令botserver會傳給使用者
* ``reaction_role`` : "加入反應以獲得相對應身分組功能"的詳細資料
    * ``message`` : 希望使用者對哪條訊息加入反應的ID
    * ``roles`` : 陣列，內容為加入反應的貼圖名稱以及相對應的身分組
        * ``sticker`` : 加入反應的貼圖**名稱**，unicode emoji的名字即為emoji本身，伺服器的emoji則為當時設定的名稱
        * ``role`` : 相對應的身分組的ID