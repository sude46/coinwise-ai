<template>
  <teleport to="body">
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="appStore.toast.show"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-[100] px-5 py-3 rounded-card shadow-lg flex items-center gap-2 min-w-[200px] justify-center"
        :class="toastClass"
        role="alert"
        aria-live="polite"
      >
        <CheckIcon v-if="appStore.toast.type === 'success'" class="w-5 h-5 shrink-0" />
        <AlertIcon v-else-if="appStore.toast.type === 'error'" class="w-5 h-5 shrink-0" />
        <InfoIcon v-else class="w-5 h-5 shrink-0" />
        <span class="text-body font-medium">{{ appStore.toast.message }}</span>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="jsx">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const toastClass = computed(() => {
  const map = {
    success: 'bg-income/10 dark:bg-income/20 text-income border border-income/20',
    error: 'bg-expense/10 dark:bg-expense/20 text-expense border border-expense/20',
    info: 'bg-brand/10 dark:bg-brand/20 text-brand border border-brand/20'
  }
  return map[appStore.toast.type] || map.info
})

function CheckIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
}
function AlertIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
}
function InfoIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
}
</script>
