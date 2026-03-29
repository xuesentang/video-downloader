<template>
  <div class="bg-white rounded-2xl shadow-lg p-6 max-w-lg w-full mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        代理设置
      </h2>
      <button 
        @click="$emit('close')"
        class="text-gray-400 hover:text-gray-600 transition-colors"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 平台说明 -->
    <div class="mb-6 p-4 bg-blue-50 rounded-xl">
      <h3 class="text-sm font-semibold text-blue-900 mb-2">需要代理的平台</h3>
      <div class="flex flex-wrap gap-2">
        <span class="px-2 py-1 bg-white rounded text-xs text-blue-700 font-medium">YouTube</span>
        <span class="px-2 py-1 bg-white rounded text-xs text-blue-700 font-medium">TikTok</span>
        <span class="px-2 py-1 bg-white rounded text-xs text-blue-700 font-medium">Twitter/X</span>
        <span class="px-2 py-1 bg-white rounded text-xs text-blue-700 font-medium">Instagram</span>
      </div>
      <p class="text-xs text-blue-600 mt-2">
        这些平台在中国大陆无法直接访问，需要配置代理才能下载视频。
      </p>
    </div>

    <!-- 自动检测 -->
    <div class="mb-6">
      <button
        @click="autoDetectProxy"
        :disabled="detecting"
        class="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <svg v-if="detecting" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {{ detecting ? '检测中...' : '自动检测常见代理' }}
      </button>
    </div>

    <!-- 代理配置表单 -->
    <div class="space-y-4">
      <!-- HTTP 代理 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">HTTP 代理</label>
        <input
          v-model="config.http_proxy"
          type="text"
          placeholder="http://127.0.0.1:7890"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
        />
        <p class="text-xs text-gray-500 mt-1">Clash、v2rayN 等工具默认 HTTP 代理端口</p>
      </div>

      <!-- HTTPS 代理 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">HTTPS 代理</label>
        <input
          v-model="config.https_proxy"
          type="text"
          placeholder="http://127.0.0.1:7890"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
        />
      </div>

      <!-- SOCKS5 代理 -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">SOCKS5 代理</label>
        <input
          v-model="config.socks_proxy"
          type="text"
          placeholder="socks5://127.0.0.1:10808"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
        />
        <p class="text-xs text-gray-500 mt-1">v2rayN、Shadowsocks 等工具默认 SOCKS5 端口</p>
      </div>
    </div>

    <!-- 测试连接 -->
    <div class="mt-6 flex gap-3">
      <button
        @click="testConnection"
        :disabled="testing || !hasAnyProxy"
        class="flex-1 py-2 px-4 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <svg v-if="testing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        {{ testing ? '测试中...' : '测试连接' }}
      </button>
      
      <button
        @click="saveConfig"
        :disabled="saving"
        class="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
    </div>

    <!-- 清除配置 -->
    <button
      v-if="hasActiveProxy"
      @click="clearConfig"
      class="mt-3 w-full py-2 px-4 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors"
    >
      清除代理配置
    </button>

    <!-- 测试结果 -->
    <div v-if="testResult" class="mt-4 p-3 rounded-lg" :class="testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      <div class="flex items-center gap-2">
        <svg v-if="testResult.success" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm">{{ testResult.message || testResult.error }}</span>
      </div>
    </div>

    <!-- 当前状态 -->
    <div v-if="activeProxy" class="mt-4 p-3 bg-gray-50 rounded-lg">
      <div class="flex items-center gap-2 text-sm text-gray-600">
        <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>当前代理: {{ activeProxy }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProxyConfig, setProxyConfig, clearProxyConfig, testProxy } from '../api/proxy.js'

/**
 * 代理设置组件
 * 
 * 功能说明:
 *   - 配置 HTTP/HTTPS/SOCKS5 代理
 *   - 自动检测常见代理工具
 *   - 测试代理连接
 *   - 保存/清除代理配置
 */

const emit = defineEmits(['close', 'update'])

// 状态
const config = ref({
  http_proxy: '',
  https_proxy: '',
  socks_proxy: ''
})
const activeProxy = ref('')
const detecting = ref(false)
const testing = ref(false)
const saving = ref(false)
const testResult = ref(null)

// 计算属性
const hasAnyProxy = computed(() => {
  return config.value.http_proxy || config.value.https_proxy || config.value.socks_proxy
})

const hasActiveProxy = computed(() => {
  return !!activeProxy.value
})

// 常见代理配置
const commonProxies = [
  { http: 'http://127.0.0.1:7890', https: 'http://127.0.0.1:7890', socks: '' },           // Clash 默认
  { http: 'http://127.0.0.1:7897', https: 'http://127.0.0.1:7897', socks: '' },           // Clash Verge
  { http: '', https: '', socks: 'socks5://127.0.0.1:10808' },                             // v2rayN 默认
  { http: '', https: '', socks: 'socks5://127.0.0.1:1080' },                              // SS/SSR 默认
  { http: 'http://127.0.0.1:10809', https: 'http://127.0.0.1:10809', socks: '' },         // v2rayN HTTP
]

// 加载配置
onMounted(async () => {
  try {
    const res = await getProxyConfig()
    if (res.success) {
      config.value.http_proxy = res.data.http_proxy || ''
      config.value.https_proxy = res.data.https_proxy || ''
      config.value.socks_proxy = res.data.socks_proxy || ''
      activeProxy.value = res.data.active_proxy || ''
    }
  } catch (err) {
    console.error('加载代理配置失败:', err)
  }
})

// 自动检测代理
async function autoDetectProxy() {
  detecting.value = true
  testResult.value = null
  
  try {
    for (const proxy of commonProxies) {
      const testProxyUrl = proxy.socks || proxy.https || proxy.http
      if (!testProxyUrl) continue
      
      try {
        const res = await testProxy(testProxyUrl, 'https://www.google.com')
        if (res.success) {
          config.value.http_proxy = proxy.http
          config.value.https_proxy = proxy.https
          config.value.socks_proxy = proxy.socks
          testResult.value = {
            success: true,
            message: `检测到可用代理: ${testProxyUrl}`
          }
          detecting.value = false
          return
        }
      } catch (e) {
        // 继续检测下一个
      }
    }
    
    testResult.value = {
      success: false,
      error: '未检测到可用代理，请手动配置'
    }
  } finally {
    detecting.value = false
  }
}

// 测试连接
async function testConnection() {
  testing.value = true
  testResult.value = null
  
  try {
    const proxy = config.value.socks_proxy || config.value.https_proxy || config.value.http_proxy
    if (!proxy) {
      testResult.value = {
        success: false,
        error: '请先输入代理地址'
      }
      return
    }
    
    const res = await testProxy(proxy, 'https://www.google.com')
    testResult.value = res
  } catch (err) {
    testResult.value = {
      success: false,
      error: `测试失败: ${err.message}`
    }
  } finally {
    testing.value = false
  }
}

// 保存配置
async function saveConfig() {
  saving.value = true
  
  try {
    const res = await setProxyConfig({
      http_proxy: config.value.http_proxy || null,
      https_proxy: config.value.https_proxy || null,
      socks_proxy: config.value.socks_proxy || null
    })
    
    if (res.success) {
      activeProxy.value = res.data.active_proxy
      testResult.value = {
        success: true,
        message: '代理配置已保存'
      }
      emit('update', res.data.active_proxy)
    } else {
      testResult.value = {
        success: false,
        error: res.error || '保存失败'
      }
    }
  } catch (err) {
    testResult.value = {
      success: false,
      error: `保存失败: ${err.message}`
    }
  } finally {
    saving.value = false
  }
}

// 清除配置
async function clearConfig() {
  try {
    const res = await clearProxyConfig()
    if (res.success) {
      config.value.http_proxy = ''
      config.value.https_proxy = ''
      config.value.socks_proxy = ''
      activeProxy.value = ''
      testResult.value = {
        success: true,
        message: '代理配置已清除'
      }
      emit('update', null)
    }
  } catch (err) {
    testResult.value = {
      success: false,
      error: `清除失败: ${err.message}`
    }
  }
}
</script>
