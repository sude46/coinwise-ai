<template>
  <button
    class="fixed right-5 bottom-[140px] w-12 h-12 rounded-full bg-ai/20 dark:bg-ai/30 backdrop-blur flex items-center justify-center z-40 tap-highlight-transparent transition-all hover:scale-110"
    :class="[
      hasNew ? 'opacity-100 animate-pulse' : 'opacity-60 hover:opacity-100',
      'shadow-lg shadow-ai/20'
    ]"
    @click="$router.push('/ai-assistant')"
    title="AI 财务助手"
  >
    <BulbIcon class="w-6 h-6 text-ai" />
    <span
      v-if="hasNew"
      class="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-expense border-2 border-bg dark:border-dark-bg"
    />
    <!-- 提示角标 -->
    <span
      v-else
      class="absolute -top-1 -right-1 px-1.5 py-0.5 rounded-full bg-brand text-white text-[10px] font-bold"
    >
      AI
    </span>
  </button>
</template>

<script setup lang="jsx">
import { ref, onMounted } from 'vue'

// 首次访问时显示红点提示，localStorage 记录已读状态
const hasNew = ref(false)

onMounted(() => {
  const visited = localStorage.getItem('ai_visited')
  if (!visited) {
    hasNew.value = true
    // 5 秒后自动消失
    setTimeout(() => {
      hasNew.value = false
    }, 5000)
  }
})

function BulbIcon(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" />
      <path d="M9 21h6" />
    </svg>
  )
}
</script>
