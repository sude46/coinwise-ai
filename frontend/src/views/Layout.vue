<template>
  <div class="min-h-screen bg-bg dark:bg-dark-bg">
    <SideNav />
    <main
      class="transition-all"
      :class="{
        'md:ml-[200px]': !isMobile,
        'pb-20': isMobile
      }"
    >
      <!-- 页面标题栏 -->
      <div class="md:hidden sticky top-0 z-30 bg-bg/90 dark:bg-dark-bg/90 backdrop-blur border-b border-divider dark:border-dark-divider">
        <div class="h-12 flex items-center px-5">
          <h1 class="text-body font-semibold text-text-primary dark:text-slate-100">
            {{ pageTitle }}
          </h1>
        </div>
      </div>
      <div class="max-w-[1200px] mx-auto px-5 py-6">
        <router-view />
      </div>
    </main>
    <BottomNav />
    <AIBubble v-if="isMobile" />
    <FAB />
    <QuickAddDrawer />
  </div>
</template>

<script setup lang="jsx">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useViewport } from '@/composables/useViewport'
import SideNav from '@/components/SideNav.vue'
import BottomNav from '@/components/BottomNav.vue'
import FAB from '@/components/FAB.vue'
import AIBubble from '@/components/AIBubble.vue'
import QuickAddDrawer from '@/components/QuickAddDrawer.vue'

const route = useRoute()
const { width } = useViewport()
const isMobile = computed(() => width.value < 768)

// 页面标题同步
const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '首页',
    '/transactions': '明细',
    '/statistics': '统计',
    '/savings-goals': '存钱计划',
    '/ai-assistant': 'AI 助手',
    '/settings': '设置'
  }
  return titles[route.path] || 'CoinWise'
})

// 首次访问 AI 助手时标记已读
watch(() => route.path, (path) => {
  if (path === '/ai-assistant') {
    localStorage.setItem('ai_visited', 'true')
  }
  // 同步 document title
  document.title = pageTitle.value + ' - CoinWise'
})
</script>
