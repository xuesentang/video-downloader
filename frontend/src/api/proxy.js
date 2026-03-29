/**
 * 代理配置 API 模块
 * 
 * 功能说明:
 *   - 获取代理配置
 *   - 设置代理配置
 *   - 测试代理连接
 *   - 获取平台支持列表
 */

import { API_BASE_URL } from './config.js'

/**
 * 获取当前代理配置
 * 
 * @returns {Promise<Object>} 代理配置信息
 */
export async function getProxyConfig() {
  const res = await fetch(`${API_BASE_URL}/api/config/proxy`)
  return res.json()
}

/**
 * 设置代理配置
 * 
 * @param {Object} config - 代理配置
 * @param {string} config.http_proxy - HTTP 代理地址
 * @param {string} config.https_proxy - HTTPS 代理地址
 * @param {string} config.socks_proxy - SOCKS5 代理地址
 * @returns {Promise<Object>} 设置结果
 */
export async function setProxyConfig(config) {
  const res = await fetch(`${API_BASE_URL}/api/config/proxy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  })
  return res.json()
}

/**
 * 清除代理配置
 * 
 * @returns {Promise<Object>} 清除结果
 */
export async function clearProxyConfig() {
  const res = await fetch(`${API_BASE_URL}/api/config/proxy`, {
    method: 'DELETE'
  })
  return res.json()
}

/**
 * 测试代理连接
 * 
 * @param {string} proxy - 代理地址
 * @param {string} testUrl - 测试目标 URL，默认 https://www.google.com
 * @returns {Promise<Object>} 测试结果
 */
export async function testProxy(proxy, testUrl = 'https://www.google.com') {
  const res = await fetch(`${API_BASE_URL}/api/config/proxy/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ proxy, test_url: testUrl })
  })
  return res.json()
}

/**
 * 获取支持的平台列表
 * 
 * @returns {Promise<Object>} 平台列表
 */
export async function getPlatforms() {
  const res = await fetch(`${API_BASE_URL}/api/platforms`)
  return res.json()
}
