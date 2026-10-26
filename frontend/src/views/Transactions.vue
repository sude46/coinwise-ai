<template>
  <div class="space-y-4">
    <!-- 顶部筛选栏 -->
    <div class="flex items-center gap-3">
      <input
        v-model="filters.yearMonth"
        type="month"
        class="h-10 px-3 rounded-card-sm bg-surface dark:bg-dark-surface border border-divider dark:border-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
      />
      <select
        v-model="filters.categoryId"
        class="h-10 px-3 rounded-card-sm bg-surface dark:bg-dark-surface border border-divider dark:border-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
      >
        <option :value="null">全部分类</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
      <button
        class="h-10 px-4 rounded-card-sm bg-brand text-white text-body font-medium active:scale-95 transition-transform"
        @click="loadTransactions"
      >
        筛选
      </button>
    </div>

    <!-- 搜索栏 -->
    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索备注..."
        class="w-full h-11 pl-10 pr-4 rounded-card-sm bg-surface dark:bg-dark-surface border border-divider dark:border-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none focus:border-brand transition-colors"
        @keyup.enter="onSearch"
      />
      <SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
    </div>

    <!-- 列表分组 -->
    <div class="space-y-4">
      <div
        v-for="group in groupedTransactions"
        :key="group.date"
      >
        <div class="sticky top-0 z-10 h-9 flex items-center px-3 bg-bg/90 dark:bg-dark-bg/90 backdrop-blur text-caption text-text-secondary dark:text-slate-400">
          {{ group.date }}
          <span class="ml-2 text-text-muted">共 {{ group.items.length }} 笔</span>
        </div>
        <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card divide-y divide-divider dark:divide-dark-divider">
          <div
            v-for="item in group.items"
            :key="item.id"
            class="flex items-center gap-3 px-4 py-3 transition-colors"
          >
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
              :class="item.type === 'income' ? 'bg-income/10 text-income' : 'bg-expense/10 text-expense'"
            >
              {{ item.category?.icon || (item.type === 'income' ? '💰' : '💳') }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-body font-medium text-text-primary dark:text-slate-100">
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
              <p class="text-caption text-text-secondary dark:text-slate-400">{{ formatTime(item.transaction_date) }}</p>
            </div>
            <div class="flex items-center gap-1 ml-1">
              <button class="p-2 text-info hover:bg-info/10 rounded-full transition-colors" @click="editItem(item)">
                <EditIcon class="w-4 h-4" />
              </button>
              <button class="p-2 text-expense hover:bg-expense/10 rounded-full transition-colors" @click="deleteItem(item)">
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="groupedTransactions.length === 0" class="text-center py-16">
        <p class="text-4xl mb-4">👛</p>
        <p class="text-body text-text-secondary dark:text-slate-400 mb-4">本月还没有记录</p>
        <button class="px-6 py-2.5 rounded-card-sm bg-brand text-white text-body font-medium" @click="appStore.openQuickAdd()">记一笔</button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="flex items-center justify-center gap-2 py-4">
      <button
        class="px-3 py-1.5 rounded-card-sm bg-surface dark:bg-dark-surface border border-divider dark:border-dark-divider text-body text-text-secondary dark:text-slate-400 disabled:opacity-50"
        :disabled="page === 1"
        @click="page--; loadTransactions()"
      >
        上一页
      </button>
      <span class="text-body text-text-secondary dark:text-slate-400">{{ page }} / {{ Math.ceil(total / size) }}</span>
      <button
        class="px-3 py-1.5 rounded-card-sm bg-surface dark:bg-dark-surface border border-divider dark:border-dark-divider text-body text-text-secondary dark:text-slate-400 disabled:opacity-50"
        :disabled="page >= Math.ceil(total / size)"
        @click="page++; loadTransactions()"
      >
        下一页
      </button>
    </div>

    <div class="h-20 md:hidden" />
  </div>
</template>

<script setup lang="jsx">
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { transactionApi, categoryApi, searchApi } from '@/api'
import { formatDate, formatDateTime, getCurrentYearMonth } from '@/utils/format'

const appStore = useAppStore()

const filters = reactive({
  yearMonth: getCurrentYearMonth(),
  categoryId: null
})
const searchQuery = ref('')
const transactions = ref([])
const categories = ref([])
const page = ref(1)
const size = ref(20)
const total = ref(0)

const groupedTransactions = ref([])

async function loadCategories() {
  try {
    const res = await categoryApi.list()
    categories.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function loadTransactions() {
  try {
    const [year, month] = filters.yearMonth.split('-')
    const start = new Date(year, month - 1, 1)
    const end = new Date(year, month, 0, 23, 59, 59)
    const res = await transactionApi.list({
      category_id: filters.categoryId,
      start_date: start.toISOString(),
      end_date: end.toISOString(),
      page: page.value,
      size: size.value
    })
    transactions.value = res.data.items || []
    total.value = res.data.total || 0
    groupByDate()
  } catch (e) {
    console.error('加载交易失败', e)
  }
}

async function onSearch() {
  if (!searchQuery.value.trim()) {
    loadTransactions()
    return
  }
  try {
    const res = await searchApi.search({ q: searchQuery.value, page: page.value, size: size.value })
    transactions.value = (res.data.hits || []).map(h => ({
      id: h.id,
      amount: h.amount,
      remark: h.highlight_remark || h.remark,
      transaction_date: h.transaction_date,
      category: { name: h.category_name },
      type: 'expense'
    }))
    total.value = res.data.total || 0
    groupByDate()
  } catch (e) {
    console.error('搜索失败', e)
  }
}

function groupByDate() {
  const groups = {}
  for (const item of transactions.value) {
    const date = formatDate(item.transaction_date)
    if (!groups[date]) groups[date] = []
    groups[date].push(item)
  }
  groupedTransactions.value = Object.entries(groups).map(([date, items]) => ({
    date,
    items
  }))
}

function editItem(item) {
  appStore.showToast('编辑功能开发中', 'info')
}

async function deleteItem(item) {
  if (!confirm('确定删除这条记录吗？')) return
  try {
    await transactionApi.delete(item.id)
    appStore.showToast('已删除', 'success')
    loadTransactions()
    window.dispatchEvent(new CustomEvent('transaction-created'))
  } catch (e) {
    appStore.showToast('删除失败', 'error')
  }
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  // 后端可能返回无时区字符串（如 "2026-06-06T03:44:00"），统一补 Z 按 UTC 解析
  const normalized = /[Z+\-]\d{2}:\d{2}$/.test(dateStr) || dateStr.endsWith('Z')
    ? dateStr : dateStr + 'Z'
  const d = new Date(normalized)
  // 如果时间是 UTC 午夜，显示 00:00
  if (d.getUTCHours() === 0 && d.getUTCMinutes() === 0) {
    return '00:00'
  }
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function SearchIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
}
function EditIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
}
function TrashIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
}

onMounted(() => {
  loadCategories()
  loadTransactions()
})
</script>
