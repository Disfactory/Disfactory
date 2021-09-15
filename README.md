# Disfactory 違章工廠舉報系統

[![g0v-disfactory-badge][g0v-disfactory-badge]](https://github.com/Disfactory/Disfactory) [![CircleCI](https://circleci.com/gh/Disfactory/Disfactory.svg?style=svg)](https://circleci.com/gh/Disfactory/Disfactory) [![g0v-tw-slack](https://join.g0v.tw/badge.svg)](https://join.g0v.tw/)

![logo](https://github.com/yoyo930021/Disfactory/raw/master/docs/images/Logo_Banner.png)

### 前端的程式碼已經移到 [Disfactory/frontend](https://github.com/Disfactory/frontend)，這裡主要是放後端的程式碼，開發時請 cd 進 [backend/](backend/) 資料夾。

- [跳坑首頁 (HackMD)](https://g0v.hackmd.io/@yukaii/Disfactory)
- [Disfactory 跳坑指南](https://g0v.hackmd.io/VqCrCpoQT4KQGVhbqR9r6A)
- [開發文件](https://g0v.hackmd.io/FZFghtuoQ0aaGIl9xXzuKw)
- [g0v slack](https://) channel `#disfactory`
  - g0v slack self-invitation → [![g0v-tw-slack](https://join.g0v.tw/badge.svg)](https://join.g0v.tw/)

[g0v-disfactory-badge]: https://img.shields.io/static/v1?label=g0v&message=disfactory&color=6d8538&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAAsTAAALEwEAmpwYAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAC40lEQVQ4EZ2Uz0tbQRDHJ7HgQUUxIlKQ9iiK4CFiIQelgp6reClCD4KI0JMgVv0DKhKqCGK9ixaExiIiYkv62/ag2GiMIJrGpPVHQjWPmASTSWcm2deX1obahX27b3bm82a+u/sglUrhtTuiHrM7MYEvAXB/ZkZscG0YJcCN4w4XF3GVYF8GBhAvL/8PiImEBIZcLnxNsE9NTRgNBsXGa1dmyBkkk0npPFctmYFFjo/xY00NviHgD7dbh3HWfwAZlFOGeBzdfX34imC+5eU0zBBzAwyNQGA2m4EygkAgAEdHRxAKhSAejwOVAwUlJZDY3oaw3Q7W6WmobG2FFMWbTKZfFJUNl8Vzr9eLAyQyeeTsj/r78dDvT2eYieV4KVmVeXJyglarVUBdXV3odDrRs7OD305PcWt1FZ/RR542N+MDWuMP2hoakCrIgmYB5+fnxbG7uxvD4bA4SgUXF+jq6cG3BNE2NvBM0/B+R4f4OhwO8VNJmSlAdGMRDg4OeACbzQZFRUWiJW01uMfG4PvUFNycm4PCujooLiyEu6QfN5/PJyPrKCx+4wk33hBukUhERn7/6nCAf3AQKoaH4VZbm9j5EYvFZJ61IWzhklS6CwsLUsad2lrc3dvD8OYmvqcyt0iCVCSiS+DxeLCxsVF8l5aWskoWoNrh8/Nz7GhvF0eorsaHVVX4mIDPJyfx3doaviC97HZ7ep3snZ2dqJGenJRiCNBoCNKuPRkdxUoKoAKu7PX19Tg+Po5BdeUMx0Y/2Hw0WUtLaSncq6iA2/ReTJtRQBsU1TQw5eVBfn4+lNDhtlgsUFZWRh70RboESnsxcHaSYeb6HK6syB/E1duLqWhU1035GUelvdGW1jBz6c9IbL7wH8rLUQsEBJag35JqDFCdbUaQmvMdlYUYafe5pQWdBDxdXxebWlPO/zLqGbqGhqRUL90WDpQM/pJFLrAA92dn5TfuHhlBRunAjL65AL+v/QTng5gP6pcfjgAAAABJRU5ErkJggg==

## Data Source / 資料來源
The initial data of suspected illegal factories on farmland are provided by [Ronny Wang](https://github.com/ronnywang) via [disfactory-crawler](https://github.com/ronnywang/disfactory-crawler) from [Taiwan Map Service](https://maps.nlsc.gov.tw/), maintained by Taiwan's National Land Surveying and Mapping Center.

We maintain a [copy](backend/fixtures/full-info.csv) crawed at 2019/7/20 as old suspected illegal factories on farmland. 

系統上的既有違章工廠資料，為 2019/7/20 取自[內政部國土測繪雲](https://maps.nlsc.gov.tw/)/農業與農地資源盤查/農地資源盤查_工廠之圖層資料。資料取得之程式碼來自 [Ronny Wang](https://github.com/ronnywang) 使用 [disfactory-crawler](https://github.com/ronnywang/disfactory-crawler)。

全站由使用者回報之資料及設計圖以CC BY姓名標示4.0釋出，標註「農地違章工廠回報系統貢獻者」。使用者回報資料未涉及個人資訊部分已整理成開放資料與[API](https://api.disfactory.tw/redoc/)。
