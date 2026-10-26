<template>
  <div class="space-y-6">
    <!-- 顶部状态栏 (移动端) -->
    <div class="flex items-center justify-between md:hidden">
      <span class="text-caption text-text-secondary">{{ greeting }}，{{ authStore.user?.username || '用户' }}</span>
      <div class="flex items-center gap-3">
        <button class="text-text-secondary dark:text-slate-400" @click="appStore.toggleDarkMode">
          <MoonIcon v-if="!appStore.isDark" class="w-5 h-5" />
          <SunIcon v-else class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- 月度总览区 -->
    <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
      <p class="text-caption text-text-secondary dark:text-slate-400 mb-2">
        {{ currentYearMonth.replace('-', ' 年 ') }} 月收支
      </p>
      <div class="text-display text-brand dark:text-brand-light tabular-nums mb-4">
        {{ formatAmount(dashboardData?.balance || 0, dashboardData?.balance >= 0 ? 'income' : 'expense') }}
      </div>
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">本月收入</p>
          <p class="text-body font-semibold text-income tabular-nums">
            +{{ formatAmount(dashboardData?.month_income || 0, 'income').replace('+', '') }}
          </p>
        </div>
        <div>
          <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">本月支出</p>
          <p class="text-body font-semibold text-expense tabular-nums">
            -{{ formatAmount(dashboardData?.month_expense || 0, 'expense').replace('-', '') }}
          </p>
        </div>
      </div>
      <div class="border-t border-divider dark:border-dark-divider pt-4 grid grid-cols-2 gap-4">
        <div>
          <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">钱包剩余</p>
          <p class="text-body font-semibold text-text-primary dark:text-slate-100 tabular-nums">
            {{ formatAmount(dashboardData?.wallet_balance || 0) }}
          </p>
        </div>
        <div>
          <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">预算剩余</p>
          <p class="text-body font-semibold text-ai tabular-nums">
            {{ formatAmount(dashboardData?.budget_remaining || 0) }}
          </p>
          <div class="w-full h-1.5 bg-bg dark:bg-dark-divider rounded-full mt-1.5 overflow-hidden">
            <div
              class="h-full rounded-full transition-all"
              :class="budgetPercent > 100 ? 'bg-expense' : 'bg-ai'"
              :style="{ width: Math.min(budgetPercent, 100) + '%' }"
            />
          </div>
          <p class="text-caption text-text-muted mt-0.5">
            预算 {{ formatAmount(dashboardData?.total_budget || 0) }}
          </p>
          <div v-if="dashboardData?.budget_breakdown?.length" class="mt-3 space-y-2 border-t border-divider dark:border-dark-divider pt-3">
            <div
              v-for="b in dashboardData.budget_breakdown"
              :key="b.budget_id"
              class="flex items-center gap-2"
            >
              <span class="text-xs">{{ b.icon }}</span>
              <span class="text-caption text-text-secondary dark:text-slate-400 flex-1 truncate">{{ b.category_name }}</span>
              <span class="text-caption tabular-nums"
                :class="b.spent > b.limit_amount ? 'text-expense' : 'text-text-muted'"
              >
                {{ formatAmount(b.spent) }} / {{ formatAmount(b.limit_amount) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI 建议条 -->
    <div
      v-if="aiSuggestion"
      class="flex items-center gap-3 px-4 py-3 rounded-card bg-ai/10 dark:bg-ai/20 border border-ai/20"
    >
      <span class="text-lg">⚡</span>
      <p class="flex-1 text-body text-text-primary dark:text-slate-100">{{ aiSuggestion }}</p>
      <button class="text-sm text-ai font-medium" @click="$router.push('/ai-assistant')">查看</button>
      <button class="text-text-muted dark:text-slate-500" @click="aiSuggestion = ''">✕</button>
    </div>

    <!-- 快捷操作栏 -->
    <div class="flex gap-3 overflow-x-auto pb-1 scrollbar-hide">
      <button
        class="flex-shrink-0 flex items-center gap-2 px-5 py-2.5 rounded-card-sm bg-brand text-white text-body font-medium shadow-btn active:scale-95 transition-transform"
        @click="appStore.openQuickAdd()"
      >
        <PlusIcon class="w-4 h-4" /> 记一笔
      </button>
      <button
        v-for="action in quickActions"
        :key="action.label"
        class="flex-shrink-0 flex items-center gap-2 px-5 py-2.5 rounded-card-sm bg-surface dark:bg-dark-surface text-text-primary dark:text-slate-100 text-body border border-divider dark:border-dark-divider active:scale-95 transition-transform"
        @click="action.onClick"
      >
        <span>{{ action.icon }}</span> {{ action.label }}
      </button>
    </div>

    <!-- 趋势迷你图 -->
    <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-h2 text-text-primary dark:text-slate-100">近 7 日支出</h3>
      </div>
      <div class="h-[120px]">
        <canvas ref="trendChart" />
      </div>
    </div>

    <!-- 最近流水 -->
    <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-h2 text-text-primary dark:text-slate-100">最近交易</h3>
        <button class="text-body text-brand" @click="$router.push('/transactions')">查看全部</button>
      </div>
      <div class="space-y-3">
        <div
          v-for="(item, idx) in recentTransactions"
          :key="item.id"
          class="flex items-center gap-3 py-2"
          :style="{ animationDelay: idx * 50 + 'ms' }"
        >
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm shrink-0"
            :class="item.type === 'income' ? 'bg-income/20 text-income' : 'bg-expense/20 text-expense'"
          >
            {{ item.category?.icon || (item.type === 'income' ? '💰' : '💳') }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-body font-medium text-text-primary dark:text-slate-100 truncate">
              {{ item.category?.name || '未分类' }}
            </p>
            <p class="text-caption text-text-secondary dark:text-slate-400 truncate">{{ item.remark || '无备注' }}</p>
          </div>
          <div class="text-right shrink-0">
            <p
              class="text-body font-medium tabular-nums"
              :class="item.type === 'income' ? 'text-income' : 'text-expense'"
            >
              {{ item.type === 'income' ? '+' : '-' }}¥{{ Number(item.amount).toFixed(2) }}
            </p>
            <p class="text-caption text-text-secondary dark:text-slate-400">{{ formatDate(item.transaction_date) }}</p>
          </div>
        </div>
        <div v-if="recentTransactions.length === 0" class="text-center py-8 text-text-secondary dark:text-slate-400">
          <p class="text-body mb-2">本月还没有记录</p>
          <button class="text-brand text-body" @click="appStore.openQuickAdd()">记一笔</button>
        </div>
      </div>
    </div>

    <!-- 底部留白给 FAB -->
    <div class="h-20 md:hidden" />
  </div>
</template>

<script setup lang="jsx">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { dashboardApi, transactionApi } from '@/api'
import { formatAmount, formatDate, getCurrentYearMonth } from '@/utils/format'
import Chart from 'chart.js/auto'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const currentYearMonth = ref(getCurrentYearMonth())
const dashboardData = ref(null)
const recentTransactions = ref([])
const aiSuggestion = ref('')
const trendChart = ref(null)
let chartInstance = null

const budgetPercent = computed(() => {
  const total = dashboardData.value?.total_budget || 0
  const breakdown = dashboardData.value?.budget_breakdown || []
  const used = breakdown.reduce((s, b) => s + (b.spent || 0), 0)
  return total > 0 ? (used / total) * 100 : 0
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const quickActions = [
  { label: '转账', icon: '↔️', onClick: () => appStore.showToast('功能开发中', 'info') },
  { label: '报销', icon: '📄', onClick: () => appStore.showToast('功能开发中', 'info') },
  { label: '定期', icon: '📅', onClick: () => appStore.showToast('功能开发中', 'info') }
]

async function loadDashboard() {
  try {
    const res = await dashboardApi.get(currentYearMonth.value)
    dashboardData.value = res.data
    recentTransactions.value = res.data.recent_transactions || []
    await nextTick()
    initTrendChart()
  } catch (e) {
    console.error('加载仪表盘失败', e)
  }
}

function initTrendChart() {
  if (!trendChart.value) return
  if (chartInstance) chartInstance.destroy()

  const ctx = trendChart.value.getContext('2d')
  const daily = dashboardData.value?.daily_trend
  if (!daily || daily.length === 0) {
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: { labels: ['暂无'], datasets: [{ data: [0] }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    })
    return
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: daily.map(d => d.label),
      datasets: [{
        data: daily.map(d => d.expense),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239,68,68,0.05)',
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        x: { display: false },
        y: { display: false, min: 0 }
      },
      interaction: { intersect: false, mode: 'index' }
    }
  })
}

function onTransactionCreated() {
  loadDashboard()
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('transaction-created', onTransactionCreated)
})

onUnmounted(() => {
  window.removeEventListener('transaction-created', onTransactionCreated)
  if (chartInstance) chartInstance.destroy()
})

// Icons
function PlusIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
}
function MoonIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
}
function SunIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
