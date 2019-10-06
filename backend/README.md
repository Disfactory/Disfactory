# Disfactory Backend
`Disfactory 違章工廠舉報系統` 的後端。

## Setup

### 1. Pre-install
- Python 3.7
- PostgreSQL > 9.0
- PostGIS > 2.0

### 2. DB settings
用 superuser 進 PostgreSQL
```
sudo su postgres
psql
```

建立一個可以開 DB 的 user 給 server
```
CREATE USER "disfactory" CREATEDB;
\password disfactory
```

開一個 DB
```
CREATE DATABASE disfactory_data OWNER "disfactory";
```

打開 PostGIS extention，但要先[安裝](https://postgis.net/install/)在系統上。
```
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

設定好之後，記得也要改環境變數，或是直接改動 `.env` 裡面的值。

### 3. Environment variables
使用環境變數來設定專案，用 `python-dotenv` 來讀取。請參考 `.env.sample` 並複製一份 `.env`。

### 4. Install python packages
`pipenv install --dev`


## Usage

### Run server
### API
https://g0v.hackmd.io/FZFghtuoQ0aaGIl9xXzuKw#API


## Development Guide

### Architecture
簡易版
![](https://g0vhackmd.blob.core.windows.net/g0v-hackmd-images/upload_b6eba6c8d06a92b8b3bc7b0fddecdc2a)


### Coding Style
用 [`black`](https://github.com/psf/black) 做自動程式碼檢查及 auto-formatting。

- 只做檢查：
```
make lint
```
- auto-formatting
```
make format
```

### Tests
用內建的 unittest ，跑以下指令就可以跑全部的測試 (包含程式碼風格檢查)：
```
make test
```
