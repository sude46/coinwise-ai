<template>
  <aside
    v-if="!isMobile"
    class="fixed left-0 top-0 bottom-0 w-[200px] bg-surface dark:bg-dark-surface border-r border-divider dark:border-dark-divider z-40 flex flex-col"
  >
    <div class="h-16 flex items-center px-5">
      <span class="text-brand font-bold text-xl">CoinWise</span>
      <span class="w-2 h-2 rounded-full bg-ai ml-1 mt-1"/>
    </div>
    <nav class="flex-1 px-3 py-4 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-card-sm text-body transition-colors"
        :class="route.path === item.path
          ? 'bg-brand/10 text-brand dark:bg-brand/20 dark:text-brand-light'
          : 'text-text-secondary dark:text-slate-400 hover:bg-bg dark:hover:bg-dark-divider'"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
    <div class="p-4 border-t border-divider dark:border-dark-divider">
      <button
        class="flex items-center gap-2 text-caption text-text-secondary dark:text-slate-400 hover:text-text-primary transition-colors"
        @click="appStore.toggleDarkMode"
      >
        <MoonIcon v-if="!appStore.isDark" class="w-4 h-4" />
        <SunIcon v-else class="w-4 h-4" />
        <span>{{ appStore.isDark ? '浅色模式' : '深色模式' }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="jsx">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useViewport } from '@/composables/useViewport'

const route = useRoute()
const appStore = useAppStore()
const { width } = useViewport()
const isMobile = computed(() => width.value < 768)

const navItems = [
  { name: 'Dashboard', path: '/dashboard', label: '首页', icon: HomeIcon },
  { name: 'Transactions', path: '/transactions', label: '明细', icon: ListIcon },
  { name: 'SavingsGoals', path: '/savings-goals', label: '存钱计划', icon: TargetIcon },
  { name: 'Statistics', path: '/statistics', label: '统计', icon: ChartIcon },
  { name: 'AiAssistant', path: '/ai-assistant', label: 'AI 助手', icon: AIIcon },
  { name: 'Settings', path: '/settings', label: '设置', icon: SettingsIcon }
]

function HomeIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
}
function ListIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
}
function ChartIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
}
function AIIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/><path d="M9 21h6"/></svg>
}
function SettingsIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.67 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.67a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
}
function TargetIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
}
function MoonIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
}
function SunIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
}
</script>
