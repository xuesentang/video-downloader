"""
视频下载器模块 - 基于 yt-dlp 的封装
提供视频解析、下载、获取直链等功能
"""

import os
import re
from typing import Dict, List, Optional, Any
from yt_dlp import YoutubeDL


class VideoDownloader:
    """
    视频下载器类
    
    功能说明:
        - 解析视频信息（标题、缩略图、格式等）
        - 下载视频到本地
        - 获取视频直链
        - 支持代理配置（用于 YouTube 等被墙网站）
    
    入参:
        download_dir: 下载文件保存目录，默认为当前目录下的 downloads 文件夹
        proxy: 代理服务器地址，如 "socks5://127.0.0.1:10808" 或 "http://127.0.0.1:7890"
    
    注意事项:
        - 需要安装 yt-dlp: pip install yt-dlp
        - 某些平台可能需要配置 cookies 才能下载高清视频
        - YouTube 等平台需要代理才能访问
    """
    
    def __init__(self, download_dir: str = None, proxy: str = None):
        """
        初始化下载器
        
        Args:
            download_dir: 下载目录路径，默认为 backend/downloads
            proxy: 代理服务器地址
        """
        if download_dir is None:
            # 获取当前文件所在目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            download_dir = os.path.join(current_dir, "downloads")
        
        self.DOWNLOAD_DIR = download_dir
        self.proxy = proxy
        # 确保下载目录存在
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
    
    def _get_ydl_opts(self, extract_flat: bool = False) -> Dict[str, Any]:
        """
        获取 yt-dlp 配置选项
        
        Args:
            extract_flat: 是否只提取列表而不下载
            
        Returns:
            yt-dlp 配置字典
        """
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": extract_flat,
        }
        
        # 添加代理配置
        if self.proxy:
            opts["proxy"] = self.proxy
        
        return opts
    
    def set_proxy(self, proxy: str):
        """
        设置代理服务器
        
        Args:
            proxy: 代理服务器地址，如 "socks5://127.0.0.1:10808"
        """
        self.proxy = proxy
    
    def clear_proxy(self):
        """清除代理配置"""
        self.proxy = None
    
    def _format_filesize(self, size: int) -> str:
        """
        将字节大小转换为人类可读格式
        
        Args:
            size: 文件大小（字节）
            
        Returns:
            格式化后的字符串，如 "50MB"
        """
        if size is None or size == 0:
            return "未知"
        
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def _get_platform(self, url: str, info: Dict) -> str:
        """
        根据 URL 和提取信息判断视频平台
        
        Args:
            url: 视频链接
            info: yt-dlp 提取的信息
            
        Returns:
            平台名称
        """
        extractor = info.get("extractor", "").lower()
        
        platform_map = {
            "youtube": "YouTube",
            "bilibili": "Bilibili",
            "douyin": "抖音",
            "tiktok": "TikTok",
            "twitter": "Twitter/X",
            "x": "Twitter/X",
            "instagram": "Instagram",
            "facebook": "Facebook",
            "reddit": "Reddit",
            "vimeo": "Vimeo",
            "dailymotion": "Dailymotion",
        }
        
        for key, name in platform_map.items():
            if key in extractor or key in url.lower():
                return name
        
        return info.get("extractor", "未知平台")
    
    def parse_video(self, url: str) -> Dict[str, Any]:
        """
        解析视频信息
        
        功能说明:
            提取视频的元数据，包括标题、缩略图、时长、可用格式等
        
        Args:
            url: 视频链接
            
        Returns:
            包含视频信息的字典
            {
                "id": 视频ID,
                "title": 标题,
                "thumbnail": 缩略图URL,
                "duration": 时长（秒）,
                "duration_string": 格式化时长,
                "uploader": 上传者,
                "platform": 平台名称,
                "view_count": 观看次数,
                "upload_date": 上传日期,
                "formats": [格式列表],
                "subtitles": [字幕语言列表]
            }
            
        Raises:
            Exception: 解析失败时抛出异常
        """
        try:
            with YoutubeDL(self._get_ydl_opts()) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    raise Exception("无法提取视频信息")
                
                # 提取格式信息
                formats = []
                seen_formats = set()
                
                for fmt in info.get("formats", []):
                    # 只保留视频格式（有视频编码的）
                    if fmt.get("vcodec") == "none":
                        continue
                    
                    height = fmt.get("height", 0)
                    if not height:
                        continue
                    
                    # 生成格式标识
                    format_key = f"{height}p"
                    if format_key in seen_formats:
                        continue
                    seen_formats.add(format_key)
                    
                    filesize = fmt.get("filesize") or fmt.get("filesize_approx", 0)
                    
                    format_info = {
                        "format_id": fmt.get("format_id", ""),
                        "ext": fmt.get("ext", "mp4"),
                        "resolution": fmt.get("resolution", ""),
                        "height": height,
                        "filesize": filesize,
                        "filesize_approx": fmt.get("filesize_approx"),
                        "vcodec": fmt.get("vcodec", ""),
                        "acodec": fmt.get("acodec", ""),
                        "label": f"{height}p {fmt.get('ext', 'mp4').upper()} ({self._format_filesize(filesize)})"
                    }
                    formats.append(format_info)
                
                # 按清晰度降序排序
                formats.sort(key=lambda x: x["height"], reverse=True)
                
                # 提取字幕信息
                subtitles = []
                subs = info.get("subtitles", {})
                auto_subs = info.get("automatic_captions", {})
                
                # 合并人工字幕和自动字幕
                all_langs = set(list(subs.keys()) + list(auto_subs.keys()))
                subtitles = sorted(list(all_langs))
                
                # 构建返回结果
                result = {
                    "id": info.get("id", ""),
                    "title": info.get("title", "未知标题"),
                    "thumbnail": info.get("thumbnail", ""),
                    "duration": info.get("duration", 0),
                    "duration_string": info.get("duration_string", ""),
                    "uploader": info.get("uploader", info.get("channel", "未知上传者")),
                    "platform": self._get_platform(url, info),
                    "view_count": info.get("view_count", 0),
                    "upload_date": info.get("upload_date", ""),
                    "formats": formats,
                    "subtitles": subtitles,
                    "original_url": url,
                }
                
                return result
                
        except Exception as e:
            raise Exception(f"解析视频失败: {str(e)}")
    
    def download_video(self, url: str, format_id: str = None) -> Dict[str, str]:
        """
        下载视频到本地
        
        功能说明:
            将视频下载到指定的下载目录
        
        Args:
            url: 视频链接
            format_id: 格式ID，如果不指定则下载最佳质量
            
        Returns:
            包含下载结果的字典
            {
                "filepath": 文件完整路径,
                "filename": 文件名
            }
            
        Raises:
            Exception: 下载失败时抛出异常
        """
        try:
            # 先获取视频信息以确定文件名和平台
            with YoutubeDL(self._get_ydl_opts()) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "video")
                # 清理文件名中的非法字符
                safe_title = re.sub(r'[<>:"/\\|?*]', "_", title)
            
            # 构建下载选项
            # 关键修复：如果指定了format_id，使用 format_id+bestaudio 合并音视频
            if format_id:
                # 对于B站等平台，format_id通常是纯视频流，需要合并音频
                format_spec = f"{format_id}+bestaudio/best"
            else:
                format_spec = "bestvideo+bestaudio/best"
            
            ydl_opts = {
                "format": format_spec,
                "outtmpl": os.path.join(self.DOWNLOAD_DIR, f"{safe_title}.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                # 关键修复：强制合并为mp4格式，确保音视频合并
                "merge_output_format": "mp4",
                # 如果ffmpeg可用，使用它来合并音视频
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }],
            }
            
            # 添加代理配置
            if self.proxy:
                ydl_opts["proxy"] = self.proxy
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # 如果输出不是mp4，强制改为mp4
                if not filename.endswith('.mp4'):
                    filename = filename.rsplit('.', 1)[0] + '.mp4'
                
                return {
                    "filepath": filename,
                    "filename": os.path.basename(filename)
                }
                
        except Exception as e:
            raise Exception(f"下载视频失败: {str(e)}")
    
    def get_direct_url(self, url: str, format_id: str = None) -> Dict[str, Any]:
        """
        获取视频直链
        
        功能说明:
            获取视频的直接下载链接，可用于浏览器直接下载
        
        Args:
            url: 视频链接
            format_id: 格式ID，如果不指定则获取最佳质量
            
        Returns:
            包含直链信息的字典
            {
                "direct_url": 直链URL,
                "ext": 文件扩展名,
                "filesize": 文件大小
            }
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        try:
            format_spec = format_id if format_id else "best"
            
            ydl_opts = {
                "format": format_spec,
                "quiet": True,
                "no_warnings": True,
            }
            
            # 添加代理配置
            if self.proxy:
                ydl_opts["proxy"] = self.proxy
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 获取指定格式的直链
                if format_id:
                    for fmt in info.get("formats", []):
                        if fmt.get("format_id") == format_id:
                            return {
                                "direct_url": fmt.get("url", ""),
                                "ext": fmt.get("ext", "mp4"),
                                "filesize": fmt.get("filesize") or fmt.get("filesize_approx", 0)
                            }
                
                # 如果没有指定格式或找不到，返回最佳格式的直链
                return {
                    "direct_url": info.get("url", ""),
                    "ext": info.get("ext", "mp4"),
                    "filesize": info.get("filesize") or info.get("filesize_approx", 0)
                }
                
        except Exception as e:
            raise Exception(f"获取直链失败: {str(e)}")


# 便捷函数，方便直接调用
def parse_video(url: str) -> Dict[str, Any]:
    """便捷函数：解析视频信息"""
    downloader = VideoDownloader()
    return downloader.parse_video(url)


def download_video(url: str, format_id: str = None) -> Dict[str, str]:
    """便捷函数：下载视频"""
    downloader = VideoDownloader()
    return downloader.download_video(url, format_id)


def get_direct_url(url: str, format_id: str = None) -> Dict[str, Any]:
    """便捷函数：获取直链"""
    downloader = VideoDownloader()
    return downloader.get_direct_url(url, format_id)
