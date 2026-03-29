<template>
  <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-border-light">
    <div class="max-w-7xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
            </svg>
          </div>
          <span class="text-lg font-bold text-text-primary">视频下载器</span>
        </div>

        <!-- 导航链接 -->
        <nav class="hidden md:flex items-center gap-6">
          <a href="#features" class="text-sm text-text-secondary hover:text-primary transition-colors">功能</a>
          <a href="#pricing" class="text-sm text-text-secondary hover:text-primary transition-colors">价格</a>
          <a href="#platforms" class="text-sm text-text-secondary hover:text-primary transition-colors">支持平台</a>
        </nav>

        <!-- 右侧按钮 -->
        <div class="flex items-center gap-3">
          <button 
            class="hidden sm:block text-sm text-text-secondary hover:text-primary transition-colors"
            @click="$emit('login')"
          >
            登录
          </button>
          <button 
            class="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary-dark rounded-full transition-colors"
            @click="$emit('register')"
          >
            免费使用
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
/**
 * 顶部导航组件
 * 
 * 功能说明:
 *   - 显示 Logo 和品牌名称
 *   - 提供导航链接
 *   - 登录/注册按钮
 * 
 * 事件:
 *   @login - 点击登录按钮时触发
 *   @register - 点击注册按钮时触发
 */
defineEmits(['login', 'register'])
</script>
