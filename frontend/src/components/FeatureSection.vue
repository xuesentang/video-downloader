<template>
  <section id="features" class="py-16 sm:py-20 bg-bg-section">
    <div class="max-w-7xl mx-auto px-4 sm:px-6">
      <!-- 标题 -->
      <div class="text-center mb-12">
        <h2 class="text-2xl sm:text-3xl font-bold text-text-primary mb-4">
          为什么选择我们的视频下载器
        </h2>
        <p class="text-text-secondary max-w-2xl mx-auto">
          简单易用、功能强大，满足你所有的视频下载需求
        </p>
      </div>

      <!-- 功能卡片 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="feature in features" 
          :key="feature.title"
          class="bg-white rounded-xl p-6 shadow-sm border border-border-light hover:shadow-md transition-shadow"
        >
          <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
            <component :is="feature.icon" class="w-6 h-6 text-primary" />
          </div>
          <h3 class="font-semibold text-text-primary text-lg mb-2">{{ feature.title }}</h3>
          <p class="text-text-secondary text-sm leading-relaxed">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
/**
 * 功能亮点区域组件
 * 
 * 功能说明:
 *   - 展示产品的核心功能特点
 *   - 使用卡片式布局
 */

// 功能列表
const features = [
  {
    title: '1800+ 平台支持',
    description: '支持 YouTube、Bilibili、抖音、TikTok、Twitter/X、Instagram 等主流视频平台',
    icon: 'PlatformIcon'
  },
  {
    title: '高清画质',
    description: '支持 4K、1080P、720P 等多种清晰度选择，满足你的不同需求',
    icon: 'QualityIcon'
  },
  {
    title: '极速下载',
    description: '采用多线程下载技术，充分利用带宽，下载速度快人一步',
    icon: 'SpeedIcon'
  },
  {
    title: '简单易用',
    description: '只需粘贴链接，一键解析下载，无需安装任何软件',
    icon: 'EasyIcon'
  },
  {
    title: '安全可靠',
    description: '不存储用户数据，临时文件自动清理，保护你的隐私安全',
    icon: 'SafeIcon'
  },
  {
    title: '全平台兼容',
    description: '支持 Windows、Mac、Linux，手机、平板、电脑都能用',
    icon: 'DeviceIcon'
  }
]
</script>

<script>
// 图标组件
const PlatformIcon = {
  render() {
    return h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24',
      class: this.$attrs.class 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2',
        d: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9' 
      })
    ])
  }
}

const QualityIcon = {
  render() {
    return h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24',
      class: this.$attrs.class 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2',
        d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' 
      })
    ])
  }
}

const SpeedIcon = {
  render() {
    return h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24',
      class: this.$attrs.class 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2',
        d: 'M13 10V3L4 14h7v7l9-11h-7z' 
      })
    ])
  }
}

const EasyIcon = {
  render() {
    return h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24',
      class: this.$attrs.class 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2',
        d: 'M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' 
      })
    ])
  }
}

const SafeIcon = {
  render() {
    return h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24',
      class: this.$attrs.class 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2',
        d: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' 
      })
    ])
  }
}

const DeviceIcon = {
  render() {
    return h('svg', { 
      fill: 'none', 
      stroke: 'currentColor', 
      viewBox: '0 0 24 24',
      class: this.$attrs.class 
    }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2',
        d: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z' 
      })
    ])
  }
}

import { h } from 'vue'
</script>
