<template>
  <div class="rounded-card bg-surface dark:bg-dark-surface border border-brand/30 dark:border-brand/20 p-4 space-y-3">
    <div class="flex items-center gap-2 text-brand">
      <CheckIcon class="w-5 h-5" />
      <span class="text-body font-medium">确认记账</span>
    </div>

    <div class="space-y-2 text-body text-text-primary dark:text-slate-100">
      <div class="flex justify-between">
        <span class="text-text-secondary dark:text-slate-400">类型</span>
        <span :class="data.type === 'income' ? 'text-income' : 'text-expense'">
          {{ data.type === 'income' ? '收入' : '支出' }}
        </span>
      </div>
      <div class="flex justify-between">
        <span class="text-text-secondary dark:text-slate-400">金额</span>
        <span class="font-semibold">¥{{ Number(data.amount).toFixed(2) }}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-text-secondary dark:text-slate-400">分类</span>
        <span>{{ data.category_hint || '未分类' }}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-text-secondary dark:text-slate-400">备注</span>
        <span class="truncate max-w-[60%] text-right">{{ data.remark || '-' }}</span>
      </div>
    </div>

    <div class="flex gap-2 pt-1">
      <button
        class="flex-1 h-10 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-secondary dark:text-slate-400 hover:bg-divider dark:hover:bg-dark-divider transition-colors"
        @click="$emit('cancel')"
      >
        取消
      </button>
      <button
        class="flex-1 h-10 rounded-card-sm bg-brand text-white text-body font-medium hover:bg-brand/90 transition-colors"
        @click="$emit('confirm')"
      >
        确认记账
      </button>
    </div>
  </div>
</template>

<script setup lang="jsx">
defineProps({
  data: { type: Object, required: true }
})
defineEmits(['confirm', 'cancel'])

function CheckIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
}
</script>
