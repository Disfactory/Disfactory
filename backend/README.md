# Disfactory Backend
`Disfactory 違章工廠舉報系統` 的後端。提供給前端的 API 以及一個管理後台

## Setup

- [透過 docker-compose](docs/SETUP_COMPOSE.md) (`Recommanded`)
- [手動設定](docs/SETUP_MANUAL.md)

## Usage

### Run server with docker-compose

```bash
make run-dev
```

### API

https://g0v.hackmd.io/FZFghtuoQ0aaGIl9xXzuKw#API

## Development Guide

### Architecture
![](backend.png)

### Unit Tests
用內建的 unittest ，跑以下指令就可以跑全部的測試：

```bash
make test
```
