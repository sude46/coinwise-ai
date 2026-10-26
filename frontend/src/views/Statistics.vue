<template>
  <div class="space-y-6">
    <!-- 顶部分段控制器 -->
    <div class="flex justify-center">
      <div class="inline-flex bg-bg dark:bg-dark-divider rounded-card-sm p-1">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="px-5 py-2 rounded-tag text-body font-medium transition-colors"
          :class="currentTab === tab.value
            ? 'bg-brand text-white shadow-btn'
            : 'text-text-secondary dark:text-slate-400 hover:text-text-primary'"
          @click="currentTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && !hasTransactions" class="text-center py-16">
      <p class="text-4xl mb-4">📊</p>
      <p class="text-body text-text-secondary dark:text-slate-400 mb-2">还没有记账数据</p>
      <p class="text-caption text-text-muted">记几笔账后，这里会显示你的消费分析</p>
    </div>

    <template v-else>
      <!-- 周期总览 -->
      <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">总收入</p>
            <p class="text-body font-semibold text-income tabular-nums">¥{{ totalIncome.toFixed(2) }}</p>
          </div>
          <div>
            <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">总支出</p>
            <p class="text-body font-semibold text-expense tabular-nums">¥{{ totalExpense.toFixed(2) }}</p>
          </div>
          <div>
            <p class="text-caption text-text-secondary dark:text-slate-400 mb-1">结余</p>
            <p class="text-body font-semibold tabular-nums" :class="balance >= 0 ? 'text-income' : 'text-expense'">¥{{ balance.toFixed(2) }}</p>
          </div>
        </div>
      </div>

      <!-- 收支对比 - 柱状图 -->
      <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-h2 text-text-primary dark:text-slate-100">收支走势</h3>
        </div>
        <div v-if="loading" class="h-[260px] shimmer rounded" />
        <div v-else-if="monthlyTrend.labels.length === 0" class="h-[260px] flex items-center justify-center text-text-secondary dark:text-slate-400 text-body">
          暂无跨月数据，下月后可查看走势
        </div>
        <div v-else class="h-[260px]">
          <canvas ref="barChart" />
        </div>
      </div>

      <!-- 支出结构 - 环形图 -->
      <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-h2 text-text-primary dark:text-slate-100">钱花哪了</h3>
        </div>
        <div v-if="totalExpense === 0" class="text-center py-6 text-text-secondary dark:text-slate-400 text-body">
          本月暂无支出
        </div>
        <div v-else class="flex flex-col md:flex-row items-center gap-6">
          <div class="w-48 h-48 relative">
            <canvas ref="doughnutChart" />
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-caption text-text-secondary dark:text-slate-400">总支出</span>
              <span class="text-data text-expense tabular-nums">¥{{ totalExpense.toFixed(2) }}</span>
            </div>
          </div>
          <div class="flex-1 w-full">
            <div class="flex flex-wrap gap-3">
              <div
                v-for="(item, idx) in categoryData.slice(0, 6)"
                :key="idx"
                class="flex items-center gap-2 text-caption"
              >
                <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: colors[idx % colors.length] }" />
                <span class="text-text-secondary dark:text-slate-400">{{ item.name }}</span>
                <span class="text-text-primary dark:text-slate-100 font-medium">{{ item.percent }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 收入来源 -->
      <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-h2 text-text-primary dark:text-slate-100">收入来源</h3>
        </div>
        <div v-if="incomeCategoryData.length === 0" class="text-center py-6 text-text-secondary dark:text-slate-400 text-body">
          本月暂无收入
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(item, idx) in incomeCategoryData"
            :key="idx"
            class="flex items-center gap-3"
          >
            <div class="w-9 h-9 rounded-full flex items-center justify-center text-sm shrink-0 bg-income/10 text-income">
              {{ item.icon || '💰' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <span class="text-body text-text-primary dark:text-slate-100">{{ item.name }}</span>
                <span class="text-body font-medium tabular-nums text-income">¥{{ item.amount.toFixed(2) }}</span>
              </div>
              <div class="h-2 bg-bg dark:bg-dark-divider rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full bg-income/60 transition-all"
                  :style="{ width: item.percent + '%' }"
                />
              </div>
            </div>
            <span class="text-caption text-text-secondary dark:text-slate-400 w-10 text-right">{{ item.percent }}%</span>
          </div>
        </div>
      </div>

      <!-- 支出排行 -->
      <div v-if="categoryData.length > 0" class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-h2 text-text-primary dark:text-slate-100">支出排行</h3>
        </div>
        <div class="space-y-3">
          <div
            v-for="(item, idx) in categoryData"
            :key="idx"
            class="flex items-center gap-3"
          >
            <div
              class="w-9 h-9 rounded-full flex items-center justify-center text-sm shrink-0"
              :class="idx < 3 ? 'bg-expense/10 text-expense' : 'bg-bg dark:bg-dark-divider text-text-secondary dark:text-slate-400'"
            >
              {{ item.icon || '💳' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <span class="text-body text-text-primary dark:text-slate-100">{{ item.name }}</span>
                <span class="text-body font-medium tabular-nums text-text-primary dark:text-slate-100">¥{{ item.amount.toFixed(2) }}</span>
              </div>
              <div class="h-2 bg-bg dark:bg-dark-divider rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full bg-expense/80 transition-all"
                  :style="{ width: item.percent + '%' }"
                />
              </div>
            </div>
            <span class="text-caption text-text-secondary dark:text-slate-400 w-10 text-right">{{ item.percent }}%</span>
          </div>
        </div>
      </div>

      <!-- 预算执行情况 -->
      <div class="bg-surface dark:bg-dark-surface rounded-card p-5 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-h2 text-text-primary dark:text-slate-100">预算执行</h3>
        </div>
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 4" :key="i" class="shimmer h-10 rounded" />
        </div>
        <div v-else-if="budgetData.length === 0" class="text-center py-6 text-text-secondary dark:text-slate-400">
          <p class="text-body">暂无预算设置</p>
          <p class="text-caption mt-1">去设置页添加分类预算</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="(item, idx) in budgetData"
            :key="idx"
            class="space-y-1.5"
          >
            <div class="flex items-center justify-between">
              <span class="text-body text-text-primary dark:text-slate-100">{{ item.name }}</span>
              <span class="text-caption text-text-secondary dark:text-slate-400">
                ¥{{ item.actual.toFixed(2) }} / ¥{{ item.budget.toFixed(2) }}
              </span>
            </div>
            <div class="h-2.5 bg-bg dark:bg-dark-divider rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="item.actual > item.budget ? 'bg-expense' : 'bg-ai'"
                :style="{ width: Math.min((item.actual / item.budget) * 100, 100) + '%' }"
              />
            </div>
            <p v-if="item.actual > item.budget" class="text-caption text-expense">
              超支 {{ ((item.actual - item.budget) / item.budget * 100).toFixed(1) }}%
            </p>
          </div>
        </div>
      </div>
    </template>

    <div class="h-20 md:hidden" />
  </div>
</template>

<script setup lang="jsx">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { transactionApi, budgetApi, categoryApi } from '@/api'
import { getCurrentYearMonth } from '@/utils/format'

const currentTab = ref('month')
const tabs = [
  { label: '本月', value: 'month' },
  { label: '本年', value: 'year' },
  { label: '自定义', value: 'custom' }
]

const loading = ref(true)
const doughnutChart = ref(null)
const barChart = ref(null)
let doughnutInstance = null
let barInstance = null

const colors = ['#EF4444', '#F59E0B', '#3B82F6', '#10B981', '#8B5CF6', '#EC4899']

const totalExpense = ref(0)
const totalIncome = ref(0)
const hasTransactions = ref(false)
const categoryData = ref([])
const incomeCategoryData = ref([])
const budgetData = ref([])
const monthlyTrend = ref({ labels: [], income: [], expense: [] })

const balance = computed(() => totalIncome.value - totalExpense.value)

function aggregateByCategory(transactions, categories, type = 'expense') {
  const catMap = {}
  let total = 0
  for (const t of transactions) {
    if (t.type !== type) continue
    total += Number(t.amount)
    const catId = t.category_id || 'other'
    const catName = t.category?.name || categories.find(c => c.id === t.category_id)?.name || '其他'
    const catIcon = t.category?.icon || categories.find(c => c.id === t.category_id)?.icon || (type === 'income' ? '💰' : '📦')
    if (!catMap[catId]) {
      catMap[catId] = { name: catName, amount: 0, icon: catIcon }
    }
    catMap[catId].amount += Number(t.amount)
  }
  const result = Object.values(catMap)
    .sort((a, b) => b.amount - a.amount)
    .map(item => ({
      ...item,
      percent: total > 0 ? Math.round((item.amount / total) * 100) : 0
    }))
  return { total, result }
}

function aggregateMonthly(transactions) {
  const monthMap = {}
  for (const t of transactions) {
    const d = new Date(t.transaction_date)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    if (!monthMap[key]) monthMap[key] = { income: 0, expense: 0 }
    if (t.type === 'income') monthMap[key].income += Number(t.amount)
    else monthMap[key].expense += Number(t.amount)
  }
  const sorted = Object.entries(monthMap).sort((a, b) => a[0].localeCompare(b[0])).slice(-6)
  return {
    labels: sorted.map(([k]) => `${parseInt(k.split('-')[1])}月`),
    income: sorted.map(([, v]) => v.income),
    expense: sorted.map(([, v]) => v.expense)
  }
}

function getDateRange(tab) {
  const now = new Date()
  if (tab === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)
    return { start_date: start.toISOString(), end_date: end.toISOString() }
  }
  if (tab === 'year') {
    const start = new Date(now.getFullYear(), 0, 1)
    const end = new Date(now.getFullYear(), 11, 31, 23, 59, 59)
    return { start_date: start.toISOString(), end_date: end.toISOString() }
  }
  return {}
}

async function loadData() {
  loading.value = true
  try {
    const dateFilter = getDateRange(currentTab.value)
    const [catRes, budgetRes] = await Promise.all([
      categoryApi.list(),
      budgetApi.list({ year_month: getCurrentYearMonth() })
    ])

    const categories = catRes.data || []

    let allTransactions = []
    let page = 1
    let totalPages = 0
    do {
      const res = await transactionApi.list({ page, size: 100, ...dateFilter })
      allTransactions = allTransactions.concat(res.data?.items || [])
      totalPages = res.data?.total || 0
      page++
    } while (allTransactions.length < totalPages)

    const transactions = allTransactions
    const budgets = budgetRes.data || []
    hasTransactions.value = transactions.length > 0

    // 支出结构 + 排行
    const { total: totalExp, result } = aggregateByCategory(transactions, categories, 'expense')
    totalExpense.value = totalExp
    categoryData.value = result

    // 收入来源
    const { total: totalInc, result: incResult } = aggregateByCategory(transactions, categories, 'income')
    totalIncome.value = totalInc
    incomeCategoryData.value = incResult

    // 收支走势
    monthlyTrend.value = aggregateMonthly(transactions)

    // 预算执行
    const expenseMap = {}
    for (const t of transactions) {
      if (t.type !== 'expense') continue
      const catId = t.category_id || 'other'
      if (!expenseMap[catId]) expenseMap[catId] = 0
      expenseMap[catId] += Number(t.amount)
    }

    budgetData.value = budgets.map(b => {
      const cat = categories.find(c => c.id === b.category_id)
      return {
        name: cat?.name || '未分类',
        budget: Number(b.limit_amount),
        actual: expenseMap[b.category_id] || 0
      }
    }).filter(b => b.budget > 0)

    initCharts()
  } catch (e) {
    console.error('加载统计失败', e)
  } finally {
    loading.value = false
  }
}

function initCharts() {
  nextTick(() => {
    try {
      if (doughnutChart.value && categoryData.value.length > 0) {
        if (doughnutInstance) doughnutInstance.destroy()
        const ctx = doughnutChart.value.getContext('2d')
        if (!ctx) return
        doughnutInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: categoryData.value.map(d => d.name),
            datasets: [{
              data: categoryData.value.map(d => d.amount),
              backgroundColor: colors,
              borderWidth: 0,
              hoverOffset: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: { legend: { display: false }, tooltip: { enabled: true } }
          }
        })
      }

      if (barChart.value && monthlyTrend.value.labels.length > 0) {
        if (barInstance) barInstance.destroy()
        const ctx = barChart.value.getContext('2d')
        if (!ctx) return
        barInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: monthlyTrend.value.labels,
            datasets: [
              {
                label: '收入',
                data: monthlyTrend.value.income,
                backgroundColor: '#10B981',
                borderRadius: 4
              },
              {
                label: '支出',
                data: monthlyTrend.value.expense,
                backgroundColor: '#EF4444',
                borderRadius: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { usePointStyle: true } } },
            scales: {
              x: { grid: { display: false } },
              y: { grid: { color: '#E2E8F0' }, ticks: { callback: v => '¥' + v } }
            }
          }
        })
      }
    } catch (e) {
      console.error('图表初始化失败:', e)
    }
  })
}

onMounted(loadData)
watch(currentTab, loadData)
</script>
