# 万能视频下载器

一个支持多平台的视频下载工具，基于 yt-dlp 和专用解析器实现，支持抖音、B站、YouTube 等主流视频平台。

## 功能特性

- **多平台支持**：支持 1800+ 视频平台（通过 yt-dlp）
- **抖音无水印下载**：专用解析器，无需 Cookie，自动获取无水印视频
- **B站视频下载**：支持 DASH 格式，自动合并音视频
- **YouTube 视频下载**：支持代理配置，服务端代理下载
- **代理配置管理**：支持 HTTP/HTTPS/SOCKS5 代理，自动检测常见代理工具
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

### 3. YouTube 视频下载

**技术方案**：
- 代理配置支持（HTTP/HTTPS/SOCKS5）
- 自动检测常见代理工具（Clash、v2rayN、Shadowsocks）
- 服务端代理下载（绕过防盗链）

**关键实现**：
```python
# 强制 YouTube 使用服务端代理下载
if is_youtube_url(req.url):
    return {
        "proxy_download": True,
        "message": "YouTube 视频需要通过服务端代理下载"
    }
```

### 4. 平台适配策略

| 平台 | 解析方式 | 下载方式 | 特殊处理 | 代理需求 |
|------|---------|---------|---------|---------|
| 抖音 | 专用解析器 | 直链下载 | 无水印处理 | 无需代理 |
| B站 | yt-dlp | 服务端代理 | 音视频合并 | 无需代理 |
| YouTube | yt-dlp | 服务端代理 | 防盗链处理 | **需要代理** |
| TikTok | yt-dlp | 服务端代理 | - | **需要代理** |
| Twitter/X | yt-dlp | 服务端代理 | - | **需要代理** |
| Instagram | yt-dlp | 服务端代理 | - | **需要代理** |

## 安装运行

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg
- 代理工具（Clash/v2rayN/Shadowsocks 等，用于下载 YouTube 等境外平台）

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

## 代理配置

### 支持的平台

以下平台在中国大陆无法直接访问，需要配置代理：
- YouTube
- TikTok
- Twitter/X
- Instagram

### 配置方法

1. 打开前端页面，点击顶部导航栏的"代理设置"按钮
2. 输入代理地址（支持 HTTP/HTTPS/SOCKS5）
3. 点击"测试连接"验证代理可用
4. 保存配置

### 常见代理配置

| 工具 | HTTP 代理 | SOCKS5 代理 |
|------|----------|-------------|
| Clash | `http://127.0.0.1:7890` | - |
| Clash Verge | `http://127.0.0.1:7897` | - |
| v2rayN | `http://127.0.0.1:10809` | `socks5://127.0.0.1:10808` |
| Shadowsocks | - | `socks5://127.0.0.1:1080` |

### 自动检测

点击"自动检测常见代理"按钮，系统会自动检测上述常见代理配置。

## API 接口

### 解析视频
```http
POST /api/parse
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=xxx"
}
```

### 下载视频
```http
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=xxx",
  "format_id": "bestvideo+bestaudio/best"
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

### 代理配置 API

#### 获取代理配置
```http
GET /api/config/proxy
```

#### 设置代理配置
```http
POST /api/config/proxy
Content-Type: application/json

{
  "http_proxy": "http://127.0.0.1:7890",
  "https_proxy": "http://127.0.0.1:7890",
  "socks_proxy": "socks5://127.0.0.1:10808"
}
```

#### 测试代理连接
```http
POST /api/config/proxy/test
Content-Type: application/json

{
  "proxy": "http://127.0.0.1:7890",
  "test_url": "https://www.google.com"
}
```

#### 获取支持的平台列表
```http
GET /api/platforms
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

### 阶段三：YouTube 支持
- [x] 代理配置管理
- [x] 自动检测常见代理工具
- [x] 服务端代理下载
- [x] 代理连接测试

### 关键技术问题及解决方案

**问题1**：抖音视频需要 Cookie
- **方案**：使用 iesdouyin.com 公开 API + WAF 挑战解决

**问题2**：B站视频下载无声
- **方案**：`format_id+bestaudio` 合并音视频

**问题3**：B站直链 403
- **方案**：服务端代理下载

**问题4**：YouTube 无法访问
- **方案**：代理配置支持 + 服务端代理下载

**问题5**：YouTube 直链防盗链
- **方案**：强制使用服务端代理下载

## 许可证

MIT License

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载工具
- [rathodpratham-dev/douyin_video_downloader](https://github.com/rathodpratham-dev/douyin_video_downloader) - 抖音解析参考
