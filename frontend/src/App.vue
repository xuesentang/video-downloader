<template>
  <div class="min-h-screen flex flex-col bg-bg-main">
    <!-- 顶部导航 -->
    <AppHeader @login="showLogin" @register="showRegister" />
    
    <main class="flex-1">
      <!-- Hero 区域 -->
      <HeroSection
        @parse="handleParse"
        :loading="loading"
        :compact="!!videoData"
        :showSlogan="!videoData"
      />
      
      <!-- 视频结果区域 -->
      <section v-if="videoData" class="py-4 sm:py-6 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6">
          <div class="max-w-md mx-auto lg:max-w-none">
            <VideoResult
              :video="videoData"
              :downloading="downloading"
              @download="handleDownload"
              @summarize="handleSummarize"
            />
          </div>
        </div>
      </section>
      
      <!-- 功能亮点 -->
      <FeatureSection />
      
      <!-- 支持平台 -->
      <PlatformSection />
    </main>
    
    <!-- 页脚 -->
    <AppFooter />

    <!-- 提示消息 -->
    <div 
      v-if="toast.visible"
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl shadow-lg"
      :class="toast.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'"
    >
      <div class="flex items-center gap-2">
        <svg v-if="toast.type === 'error'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-medium">{{ toast.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import HeroSection from './components/HeroSection.vue'
import VideoResult from './components/VideoResult.vue'
import FeatureSection from './components/FeatureSection.vue'
import PlatformSection from './components/PlatformSection.vue'
import AppFooter from './components/AppFooter.vue'
import { parseVideo, downloadViaServer, getDirectUrl } from './api/video.js'

/**
 * 主应用组件
 * 
 * 功能说明:
 *   - 整合所有子组件
 *   - 管理全局状态（视频数据、加载状态等）
 *   - 处理视频解析和下载逻辑
 */

// 状态
const loading = ref(false)
const downloading = ref(false)
const videoData = ref(null)
const currentUrl = ref('')
const toast = ref({
  visible: false,
  type: 'success',
  message: ''
})

/**
 * 显示提示消息
 */
function showToast(message, type = 'success') {
  toast.value = {
    visible: true,
    type,
    message
  }
  setTimeout(() => {
    toast.value.visible = false
  }, 3000)
}

/**
 * 处理视频解析
 */
async function handleParse(url) {
  loading.value = true
  videoData.value = null
  currentUrl.value = url
  
  try {
    const res = await parseVideo(url)
    if (res.success) {
      videoData.value = res.data
      showToast('视频解析成功！')
    } else {
      showToast(res.error || '解析失败', 'error')
    }
  } catch (err) {
    showToast(err.message || '解析失败，请检查链接是否正确', 'error')
  } finally {
    loading.value = false
  }
}

/**
 * 处理视频下载
 */
async function handleDownload(formatId) {
  downloading.value = true
  
  try {
    // 先尝试获取直链
    const directRes = await getDirectUrl(currentUrl.value, formatId)
    
    if (directRes.success) {
      // 检查是否需要服务端代理下载
      if (directRes.data.proxy_download) {
        console.log('该视频需要通过服务端代理下载')
        // 继续执行下面的服务端下载逻辑
      } else if (directRes.data.url || directRes.data.direct_url) {
        // 使用直链下载
        const directUrl = directRes.data.url || directRes.data.direct_url
        const link = document.createElement('a')
        link.href = directUrl
        link.target = '_blank'
        link.download = `${videoData.value.title}.${directRes.data.ext || 'mp4'}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        showToast('开始下载！')
        downloading.value = false
        return
      }
    }
    
    // 使用服务端代理下载
    const response = await downloadViaServer(currentUrl.value, formatId)
    
    // 从响应头获取文件名
    const contentDisposition = response.headers.get('content-disposition')
    let filename = `${videoData.value.title}.mp4`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?([^;\n]+)/i)
      if (match) {
        filename = decodeURIComponent(match[1].replace(/"/g, ''))
      }
    }
    
    // 创建下载链接
    const blob = response.blob
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    showToast('下载完成！')
  } catch (err) {
    showToast(err.message || '下载失败', 'error')
  } finally {
    downloading.value = false
  }
}

/**
 * 处理 AI 总结
 */
function handleSummarize() {
  showToast('AI 总结功能即将上线，敬请期待！')
}

/**
 * 显示登录弹窗
 */
function showLogin() {
  showToast('登录功能即将上线！')
}

/**
 * 显示注册弹窗
 */
function showRegister() {
  showToast('注册功能即将上线！')
}
</script>

<style>
/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
