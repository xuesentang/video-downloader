# 万能视频下载网站 - 完整开发计划

## 📋 项目概述

**项目名称**: 万能视频下载网站  
**核心目标**: 构建一个支持 1800+ 平台的视频下载工具网站，具备 AI 视频总结功能  
**目标用户**: 需要下载/保存视频的普通用户和内容创作者  

---

## 🎯 需求完整性校验与补全

### 1. 已明确的需求

| 需求项 | 状态 | 说明 |
|--------|------|------|
| 跨平台视频下载 | ✅ 已明确 | 基于 yt-dlp，支持 1800+ 平台 |
| Web 网站形态 | ✅ 已明确 | 前后端分离架构 |
| AI 视频总结 | ✅ 已明确 | DeepSeek API 流式输出 |
| 移动端适配 | ✅ 已明确 | 响应式设计 |
| 用户/付费系统 | ✅ 已明确 | Stripe 支付 + JWT 认证 |
| UI 风格参考 | ✅ 已明确 | 参考 ai.codefather.cn/painting |

### 2. 需要补全/确认的细节

#### 2.1 配色方案确认
根据参考网站分析，建议采用以下配色：
- **主色**: `#1777FF` (科技蓝，突出专业可靠)
- **背景**: `#FFFFFF` (纯白，简洁干净)
- **辅助背景**: `#F8FAFC` (浅灰，区分区块)
- **文字主色**: `#1F1F1F` (深黑，确保可读性)
- **文字次要**: `#6B7280` (灰色，辅助信息)
- **成功色**: `#10B981` (绿色，操作成功)
- **警告色**: `#F59E0B` (橙色，提示注意)

#### 2.2 功能优先级确认
```
P0 (核心功能，必须实现):
├── 视频链接解析
├── 视频下载（直链+代理模式）
├── 多平台支持
└── 基础 UI 界面

P1 (重要功能，建议实现):
├── AI 视频总结
├── 用户注册/登录
├── 移动端适配
└── VIP 套餐展示

P2 (扩展功能，后续迭代):
├── Stripe 支付集成
├── 字幕翻译
├── 批量下载
└── 下载历史
```

#### 2.3 技术栈确认

**前端**:
- Vue 3 + Vite (已确认)
- Tailwind CSS v4 (已确认)
- 图标: Heroicons (SVG)

**后端**:
- FastAPI (已确认)
- yt-dlp (已确认)
- DeepSeek API (已确认)
- SQLite (轻量数据库，已确认)

---

## 🏗️ 全局架构规划

### 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          用户浏览器                                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │              Vue3 + Vite + Tailwind CSS                        ││
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  ││
│  │  │   Hero区域    │───▶│  视频信息面板 │───▶│   AI总结面板      │  ││
│  │  │  (URL输入)   │    │ (格式+下载)  │    │ (4 Tab切换)      │  ││
│  │  └──────────────┘    └──────────────┘    └──────────────────┘  ││
│  └───────────────────────────┬─────────────────────────────────────┘│
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTP API / SSE
┌──────────────────────────────┼──────────────────────────────────────┐
│                      FastAPI 后端                                     │
│  ┌───────────────────────────┴─────────────────────────────────────┐│
│  │  /api/parse      → 解析视频信息                                   ││
│  │  /api/download   → 服务端下载并提供文件                            ││
│  │  /api/direct-url → 获取视频直链                                   ││
│  │  /api/summarize  → AI视频总结（SSE流式）                          ││
│  │  /api/chat       → AI视频问答（SSE流式）                          ││
│  │  /api/auth/*     → 用户认证                                       ││
│  │  /api/payment/*  → 支付相关                                       ││
│  └──────────┬─────────────────────────┬──────────────────────────┘│
│             │                         │                             │
│  ┌──────────┴──────────┐  ┌───────────┴──────────────┐             │
│  │   yt-dlp 封装层      │  │   AI 总结模块             │             │
│  │   extract_info()    │  │   SubtitleExtractor       │             │
│  │   download()        │  │   → 字幕提取(yt-dlp/B站)   │             │
│  │   get_url()         │  │   VideoSummarizer         │             │
│  │                     │  │   → DeepSeek API 总结/问答 │             │
│  └─────────────────────┘  └────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. 项目目录结构

```
free-video-downloader/
├── docs/                           # 项目文档
│   ├── 需求分析.md
│   ├── 方案设计.md
│   └── 保姆级本地运行指南.md
│
├── backend/                        # FastAPI 后端
│   ├── main.py                     # 入口 + 路由 + dotenv 加载
│   ├── downloader.py               # yt-dlp 封装（视频解析/下载）
│   ├── douyin.py                   # 抖音专用解析模块
│   ├── summarizer.py               # AI 总结模块（字幕提取 + DeepSeek）
│   ├── api_summarize.py            # AI 总结 API 路由
│   ├── api_auth.py                 # 用户认证 API 路由
│   ├── api_payment.py              # 支付 API 路由
│   ├── auth.py                     # JWT 认证工具
│   ├── database.py                 # SQLite 数据库操作
│   ├── requirements.txt            # Python 依赖
│   ├── .env.example                # 环境变量模板
│   └── downloads/                  # 临时下载目录
│
├── frontend/                       # Vue3 前端
│   ├── public/
│   │   ├── favicon.svg
│   │   └── robots.txt
│   ├── src/
│   │   ├── main.js                 # 入口文件
│   │   ├── App.vue                 # 根组件
│   │   ├── style.css               # 全局样式 + Tailwind 配置
│   │   ├── api/                    # API 封装
│   │   │   ├── video.js            # 视频相关 API
│   │   │   ├── summarize.js        # AI 总结 API
│   │   │   ├── auth.js             # 认证 API
│   │   │   └── payment.js          # 支付 API
│   │   └── components/             # Vue 组件
│   │       ├── AppHeader.vue       # 顶部导航
│   │       ├── HeroSection.vue     # 首页 Hero 区域
│   │       ├── VideoResult.vue     # 视频信息展示
│   │       ├── VideoSummary.vue    # AI 总结面板
│   │       ├── FeatureSection.vue  # 功能亮点
│   │       ├── HowToSection.vue    # 使用步骤
│   │       ├── ComparisonSection.vue # 对比区域
│   │       ├── PricingSection.vue  # VIP 套餐
│   │       ├── PlatformSection.vue # 支持平台
│   │       ├── AppFooter.vue       # 页脚
│   │       └── AuthModal.vue       # 登录/注册弹窗
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## 📐 接口设计规范

### 1. 视频解析接口

```
POST /api/parse
Content-Type: application/json

Request:
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

Response (200):
{
    "success": true,
    "data": {
        "id": "dQw4w9WgXcQ",
        "title": "视频标题",
        "thumbnail": "https://i.ytimg.com/vi/xxx/maxresdefault.jpg",
        "duration": 212,
        "duration_string": "3:32",
        "uploader": "上传者名称",
        "platform": "YouTube",
        "view_count": 1500000,
        "upload_date": "20240101",
        "formats": [
            {
                "format_id": "137+140",
                "ext": "mp4",
                "resolution": "1920x1080",
                "height": 1080,
                "filesize": 52428800,
                "filesize_approx": 52428800,
                "vcodec": "avc1",
                "acodec": "mp4a",
                "label": "1080p MP4 (50MB)"
            }
        ],
        "subtitles": ["en", "zh-Hans", "ja"]
    }
}
```

### 2. 视频下载接口

```
POST /api/download
Content-Type: application/json

Request:
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format_id": "137+140"
}

Response: 视频文件流 (Content-Type: video/mp4)
Headers:
  Content-Disposition: attachment; filename="视频标题.mp4"
```

### 3. AI 视频总结接口 (SSE 流式)

```
POST /api/summarize
Content-Type: application/json

Request:
{
    "url": "https://www.bilibili.com/video/BV1mAAmzqEfP",
    "language": "zh"
}

Response: SSE 事件流 (Content-Type: text/event-stream)

事件类型：
  - subtitle  → 字幕数据（含 segments 时间戳列表和 full_text）
  - summary   → 总结摘要（流式 token，逐字输出）
  - mindmap   → 思维导图 Markdown（一次性返回）
  - done      → 完成信号
  - error     → 错误信息
```

---

## 🎨 UI/UX 设计规范

### 1. 配色方案

```css
/* 主色调 */
--color-primary: #1777FF;        /* 科技蓝 - 主按钮、链接 */
--color-primary-dark: #1260DD;   /* 深蓝 - 悬停状态 */
--color-primary-light: #E8F1FF;  /* 浅蓝 - 背景装饰 */

/* 背景色 */
--color-bg-main: #FFFFFF;        /* 纯白主背景 */
--color-bg-section: #F8FAFC;     /* 浅灰区块背景 */

/* 文字色 */
--color-text-primary: #1F1F1F;   /* 主文字 - 标题 */
--color-text-secondary: #6B7280; /* 次要文字 - 描述 */
--color-text-muted: #9CA3AF;     /* 辅助文字 - 提示 */

/* 功能色 */
--color-success: #10B981;        /* 成功 - 绿色 */
--color-warning: #F59E0B;        /* 警告 - 橙色 */
--color-error: #EF4444;          /* 错误 - 红色 */

/* 边框色 */
--color-border: #E5E7EB;         /* 边框 */
--color-border-light: #F3F4F6;   /* 浅色边框 */
```

### 2. 页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  Header (固定顶部)                                           │
│  Logo + 导航链接 + 登录/注册按钮                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Hero 区域 (渐变背景)                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  标签: 支持 1800+ 平台，永久免费使用                    │  │
│  │                                                       │  │
│  │  大标题: 免费在线视频下载器，一键保存                   │  │
│  │                                                       │  │
│  │  副标题: 粘贴视频链接，智能解析下载...                  │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  🔗 粘贴视频链接...                    [解析视频] │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                       │  │
│  │  试试: [YouTube] [Bilibili] [Twitter/X]               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  视频结果区域 (解析成功后显示)                                │
│  ┌───────────────────────┐  ┌─────────────────────────────┐ │
│  │                       │  │                             │ │
│  │   视频缩略图           │  │   AI 总结面板 (4 Tab)        │ │
│  │   + 视频信息           │  │   - 总结摘要                 │ │
│  │   + 格式选择           │  │   - 字幕文本                 │ │
│  │   + 下载按钮           │  │   - 思维导图                 │ │
│  │   + AI总结按钮         │  │   - AI 问答                  │ │
│  │                       │  │                             │ │
│  └───────────────────────┘  └─────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  功能亮点区域 (5个特性卡片)                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│  │ 1800+   │ │  高清    │ │  AI     │ │  全平台  │ │  安全   ││
│  │ 平台    │ │  画质    │ │  总结   │ │  支持    │ │  可靠   ││
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  使用步骤区域                                                │
│  步骤1 → 步骤2 → 步骤3                                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  对比区域 (免费版 vs 高级版)                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  VIP 套餐定价区域                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   月度会员   │  │   年度会员   │  │   终身会员   │          │
│  │   ¥29/月    │  │   ¥199/年   │  │   ¥499一次性 │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  支持平台展示区域 (Logo墙)                                    │
│  YouTube Bilibili 抖音 TikTok Twitter/X Instagram ...       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Footer                                                      │
│  版权信息 + 免责声明                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. 组件设计规范

#### 按钮样式
```
主按钮: bg-primary hover:bg-primary-dark text-white rounded-full px-6 py-3
次要按钮: bg-white border border-border hover:border-primary text-text-primary rounded-full
下载按钮: bg-success hover:bg-success/90 text-white rounded-lg px-4 py-2
```

#### 卡片样式
```
功能卡片: bg-white rounded-xl p-6 shadow-sm border border-border-light hover:shadow-md transition-shadow
视频卡片: bg-white rounded-xl overflow-hidden shadow-md
```

#### 输入框样式
```
搜索框: w-full h-14 pl-12 pr-4 rounded-full border border-border bg-white 
        focus:ring-2 focus:ring-primary/30 focus:border-primary
```

---

## 📦 开发阶段计划

### 阶段一: 核心功能实现 (预计 2-3 天)

#### 1.1 后端基础搭建
- [ ] 创建 requirements.txt 依赖文件
- [ ] 实现 downloader.py (yt-dlp 封装)
  - parse_video() - 解析视频信息
  - download_video() - 下载视频
  - get_direct_url() - 获取直链
- [ ] 实现 main.py FastAPI 入口
  - /api/health 健康检查
  - /api/parse 解析接口
  - /api/download 下载接口
  - /api/direct-url 直链接口
  - /api/proxy/thumbnail 缩略图代理

#### 1.2 前端基础搭建
- [ ] 初始化 Vue3 + Vite 项目
- [ ] 配置 Tailwind CSS v4
- [ ] 创建基础组件结构
- [ ] 实现 HeroSection.vue (URL 输入)
- [ ] 实现 VideoResult.vue (视频信息展示)
- [ ] 实现 API 封装 (video.js)

#### 1.3 联调测试
- [ ] 前后端联调测试
- [ ] 测试 YouTube 视频解析下载
- [ ] 测试 Bilibili 视频解析下载
- [ ] 测试抖音视频解析下载

### 阶段二: AI 总结功能 (预计 2-3 天)

#### 2.1 后端 AI 模块
- [ ] 实现 summarizer.py
  - 字幕提取 (yt-dlp / B站 API)
  - DeepSeek API 调用封装
- [ ] 实现 api_summarize.py
  - /api/summarize SSE 流式接口
  - /api/chat SSE 问答接口

#### 2.2 前端 AI 面板
- [ ] 实现 VideoSummary.vue (4 Tab 面板)
  - 总结摘要 Tab
  - 字幕文本 Tab
  - 思维导图 Tab
  - AI 问答 Tab
- [ ] 实现 API 封装 (summarize.js)
- [ ] 集成 marked + markmap

#### 2.3 联调测试
- [ ] 测试字幕提取
- [ ] 测试 AI 总结流式输出
- [ ] 测试思维导图渲染

### 阶段三: 用户与支付系统 (预计 2-3 天)

#### 3.1 后端用户系统
- [ ] 实现 database.py (SQLite)
- [ ] 实现 auth.py (JWT 工具)
- [ ] 实现 api_auth.py
  - 注册/登录/登出
  - 获取当前用户
- [ ] 实现 api_payment.py (Stripe)
  - 创建支付会话
  - 支付回调处理

#### 3.2 前端用户界面
- [ ] 实现 AppHeader.vue (登录状态)
- [ ] 实现 AuthModal.vue (登录/注册弹窗)
- [ ] 实现 PricingSection.vue (VIP 定价)
- [ ] 实现 API 封装 (auth.js, payment.js)

#### 3.3 联调测试
- [ ] 测试用户注册登录
- [ ] 测试 Stripe 支付流程
- [ ] 测试 VIP 权限控制

### 阶段四: UI 优化与完善 (预计 1-2 天)

#### 4.1 页面组件完善
- [ ] 实现 FeatureSection.vue (功能亮点)
- [ ] 实现 HowToSection.vue (使用步骤)
- [ ] 实现 ComparisonSection.vue (对比区域)
- [ ] 实现 PlatformSection.vue (平台展示)
- [ ] 实现 AppFooter.vue (页脚)

#### 4.2 响应式优化
- [ ] 移动端适配测试
- [ ] 平板适配测试
- [ ] 动画效果优化

#### 4.3 性能优化
- [ ] 图片懒加载
- [ ] 代码分割
- [ ] 缓存策略

### 阶段五: 测试与部署 (预计 1-2 天)

#### 5.1 功能测试
- [ ] 编写测试用例
- [ ] 核心功能回归测试
- [ ] 边界情况测试

#### 5.2 部署准备
- [ ] 编写部署文档
- [ ] 配置生产环境变量
- [ ] 准备 Docker 配置 (可选)

---

## ⚠️ 风险与注意事项

### 技术风险
1. **yt-dlp 更新**: 视频平台经常更新反爬机制，需要定期更新 yt-dlp
2. **DeepSeek API 稳定性**: 需要做好降级处理和错误提示
3. **跨域问题**: 开发环境需要配置 CORS

### 法律风险
1. **版权问题**: 需要明确告知用户仅下载自己有权限的视频
2. **免责声明**: 在页脚添加免责声明

### 性能风险
1. **大文件下载**: 需要设置合理的超时和分片下载
2. **AI 调用成本**: 需要限制免费用户的 AI 调用次数

---

## ✅ 验收标准

### 功能验收
- [ ] 支持至少 5 个主流平台 (YouTube/Bilibili/抖音/TikTok/Twitter)
- [ ] 视频解析成功率 > 90%
- [ ] AI 总结功能正常运行
- [ ] 用户注册登录功能正常
- [ ] Stripe 支付流程完整

### 性能验收
- [ ] 视频解析响应时间 < 10s
- [ ] 页面首屏加载时间 < 3s
- [ ] 移动端操作流畅

### UI 验收
- [ ] 与参考网站风格一致
- [ ] 响应式布局正常
- [ ] 动画效果流畅

---

## 📝 下一步行动

**请确认以下内容后，我将开始执行开发:**

1. **配色方案**是否符合预期？
2. **功能优先级**是否需要调整？
3. **开发阶段计划**是否合理？是否需要调整时间分配？
4. 是否需要先完成某个特定阶段再推进其他阶段？

确认后，我将立即开始 **阶段一: 核心功能实现** 的开发工作。
