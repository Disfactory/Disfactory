# 用 Gitpod 立即設定線上開發環境

Gitpod 是一套線上的開發環境，可以讓第一次來到本專案的你，免安裝任何套件、設定環境，直接在瀏覽器裡開始貢獻 Disfactory 這個專案！

本份文件將會介紹如何開啟 Disfactory 的 gitpod 環境，並開始貢獻你的第一行程式碼！

## 建立 gitpod workspace

1. 首先點選這個按鈕： [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/yoyo930021/Disfactory) 開啟 gitpod workspace

1. 若你還沒有註冊過 gitpod，會看到以下的畫面：
    ![](https://i.imgur.com/hRhmgQu.png)
    點選 **Login with GitHub & launch workspace** 這個按鈕
2. 完成註冊後，會看到以下畫面，顯示工作空間 (Workspace) 正在啟動中
    ![](https://i.imgur.com/LO8wrmD.png)
3. 完成後將會進入 gitpod 主介面，可以看到和 VSCode 非常相似！
    ![](https://i.imgur.com/fAnE4b0.png)

接下來介紹如何啟動後端的 Django Server 以進行開發

## 啟動後端的 Django Server

1. 點選 Terminal，輸入以下指令，建立預設資料庫使用者：
    ```bash
    createuser postgres
    ```
    ![](https://i.imgur.com/Kqo8I4r.png)
2. 在終端機輸入以下指令，安裝 python 相依套件，並載入 python 虛擬環境：
    ```bash
    cd backend # 進入 backend 資料夾
    pipenv install && pipenv shell # 設定 python 環境
    ```
    ![](https://i.imgur.com/tCX6Alv.png)
3. 最後輸入執行 Django Server 的指令
    ```bash
    python3 manage.py runserver 0.0.0.0:8000
    ```
4. 此時你會看到右下角跳出一個提示框，告訴你 gitpod workspace 中我們 server 的 8000 port 需不需要暴露給外部存取，這邊選擇 **Expose** <br>
    ![](https://i.imgur.com/7twBQuQ.png)
5. gitpod 會再跳出一個通知，這邊可以選擇 Open Preview，預覽我們剛剛跑起來的 Django Server
    ![](https://i.imgur.com/l93pfU7.png)
6. 成功跑起 Server！
    ![](https://i.imgur.com/ro5mUbG.png)


