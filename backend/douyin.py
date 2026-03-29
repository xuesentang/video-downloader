"""
抖音视频解析模块 - 基于 rathodpratham-dev/douyin_video_downloader

功能说明:
    - 使用抖音公开 API (iesdouyin.com) 解析视频
    - 无需登录态，自动处理 WAF 挑战
    - 支持短链接、分享链接、网页链接等多种格式
    - playwm -> play 替换获取无水印视频

核心流程:
    分享链接 → 302 重定向 → 提取 video_id → 调用公开 API → 获取无水印播放地址

参考项目:
    https://github.com/rathodpratham-dev/douyin_video_downloader (MIT 协议)
"""

import re
import json
import base64
import asyncio
import aiohttp
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from hashlib import sha256


# 抖音 API 配置
DOUYIN_API_URL = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/"

# 请求头配置
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.douyin.com/",
}

MOBILE_SHARE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.douyin.com/",
}

# 重试配置
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0

# URL 匹配正则
URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)


class DouyinError(Exception):
    """抖音解析基础异常"""
    pass


class InvalidDouyinURLError(DouyinError):
    """无效的抖音链接"""
    pass


class LinkResolutionError(DouyinError):
    """链接解析失败"""
    pass


class VideoIdExtractionError(DouyinError):
    """视频 ID 提取失败"""
    pass


class DouyinAPIError(DouyinError):
    """抖音 API 调用失败"""
    pass


@dataclass
class VideoInfo:
    """视频信息数据类"""
    id: str
    title: str
    thumbnail: str
    duration: int
    duration_string: str
    uploader: str
    platform: str
    view_count: int
    upload_date: str
    formats: list
    subtitles: list
    original_url: str
    download_url: str


def is_douyin_url(url: str) -> bool:
    """
    判断是否为抖音链接
    
    Args:
        url: 视频链接
        
    Returns:
        是否为抖音链接
    """
    patterns = [
        r'douyin\.com',
        r'v\.douyin\.com',
        r'iesdouyin\.com',
    ]
    url_lower = url.lower()
    return any(re.search(pattern, url_lower) for pattern in patterns)


def extract_first_url(text: str) -> str:
    """
    从文本中提取第一个 URL
    
    Args:
        text: 包含 URL 的文本
        
    Returns:
        提取的 URL
        
    Raises:
        InvalidDouyinURLError: 未找到有效 URL
    """
    match = URL_PATTERN.search(text)
    if not match:
        raise InvalidDouyinURLError("输入中未找到有效的 URL")
    
    candidate = match.group(0).strip().strip('"').strip("'")
    return candidate.rstrip(').,;!?\'"')


def extract_video_id(url: str) -> str:
    """
    从 URL 中提取抖音视频 ID
    
    Args:
        url: 抖音视频链接
        
    Returns:
        视频 ID
        
    Raises:
        VideoIdExtractionError: 无法提取视频 ID
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # 从查询参数中提取
    for key in ("modal_id", "item_ids", "group_id", "aweme_id"):
        values = query.get(key)
        if not values:
            continue
        match = re.search(r"(\d{8,24})", values[0])
        if match:
            return match.group(1)
    
    # 从路径中提取
    for pattern in (r"/video/(\d{8,24})", r"/note/(\d{8,24})", r"/(\d{8,24})(?:/|$)"):
        match = re.search(pattern, parsed.path)
        if match:
            return match.group(1)
    
    # 兜底方案：从整个 URL 中提取数字
    fallback = re.search(r"(?<!\d)(\d{8,24})(?!\d)", url)
    if fallback:
        return fallback.group(1)
    
    raise VideoIdExtractionError("无法从 URL 中提取视频 ID")


class DouyinParser:
    """
    抖音视频解析器
    
    功能说明:
        - 解析抖音分享链接，提取视频元信息
        - 自动处理短链接重定向
        - 自动解决 WAF 挑战
        - 无需 Cookie，开箱即用
    """
    
    def __init__(self):
        """初始化解析器"""
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(headers=DEFAULT_HEADERS)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        """确保 session 已创建"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=DEFAULT_HEADERS)
    
    async def parse(self, url: str) -> Dict[str, Any]:
        """
        解析抖音视频
        
        Args:
            url: 抖音视频链接，支持以下格式:
                - https://v.douyin.com/xxxxx (短链接)
                - https://www.douyin.com/video/xxxxx (网页链接)
                - https://www.douyin.com/discover?modal_id=xxxxx (发现页链接)
                - 抖音分享口令 (APP内复制)
        
        Returns:
            包含视频信息的字典（与其他平台格式保持一致）
            {
                "id": 视频ID,
                "title": 标题,
                "thumbnail": 缩略图URL,
                "duration": 时长（秒）,
                "duration_string": 格式化时长,
                "uploader": 作者昵称,
                "platform": "抖音",
                "view_count": 播放次数,
                "upload_date": 上传日期,
                "formats": [格式列表],
                "subtitles": [字幕列表],
                "original_url": 原始链接
            }
            
        Raises:
            DouyinError: 解析失败时抛出异常
        """
        await self._ensure_session()
        
        try:
            # 1. 提取分享链接中的 URL
            share_url = extract_first_url(url)
            
            # 2. 解析短链接重定向
            resolved_url = await self._resolve_redirect_url(share_url)
            
            # 3. 提取视频 ID
            video_id = extract_video_id(resolved_url)
            
            # 4. 获取视频信息
            item_info = await self._fetch_item_info(video_id, resolved_url)
            
            # 5. 转换为标准格式
            return self._convert_to_standard_format(item_info, url)
            
        except DouyinError:
            raise
        except Exception as e:
            raise DouyinError(f"解析抖音视频失败: {str(e)}")
    
    async def _resolve_redirect_url(self, share_url: str) -> str:
        """
        解析短链接重定向
        
        Args:
            share_url: 分享链接
            
        Returns:
            重定向后的真实 URL
        """
        last_error = None
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with self.session.get(
                    share_url,
                    allow_redirects=True,
                    headers=DEFAULT_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in RETRYABLE_STATUS_CODES:
                        raise aiohttp.ClientError(f"可重试的 HTTP {response.status}")
                    
                    response.raise_for_status()
                    
                    if not response.url:
                        raise LinkResolutionError("重定向 URL 为空")
                    
                    return str(response.url)
                    
            except Exception as exc:
                last_error = exc
                if attempt == MAX_RETRIES:
                    break
                
                sleep_seconds = BACKOFF_FACTOR * (2 ** (attempt - 1))
                await asyncio.sleep(sleep_seconds)
        
        raise LinkResolutionError("无法解析抖音分享链接") from last_error
    
    async def _fetch_item_info(self, video_id: str, resolved_url: str) -> Dict:
        """
        获取视频详细信息
        
        Args:
            video_id: 视频 ID
            resolved_url: 解析后的 URL
            
        Returns:
            视频信息字典
        """
        params = {"item_ids": video_id}
        
        try:
            data = await self._get_json_with_retry(DOUYIN_API_URL, params=params)
            
            if data.get("status_code") not in (0, None):
                raise DouyinAPIError(f"抖音 API 返回错误状态码: {data.get('status_code')}")
            
            item_list = data.get("item_list", [])
            if item_list:
                return item_list[0]
            
            raise DouyinAPIError("API 响应中未找到视频数据")
            
        except DouyinAPIError:
            # 如果公开 API 失败，尝试从分享页面解析
            return await self._fetch_item_info_from_share_page(video_id, resolved_url)
    
    async def _get_json_with_retry(self, url: str, params: Dict = None) -> Dict:
        """
        带重试的 JSON 请求
        
        Args:
            url: 请求 URL
            params: 查询参数
            
        Returns:
            JSON 响应数据
        """
        last_error = None
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with self.session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in RETRYABLE_STATUS_CODES:
                        raise aiohttp.ClientError(f"可重试的 HTTP {response.status}")
                    
                    response.raise_for_status()
                    
                    content = await response.text()
                    if not content:
                        raise ValueError("API 响应为空")
                    
                    return json.loads(content)
                    
            except Exception as exc:
                last_error = exc
                if attempt == MAX_RETRIES:
                    break
                
                sleep_seconds = BACKOFF_FACTOR * (2 ** (attempt - 1))
                await asyncio.sleep(sleep_seconds)
        
        raise DouyinAPIError("无法从抖音 API 获取数据") from last_error
    
    async def _fetch_item_info_from_share_page(self, video_id: str, resolved_url: str) -> Dict:
        """
        从分享页面解析视频信息（备用方案）
        
        Args:
            video_id: 视频 ID
            resolved_url: 解析后的 URL
            
        Returns:
            视频信息字典
        """
        share_url = self._build_share_page_url(video_id, resolved_url)
        html = await self._get_share_page_html(share_url)
        
        router_data = self._extract_router_data_json(html)
        if not router_data:
            raise DouyinAPIError("无法从分享页面提取数据")
        
        item_info = self._extract_item_info_from_router_data(router_data)
        if not item_info:
            raise DouyinAPIError("无法从分享页面提取视频信息")
        
        return item_info
    
    def _build_share_page_url(self, video_id: str, resolved_url: str) -> str:
        """构建分享页面 URL"""
        parsed = urlparse(resolved_url)
        if parsed.netloc and "iesdouyin.com" in parsed.netloc:
            return resolved_url
        return f"https://www.iesdouyin.com/share/video/{video_id}/"
    
    async def _get_share_page_html(self, share_url: str) -> str:
        """获取分享页面 HTML"""
        async with self.session.get(
            share_url,
            headers=MOBILE_SHARE_HEADERS,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response.raise_for_status()
            html = await response.text()
            
            # 检查是否需要解决 WAF 挑战
            if self._is_waf_challenge_page(html):
                solved = await self._solve_and_set_waf_cookie(html, share_url)
                if solved:
                    async with self.session.get(
                        share_url,
                        headers=MOBILE_SHARE_HEADERS,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.text()
            
            return html
    
    @staticmethod
    def _is_waf_challenge_page(html: str) -> bool:
        """检查是否为 WAF 挑战页面"""
        return "Please wait..." in html and "wci=" in html and "cs=" in html
    
    async def _solve_and_set_waf_cookie(self, html: str, page_url: str) -> bool:
        """
        解决 WAF 挑战
        
        抖音使用 JavaScript 挑战来防止爬虫，需要计算正确的 cookie 值
        """
        match = re.search(r'wci="([^"]+)"\s*,\s*cs="([^"]+)"', html)
        if not match:
            return False
        
        cookie_name, challenge_blob = match.groups()
        
        try:
            challenge_data = json.loads(self._decode_urlsafe_b64(challenge_blob).decode("utf-8"))
            prefix = self._decode_urlsafe_b64(challenge_data["v"]["a"])
            expected_digest = self._decode_urlsafe_b64(challenge_data["v"]["c"]).hex()
        except (KeyError, ValueError, TypeError):
            return False
        
        # 暴力破解挑战
        solved_value = None
        for candidate in range(1_000_001):
            digest = sha256(prefix + str(candidate).encode("utf-8")).hexdigest()
            if digest == expected_digest:
                solved_value = candidate
                break
        
        if solved_value is None:
            return False
        
        # 构建 cookie
        challenge_data["d"] = base64.b64encode(str(solved_value).encode("utf-8")).decode("utf-8")
        cookie_value = base64.b64encode(
            json.dumps(challenge_data, separators=(",", ":")).encode("utf-8")
        ).decode("utf-8")
        
        # 设置 cookie - 使用正确的 aiohttp cookie 设置方式
        from http.cookies import SimpleCookie
        simple_cookie = SimpleCookie()
        simple_cookie[cookie_name] = cookie_value
        self.session.cookie_jar.update_cookies(simple_cookie)
        
        return True
    
    @staticmethod
    def _decode_urlsafe_b64(value: str) -> bytes:
        """解码 URL-safe base64"""
        normalized = value.replace("-", "+").replace("_", "/")
        normalized += "=" * (-len(normalized) % 4)
        return base64.b64decode(normalized)
    
    def _extract_router_data_json(self, html: str) -> Dict:
        """从 HTML 中提取路由数据"""
        marker = "window._ROUTER_DATA = "
        start = html.find(marker)
        if start < 0:
            return {}
        
        index = start + len(marker)
        while index < len(html) and html[index].isspace():
            index += 1
        
        if index >= len(html) or html[index] != "{":
            return {}
        
        depth = 0
        in_string = False
        escaped = False
        
        for cursor in range(index, len(html)):
            char = html[cursor]
            
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    payload = html[index:cursor+1]
                    try:
                        return json.loads(payload)
                    except ValueError:
                        return {}
        
        return {}
    
    def _extract_item_info_from_router_data(self, router_data: Dict) -> Dict:
        """从路由数据中提取视频信息"""
        loader_data = router_data.get("loaderData", {})
        if not isinstance(loader_data, dict):
            return {}
        
        for node in loader_data.values():
            if not isinstance(node, dict):
                continue
            
            video_info_res = node.get("videoInfoRes", {})
            if not isinstance(video_info_res, dict):
                continue
            
            item_list = video_info_res.get("item_list", [])
            if item_list and isinstance(item_list[0], dict):
                return item_list[0]
        
        return {}
    
    def _convert_to_standard_format(self, item_info: Dict, original_url: str) -> Dict[str, Any]:
        """
        转换为标准格式（与其他平台保持一致）
        
        Args:
            item_info: 抖音 API 返回的视频信息
            original_url: 原始链接
            
        Returns:
            标准格式的视频信息字典
        """
        # 提取视频数据
        video_data = item_info.get("video", {})
        music_data = item_info.get("music", {})
        author_data = item_info.get("author", {})
        
        # 视频 ID
        video_id = item_info.get("aweme_id", "")
        
        # 标题
        title = item_info.get("desc", "")
        if not title and music_data:
            title = music_data.get("title", "抖音视频")
        if not title:
            title = "抖音视频"
        
        # 缩略图
        thumbnail = ""
        cover_data = video_data.get("cover", {})
        if cover_data:
            url_list = cover_data.get("url_list", [])
            if url_list:
                thumbnail = url_list[0]
        
        # 时长（抖音 API 返回的是毫秒）
        duration = video_data.get("duration", 0)
        if duration:
            duration = duration // 1000  # 转换为秒
        
        # 作者信息
        author_nickname = author_data.get("nickname", "未知作者")
        
        # 播放次数
        stats = item_info.get("statistics", {})
        view_count = stats.get("play_count", 0)
        
        # 获取无水印视频地址
        download_url = ""
        play_addr = video_data.get("play_addr", {})
        if play_addr:
            url_list = play_addr.get("url_list", [])
            if url_list:
                # playwm -> play 替换获取无水印视频
                download_url = url_list[0].replace("playwm", "play")
        
        # 构建格式列表（与其他平台保持一致）
        formats = []
        if download_url:
            formats.append({
                "format_id": "no_watermark_hd",
                "ext": "mp4",
                "resolution": "1080x1920",
                "height": 1920,
                "filesize": 0,
                "filesize_approx": play_addr.get("data_size", 0),
                "vcodec": "h264",
                "acodec": "aac",
                "label": "无水印高清 MP4",
                "url": download_url
            })
        
        # 如果没有提取到格式，添加默认格式
        if not formats:
            formats = [{
                "format_id": "default",
                "ext": "mp4",
                "resolution": "1080x1920",
                "height": 1920,
                "filesize": 0,
                "label": "默认 MP4",
                "url": download_url
            }]
        
        return {
            "id": video_id,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration,
            "duration_string": self._format_duration(duration),
            "uploader": author_nickname,
            "platform": "抖音",
            "view_count": view_count,
            "upload_date": "",
            "formats": formats,
            "subtitles": [],
            "original_url": original_url,
            "download_url": download_url  # 额外提供下载地址
        }
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """
        格式化时长
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化后的字符串，如 "3:32"
        """
        if not seconds:
            return ""
        minutes = seconds // 60
        secs = seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    async def get_download_url(self, url: str) -> str:
        """
        获取视频下载地址
        
        Args:
            url: 抖音视频链接
            
        Returns:
            无水印视频下载地址
        """
        try:
            result = await self.parse(url)
            return result.get("download_url", "")
        except Exception:
            return ""


# 便捷函数
async def parse_douyin(url: str) -> Dict[str, Any]:
    """
    便捷函数：解析抖音视频
    
    Args:
        url: 抖音视频链接
        
    Returns:
        视频信息字典
        
    示例:
        result = await parse_douyin("https://v.douyin.com/xxxxx")
        print(result["title"])
    """
    async with DouyinParser() as parser:
        return await parser.parse(url)
