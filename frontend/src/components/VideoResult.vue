<template>
  <div class="bg-white rounded-xl shadow-md overflow-hidden border border-border-light">
    <!-- 视频缩略图 -->
    <div class="relative aspect-video bg-gray-100">
      <img 
        v-if="video.thumbnail"
        :src="thumbnailProxyUrl" 
        :alt="video.title"
        class="w-full h-full object-cover"
        @error="handleImageError"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-text-muted">
        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      
      <!-- 时长标签 -->
      <div v-if="video.duration_string" class="absolute bottom-2 right-2 px-2 py-1 bg-black/70 text-white text-xs rounded">
        {{ video.duration_string }}
      </div>
      
      <!-- 平台标签 -->
      <div class="absolute top-2 left-2 px-2 py-1 bg-primary/90 text-white text-xs rounded-full">
        {{ video.platform }}
      </div>
    </div>

    <!-- 视频信息 -->
    <div class="p-4">
      <h3 class="font-semibold text-text-primary text-lg mb-2 line-clamp-2" :title="video.title">
        {{ video.title }}
      </h3>
      
      <div class="flex items-center gap-4 text-sm text-text-secondary mb-4">
        <span v-if="video.uploader" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          {{ video.uploader }}
        </span>
        <span v-if="video.view_count" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          {{ formatViewCount(video.view_count) }}
        </span>
      </div>

      <!-- 格式选择 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-text-secondary mb-2">选择清晰度</label>
        <div class="relative">
          <select 
            v-model="selectedFormat"
            class="w-full px-3 py-2.5 bg-white border border-border rounded-lg text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary appearance-none cursor-pointer"
          >
            <option v-for="fmt in video.formats" :key="fmt.format_id" :value="fmt.format_id">
              {{ fmt.label }}
            </option>
          </select>
          <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <!-- 下载按钮 -->
      <div class="flex gap-2">
        <button
          @click="handleDownload"
          :disabled="downloading"
          class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-success hover:bg-success/90 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="downloading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          {{ downloading ? '下载中...' : '下载视频' }}
        </button>
        
        <button
          @click="$emit('summarize')"
          class="flex items-center justify-center gap-2 px-4 py-2.5 bg-primary/10 hover:bg-primary/20 text-primary font-medium rounded-lg transition-all"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          AI总结
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getThumbnailProxyUrl } from '../api/video.js'

/**
 * 视频结果展示组件
 * 
 * 功能说明:
 *   - 显示视频缩略图和元信息
 *   - 提供清晰度选择
 *   - 下载按钮
 *   - AI总结按钮
 * 
 * Props:
 *   @video - 视频信息对象
 *   @downloading - 是否正在下载中
 * 
 * Events:
 *   @download(formatId) - 点击下载按钮时触发
 *   @summarize - 点击AI总结按钮时触发
 */
const props = defineProps({
  video: {
    type: Object,
    required: true
  },
  downloading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['download', 'summarize'])

// 选中的格式
const selectedFormat = ref('')

// 缩略图代理 URL
const thumbnailProxyUrl = computed(() => {
  return getThumbnailProxyUrl(props.video.thumbnail)
})

// 监听视频变化，重置选中的格式
watch(() => props.video, (newVideo) => {
  if (newVideo.formats && newVideo.formats.length > 0) {
    // 默认选择最高清晰度
    selectedFormat.value = newVideo.formats[0].format_id
  }
}, { immediate: true })

/**
 * 格式化观看次数
 */
function formatViewCount(count) {
  if (!count) return '0'
  if (count >= 1000000) {
    return (count / 1000000).toFixed(1) + 'M'
  }
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'K'
  }
  return count.toString()
}

/**
 * 处理图片加载失败
 */
function handleImageError(e) {
  e.target.style.display = 'none'
}

/**
 * 处理下载
 */
function handleDownload() {
  if (selectedFormat.value) {
    emit('download', selectedFormat.value)
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
