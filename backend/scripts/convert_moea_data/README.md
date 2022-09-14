# 1. 從經濟部網站下載資料

`download_moea_data.py` 會從 "https://www.cto.moea.gov.tw/FactoryMCLA/web/information/list.php?cid=1"
下載 xlsx 檔案到 `moea_data` 資料夾中。

# 2. 轉換 xlsx 資料

讀取所有在 `moea_data/xlsx` 的檔案，使用 `openpyxl` 解析 xlsx 檔案。
如果解析出來的資料欄位有包含地段名稱，

那麼就會用 `sectname.py` 來猜測這個地段名稱的地段號
（因為儲存在 Disfactory 上的資料都是地段號，所以需要轉換城地段後來查詢） 

如果解析出來的資料有包含圖片，那麼會將圖片轉成 base64 儲存在 json 檔案中。

# 3. 使用地段號來尋找在 Disfactory 資料庫是否已經有相對應的資料了

Disfactory 有個可以用地段號查詢工廠 id 的 API `https://staging.disfactory.tw/api/sectcode`

