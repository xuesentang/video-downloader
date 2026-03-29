/**
 * 视频相关 API 封装
 * 
 * 功能说明:
 *   - 视频解析
 *   - 视频下载
 *   - 获取直链
 * 
 * 注意事项:
 *   - 所有接口统一返回 Promise
 *   - 错误处理统一在调用处处理
 */

const API_BASE_URL = '/api'

/**
 * 解析视频信息
 * 
 * @param {string} url - 视频链接
 * @returns {Promise<Object>} - 返回视频信息
 * 
 * 示例:
 *   const result = await parseVideo('https://www.youtube.com/watch?v=xxx')
 *   console.log(result.data.title)
 */
export async function parseVideo(url) {
  const response = await fetch(`${API_BASE_URL}/parse`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail?.error || '解析失败')
  }

  return response.json()
}

/**
 * 下载视频（服务端代理模式）
 * 
 * @param {string} url - 视频链接
 * @param {string} formatId - 格式ID
 * @returns {Promise<Blob>} - 返回视频文件 Blob
 * 
 * 示例:
 *   const blob = await downloadViaServer('https://...', '137+140')
 *   // 使用 blob 创建下载链接
 */
export async function downloadViaServer(url, formatId) {
  const response = await fetch(`${API_BASE_URL}/download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, format_id: formatId }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail?.error || '下载失败')
  }

  return {
    blob: await response.blob(),
    headers: response.headers,
  }
}

/**
 * 获取视频直链
 * 
 * @param {string} url - 视频链接
 * @param {string} formatId - 格式ID
 * @returns {Promise<Object>} - 返回直链信息
 * 
 * 示例:
 *   const result = await getDirectUrl('https://...', '137')
 *   window.open(result.data.direct_url, '_blank')
 */
export async function getDirectUrl(url, formatId) {
  const response = await fetch(`${API_BASE_URL}/direct-url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, format_id: formatId }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail?.error || '获取直链失败')
  }

  return response.json()
}

/**
 * 获取缩略图代理 URL
 * 
 * @param {string} url - 原始缩略图 URL
 * @returns {string} - 代理后的 URL
 * 
 * 说明:
 *   由于某些平台的缩略图有防盗链，需要通过后端代理获取
 */
export function getThumbnailProxyUrl(url) {
  if (!url) return ''
  return `${API_BASE_URL}/proxy/thumbnail?url=${encodeURIComponent(url)}`
}
