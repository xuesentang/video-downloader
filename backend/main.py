"""
FastAPI 主入口模块
提供视频解析、下载、直链获取等 REST API 接口
"""

import os
import asyncio
from contextlib import asynccontextmanager
from urllib.parse import unquote

from dotenv import load_dotenv
load_dotenv()

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from downloader import VideoDownloader
from douyin import DouyinParser, is_douyin_url


# 初始化下载器实例
downloader = VideoDownloader()

# 初始化抖音解析器（无需 cookies，开箱即用）
douyin_parser = DouyinParser()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时: 初始化必要资源
    关闭时: 清理临时下载文件
    """
    # 启动时执行
    print("🚀 万能视频下载器服务启动中...")
    yield
    # 关闭时执行
    print("🧹 清理临时文件...")
    download_dir = downloader.DOWNLOAD_DIR
    if os.path.exists(download_dir):
        for f in os.listdir(download_dir):
            try:
                os.remove(os.path.join(download_dir, f))
                print(f"  已删除: {f}")
            except OSError as e:
                print(f"  删除失败 {f}: {e}")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="万能视频下载器 API",
    description="基于 yt-dlp 的万能视频下载服务，支持 1800+ 平台",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS 中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 请求模型定义 ====================

class ParseRequest(BaseModel):
    """
    视频解析请求模型
    
    Attributes:
        url: 视频链接，支持 1800+ 平台
    """
    url: str


class DownloadRequest(BaseModel):
    """
    视频下载请求模型
    
    Attributes:
        url: 视频链接
        format_id: 格式ID，默认最佳质量
    """
    url: str
    format_id: str = "bestvideo+bestaudio/best"


class DirectUrlRequest(BaseModel):
    """
    获取直链请求模型
    
    Attributes:
        url: 视频链接
        format_id: 格式ID，默认最佳质量
    """
    url: str
    format_id: str = "best"


# ==================== API 路由 ====================

@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态信息
    """
    return {
        "status": "ok",
        "message": "万能视频下载器服务运行中",
        "version": "1.0.0"
    }


@app.post("/api/parse")
async def parse_video_endpoint(req: ParseRequest):
    """
    解析视频信息
    
    功能说明:
        提取视频的元数据，包括标题、缩略图、时长、可用格式等
        抖音视频使用专门的解析器
    
    Args:
        req: ParseRequest 包含视频 URL
        
    Returns:
        包含视频信息的 JSON 响应
        
    Raises:
        HTTPException: 解析失败时返回 400 错误
    """
    try:
        # 判断是否为抖音链接，使用专门的解析器
        if is_douyin_url(req.url):
            # 抖音解析器是异步的，直接 await
            result = await douyin_parser.parse(req.url)
        else:
            # 其他平台使用 yt-dlp（同步，在线程池中运行）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, downloader.parse_video, req.url)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": f"解析失败: {str(e)}"
            }
        )


@app.post("/api/download")
async def download_video_endpoint(req: DownloadRequest):
    """
    下载视频（服务端代理模式）
    
    功能说明:
        服务端下载视频后，以文件流形式返回给客户端
        适用于有防盗链的平台
    
    Args:
        req: DownloadRequest 包含视频 URL 和格式ID
        
    Returns:
        视频文件流
        
    Raises:
        HTTPException: 下载失败时返回 400/500 错误
    """
    try:
        # 抖音链接使用 aiohttp 直接下载
        if is_douyin_url(req.url):
            # 1. 解析获取无水印直链
            parse_result = await douyin_parser.parse(req.url)
            video_url = parse_result["download_url"]
            title = parse_result["title"]
            
            # 2. 生成安全文件名
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_title:
                safe_title = "douyin_video"
            filename = f"{safe_title}.mp4"
            filepath = os.path.join(downloader.DOWNLOAD_DIR, filename)
            
            # 3. 确保下载目录存在
            os.makedirs(downloader.DOWNLOAD_DIR, exist_ok=True)
            
            # 4. 使用 aiohttp 下载视频
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    video_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Referer": "https://www.douyin.com/"
                    }
                ) as response:
                    response.raise_for_status()
                    with open(filepath, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
            
            # 5. 返回文件响应
            return FileResponse(
                path=filepath,
                filename=filename,
                media_type="video/mp4",
            )
        
        # B站链接使用 yt-dlp 下载（处理分片视频）
        if is_bilibili_url(req.url):
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, downloader.download_video, req.url, req.format_id
            )
            
            filepath = result["filepath"]
            
            # 检查文件是否存在
            if not os.path.exists(filepath):
                raise HTTPException(
                    status_code=500,
                    detail="下载的文件不存在"
                )
            
            # 返回文件响应
            return FileResponse(
                path=filepath,
                filename=result["filename"],
                media_type="video/mp4",
            )
        
        # 其他平台使用 yt-dlp
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, downloader.download_video, req.url, req.format_id
        )
        
        filepath = result["filepath"]
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=500,
                detail="下载的文件不存在"
            )
        
        # 返回文件响应
        return FileResponse(
            path=filepath,
            filename=result["filename"],
            media_type="application/octet-stream",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": f"下载失败: {str(e)}"
            }
        )


def is_bilibili_url(url: str) -> bool:
    """判断是否为B站链接"""
    return "bilibili.com" in url.lower() or "b23.tv" in url.lower()


@app.post("/api/direct-url")
async def get_direct_url_endpoint(req: DirectUrlRequest):
    """
    获取视频直链
    
    功能说明:
        获取视频的直接下载链接，浏览器可直接访问下载
        不占服务器带宽
    
    Args:
        req: DirectUrlRequest 包含视频 URL 和格式ID
        
    Returns:
        包含直链信息的 JSON 响应
        
    Raises:
        HTTPException: 获取失败时返回 400 错误
    """
    try:
        # 抖音链接使用专用解析器获取无水印直链
        if is_douyin_url(req.url):
            result = await douyin_parser.parse(req.url)
            return {
                "success": True,
                "data": {
                    "url": result["download_url"],
                    "title": result["title"],
                    "ext": "mp4",
                    "proxy_download": False
                }
            }
        
        # B站链接需要服务端代理下载（防盗链）
        if is_bilibili_url(req.url):
            return {
                "success": True,
                "data": {
                    "url": "",
                    "title": "",
                    "ext": "mp4",
                    "proxy_download": True,
                    "message": "B站视频需要通过服务端代理下载"
                }
            }
        
        # 其他平台使用 yt-dlp
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, downloader.get_direct_url, req.url, req.format_id
        )
        result["proxy_download"] = False
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": f"获取直链失败: {str(e)}"
            }
        )


@app.get("/api/proxy/thumbnail")
async def proxy_thumbnail(url: str = Query(..., description="缩略图URL")):
    """
    代理获取视频缩略图
    
    功能说明:
        绕过防盗链，代理获取视频平台的缩略图
        前端可直接使用此接口作为图片 src
    
    Args:
        url: 缩略图原始 URL
        
    Returns:
        图片二进制数据
        
    Raises:
        HTTPException: 获取失败时返回 502 错误
    """
    try:
        # URL 解码
        decoded_url = unquote(url)
        
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                decoded_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": decoded_url,
                }
            )
            resp.raise_for_status()
            
            content_type = resp.headers.get("content-type", "image/jpeg")
            
            return StreamingResponse(
                iter([resp.content]),
                media_type=content_type,
                headers={"Cache-Control": "public, max-age=86400"},
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"缩略图加载失败: {str(e)}"
        )


# ==================== 主入口 ====================

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置，或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🌐 服务启动: http://{host}:{port}")
    print(f"📚 API 文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
