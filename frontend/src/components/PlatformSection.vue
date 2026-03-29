<template>
  <section id="platforms" class="py-16 sm:py-20 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6">
      <!-- 标题 -->
      <div class="text-center mb-12">
        <h2 class="text-2xl sm:text-3xl font-bold text-text-primary mb-4">
          支持 1800+ 视频平台
        </h2>
        <p class="text-text-secondary max-w-2xl mx-auto">
          覆盖全球主流视频平台，你想下载的这里都有
        </p>
      </div>

      <!-- 平台 Logo 墙 -->
      <div class="flex flex-wrap justify-center items-center gap-8 sm:gap-12">
        <div 
          v-for="platform in platforms" 
          :key="platform.name"
          class="flex flex-col items-center gap-2 group"
        >
          <div class="w-16 h-16 rounded-xl bg-bg-section flex items-center justify-center group-hover:bg-primary/10 transition-colors">
            <span class="text-2xl">{{ platform.icon }}</span>
          </div>
          <span class="text-sm text-text-secondary">{{ platform.name }}</span>
        </div>
      </div>

      <!-- 更多平台提示 -->
      <p class="text-center text-text-muted text-sm mt-10">
        以及更多 1800+ 个视频平台...
      </p>
    </div>
  </section>
</template>

<script setup>
/**
 * 支持平台展示组件
 * 
 * 功能说明:
 *   - 展示支持的主流视频平台
 *   - 使用图标墙形式展示
 */

// 平台列表（使用 emoji 作为图标）
const platforms = [
  { name: 'YouTube', icon: '▶️' },
  { name: 'Bilibili', icon: '📺' },
  { name: '抖音', icon: '🎵' },
  { name: 'TikTok', icon: '🎵' },
  { name: 'Twitter/X', icon: '🐦' },
  { name: 'Instagram', icon: '📷' },
  { name: 'Facebook', icon: '👥' },
  { name: 'Vimeo', icon: '🎬' },
]
</script>
