<template>
  <teleport to="body">
    <transition name="drawer-overlay">
      <div
        v-if="appStore.showQuickAdd"
        class="fixed inset-0 bg-black/30 z-[60]"
        @click="appStore.closeQuickAdd"
      />
    </transition>
    <transition name="drawer">
      <div
        v-if="appStore.showQuickAdd"
        class="fixed left-0 right-0 bottom-0 md:left-auto md:right-4 md:bottom-4 md:w-[480px] md:rounded-card bg-surface dark:bg-dark-surface z-[70] rounded-t-card max-h-[85vh] md:max-h-[640px] flex flex-col shadow-2xl"
      >
        <div class="flex items-center justify-between px-5 pt-3 pb-2">
          <div class="w-10 h-1 rounded-full bg-divider dark:bg-dark-divider mx-auto" />
          <button class="text-text-secondary dark:text-slate-400 text-sm" @click="appStore.closeQuickAdd">关闭</button>
        </div>

        <div class="px-8 py-4 text-center">
          <div class="text-data text-text-primary dark:text-slate-100 tabular-nums">¥{{ amountDisplay }}</div>
        </div>

        <div class="px-5 py-3 border-t border-divider dark:border-dark-divider">
          <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            <button
              v-for="cat in categories"
              :key="cat.id"
              class="flex-shrink-0 flex flex-col items-center gap-1 px-4 py-2 rounded-tag transition-colors"
              :class="selectedCategory === cat.id
                ? 'bg-brand text-white'
                : 'bg-bg dark:bg-dark-divider text-text-secondary dark:text-slate-400'"
              @click="selectedCategory = cat.id"
            >
              <span class="text-lg">{{ cat.icon || '📦' }}</span>
              <span class="text-xs">{{ cat.name }}</span>
            </button>
            <div v-if="categories.length === 0" class="text-caption text-text-muted px-2 py-2">暂无分类</div>
          </div>
        </div>

        <div class="px-5 py-2">
          <select
            v-model="selectedAccount"
            class="w-full h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
          >
            <option :value="null">选择账户</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }} (¥{{ Number(acc.balance).toFixed(2) }})</option>
          </select>
        </div>

        <div class="px-5 py-2">
          <input
            v-model="remark"
            type="text"
            placeholder="写点什么...（可选）"
            class="w-full h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none"
          />
        </div>

        <div class="px-5 py-2">
          <select
            v-model="selectedGoal"
            class="w-full h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
            :disabled="goalsLoading"
          >
            <option :value="null">
              {{ goalsLoading ? '加载存钱计划中...' : '关联存钱计划（可选）' }}
            </option>
            <option v-for="goal in goals" :key="goal.id" :value="goal.id">{{ goal.name }}</option>
          </select>
        </div>

        <div class="px-5 py-2 flex gap-3">
          <input
            v-model="transactionDate"
            type="date"
            class="flex-1 h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
          />
          <select
            v-model="transactionType"
            class="h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
          >
            <option value="expense">支出</option>
            <option value="income">收入</option>
          </select>
        </div>

        <div class="px-5 py-3 grid grid-cols-4 gap-2">
          <button
            v-for="key in numpadKeys"
            :key="key"
            class="h-12 rounded-card-sm bg-bg dark:bg-dark-divider text-body font-medium text-text-primary dark:text-slate-100 tap-highlight-transparent active:scale-95 transition-transform flex items-center justify-center"
            :class="key === '确认' ? 'col-span-1 bg-brand text-white dark:bg-brand' : ''"
            @click="onNumpad(key)"
          >
            {{ key }}
          </button>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="jsx">
import { ref, computed, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { transactionApi, categoryApi, accountApi, savingsGoalApi } from '@/api'

const appStore = useAppStore()

const amount = ref('')
const selectedCategory = ref(null)
const selectedAccount = ref(null)
const remark = ref('')
const selectedGoal = ref(null)
const goals = ref([])
const goalsLoading = ref(false)
const transactionType = ref('expense')
const transactionDate = ref(new Date().toISOString().split('T')[0])
const categories = ref([])
const accounts = ref([])
const loading = ref(false)

const amountDisplay = computed(() => {
  if (!amount.value) return '0.00'
  const num = parseFloat(amount.value)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
})

const numpadKeys = ['7', '8', '9', '退格', '4', '5', '6', '清空', '1', '2', '3', '.', '0', '00', '确认']

function onNumpad(key) {
  if (key === '退格') {
    amount.value = amount.value.slice(0, -1)
  } else if (key === '清空') {
    amount.value = ''
  } else if (key === '确认') {
    submit()
  } else if (key === '.') {
    if (!amount.value.includes('.')) amount.value += '.'
  } else {
    if (amount.value.replace('.', '').length >= 8) return
    if (amount.value.includes('.') && amount.value.split('.')[1]?.length >= 2) return
    amount.value += key
  }
}

async function submit() {
  if (loading.value) return
  const num = parseFloat(amount.value)
  if (!num || num <= 0) {
    appStore.showToast('请输入金额', 'error')
    return
  }
  if (!selectedAccount.value) {
    appStore.showToast('请选择账户', 'error')
    return
  }
  loading.value = true
  try {
    await transactionApi.create({
      category_id: selectedCategory.value,
      account_id: selectedAccount.value,
      type: transactionType.value,
      amount: num,
      remark: remark.value || null,
      goal_id: selectedGoal.value,
      transaction_date: (() => {
        const now = new Date()
        const h = String(now.getHours()).padStart(2, '0')
        const m = String(now.getMinutes()).padStart(2, '0')
        const s = String(now.getSeconds()).padStart(2, '0')
        return new Date(transactionDate.value + 'T' + h + ':' + m + ':' + s).toISOString()
      })()
    })
    appStore.showToast('已记一笔', 'success')
    resetForm()
    appStore.closeQuickAdd()
    reloadDashboard()
  } catch (e) {
    appStore.showToast(e.response?.data?.detail || '记账失败', 'error')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  amount.value = ''
  remark.value = ''
  selectedGoal.value = null
  selectedCategory.value = null
  selectedAccount.value = null
}

function reloadDashboard() {
  window.dispatchEvent(new CustomEvent('transaction-created'))
}

async function loadCategories() {
  try {
    const res = await categoryApi.list()
    categories.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

async function loadAccounts() {
  try {
    const res = await accountApi.list()
    accounts.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('加载账户失败', e)
  }
}

async function loadGoals() {
  goalsLoading.value = true
  try {
    const res = await savingsGoalApi.list({ page: 1, size: 100 })
    const items = res.data?.items || res.data || []
    goals.value = items.filter(g => g.status === 'active')
  } catch (e) {
    console.error('加载存钱计划失败', e)
  } finally {
    goalsLoading.value = false
  }
}

watch(() => appStore.showQuickAdd, (open) => {
  if (open) {
    loadCategories()
    loadAccounts()
    loadGoals()
    transactionDate.value = new Date().toISOString().split('T')[0]
  }
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.drawer-overlay-enter-active, .drawer-overlay-leave-active { transition: opacity 0.2s; }
.drawer-overlay-enter-from, .drawer-overlay-leave-to { opacity: 0; }
.drawer-enter-active, .drawer-leave-active { transition: transform 0.3s ease-out; }
.drawer-enter-from, .drawer-leave-to { transform: translateY(100%); }
@media (min-width: 768px) {
  .drawer-enter-from, .drawer-leave-to { transform: translateX(100%); }
}
</style>
