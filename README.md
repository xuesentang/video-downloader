# 万能视频下载器

一个支持多平台的视频下载工具，基于 yt-dlp 和专用解析器实现，支持抖音、B站等主流视频平台。

## 功能特性

- **多平台支持**：支持 1800+ 视频平台（通过 yt-dlp）
- **抖音无水印下载**：专用解析器，无需 Cookie，自动获取无水印视频
- **B站视频下载**：支持 DASH 格式，自动合并音视频
- **Web 界面**：基于 Vue3 + Tailwind CSS 的现代化前端
- **REST API**：FastAPI 提供完整的 API 接口

## 技术栈

### 后端
- Python 3.8+
- FastAPI - Web 框架
- yt-dlp - 视频下载引擎
- aiohttp - 异步 HTTP 客户端
- FFmpeg - 音视频合并

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- Tailwind CSS - 样式框架

## 项目结构

```
video-downloader/
├── backend/              # 后端代码
│   ├── main.py          # FastAPI 主入口
│   ├── downloader.py    # yt-dlp 下载器封装
│   ├── douyin.py        # 抖音专用解析器
│   ├── requirements.txt # Python 依赖
│   └── downloads/       # 下载文件存放目录
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── App.vue
│   │   ├── api/         # API 封装
│   │   └── components/  # Vue 组件
│   ├── package.json
│   └── vite.config.js
└── docs/                # 文档
```

## 核心功能实现

### 1. 抖音视频下载

**技术方案**：
- 使用 iesdouyin.com 公开 API 解析视频
- 自动处理短链接重定向
- 解决 WAF 反爬挑战
- URL 替换 `playwm` → `play` 获取无水印视频

**关键代码**：[backend/douyin.py](backend/douyin.py)

### 2. B站视频下载

**技术方案**：
- yt-dlp 解析 DASH 格式视频
- 视频流 + 音频流合并
- FFmpeg 自动合并输出 MP4

**关键修复**：
```python
# 音视频合并
format_spec = f"{format_id}+bestaudio/best"
"merge_output_format": "mp4"
```

### 3. 平台适配策略

| 平台 | 解析方式 | 下载方式 | 特殊处理 |
|------|---------|---------|---------|
| 抖音 | 专用解析器 | 直链下载 | 无水印处理 |
| B站 | yt-dlp | 服务端代理 | 音视频合并 |
| 其他 | yt-dlp | 直链/代理 | 自动适配 |

## 安装运行

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

服务启动在 http://localhost:8000

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## API 接口

### 解析视频
```http
POST /api/parse
Content-Type: application/json

{
  "url": "https://www.bilibili.com/video/xxx"
}
```

### 下载视频
```http
POST /api/download
Content-Type: application/json

{
  "url": "https://www.bilibili.com/video/xxx",
  "format_id": "30080"
}
```

### 获取直链
```http
POST /api/direct-url
Content-Type: application/json

{
  "url": "https://v.douyin.com/xxx"
}
```

## 开发历程

### 阶段一：核心功能实现
- [x] 项目架构设计
- [x] FastAPI 后端搭建
- [x] Vue3 前端开发
- [x] yt-dlp 集成

### 阶段二：平台适配
- [x] 抖音无水印下载（无需 Cookie）
- [x] B站音视频合并修复
- [x] 防盗链处理

### 关键技术问题及解决方案

**问题1**：抖音视频需要 Cookie
- **方案**：使用 iesdouyin.com 公开 API + WAF 挑战解决

**问题2**：B站视频下载无声
- **方案**：`format_id+bestaudio` 合并音视频

**问题3**：B站直链 403
- **方案**：服务端代理下载

## 许可证

MIT License

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载工具
- [rathodpratham-dev/douyin_video_downloader](https://github.com/rathodpratham-dev/douyin_video_downloader) - 抖音解析参考
