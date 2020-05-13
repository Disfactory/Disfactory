# Disfactory Backend
`Disfactory 違章工廠舉報系統` 的後端。

## Setup
- [手動設定](docs/SETUP_MANUAL.md)
- [透過 docker-compose](docs/SETUP_COMPOSE.md)

## Usage

### Run server
```
python manage.py runserver
```

### API
https://g0v.hackmd.io/FZFghtuoQ0aaGIl9xXzuKw#API


## Development Guide

### Architecture
![](backend.png)

### Tests
用內建的 unittest ，跑以下指令就可以跑全部的測試：
```
make test
```
