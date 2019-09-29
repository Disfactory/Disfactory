# Disfactory Backend
`Disfactory 違章工廠舉報系統` 的後端。

## Setup

### 1. Pre-install
- Python 3.7
- PostgreSQL 11

### 2. DB settings
### 3. Environment variables
使用環境變數來設定，使用 `dotenv` 來方便修改。請參考 `.env.sample` 並複製一份 `.env`。

### 4. Install python packages
`pipenv install --dev`


## Usage

### Run server
### API
https://g0v.hackmd.io/FZFghtuoQ0aaGIl9xXzuKw#API


## Development Guide

### Architecture
還在畫...


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
