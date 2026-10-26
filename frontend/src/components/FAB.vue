<template>
  <button
    class="fixed right-5 bottom-24 md:bottom-10 w-14 h-14 rounded-full bg-brand text-white flex items-center justify-center shadow-fab z-50 tap-highlight-transparent transition-transform active:scale-95 hover:bg-brand-dark"
    @click="appStore.openQuickAdd()"
  >
    <PlusIcon class="w-7 h-7" />
  </button>
</template>

<script setup lang="jsx">
import { useAppStore } from '@/stores/app'
const appStore = useAppStore()

function PlusIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/>
      <line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  )
}
</script>
