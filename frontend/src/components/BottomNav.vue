<template>
  <nav
    v-if="isMobile"
    class="fixed bottom-0 left-0 right-0 h-16 bg-surface dark:bg-dark-surface border-t border-divider dark:border-dark-divider z-50 flex items-center justify-around safe-area-pb"
  >
    <router-link
      v-for="item in navItems"
      :key="item.name"
      :to="item.path"
      class="flex flex-col items-center justify-center gap-1 w-16 tap-highlight-transparent transition-transform active:scale-95"
      :class="route.path === item.path ? 'text-brand' : 'text-text-secondary dark:text-slate-400'"
    >
      <component :is="item.icon" class="w-6 h-6" />
      <span class="text-[11px]">{{ item.label }}</span>
    </router-link>
  </nav>
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
  { name: 'SavingsGoals', path: '/savings-goals', label: '存钱', icon: TargetIcon },
  { name: 'AiAssistant', path: '/ai-assistant', label: 'AI', icon: AIIcon },
  { name: 'Settings', path: '/settings', label: '我的', icon: UserIcon }
]

function HomeIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  )
}
function ListIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="8" y1="6" x2="21" y2="6"/>
      <line x1="8" y1="12" x2="21" y2="12"/>
      <line x1="8" y1="18" x2="21" y2="18"/>
      <line x1="3" y1="6" x2="3.01" y2="6"/>
      <line x1="3" y1="12" x2="3.01" y2="12"/>
      <line x1="3" y1="18" x2="3.01" y2="18"/>
    </svg>
  )
}
function ChartIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  )
}
function AIIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/>
      <path d="M9 21h6"/>
    </svg>
  )
}
function TargetIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="6"/>
      <circle cx="12" cy="12" r="2"/>
    </svg>
  )
}
function UserIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  )
}
</script>
