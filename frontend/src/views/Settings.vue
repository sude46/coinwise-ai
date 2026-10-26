<template>
  <div class="space-y-6">
    <h2 class="text-h1 text-text-primary dark:text-slate-100">设置</h2>

    <!-- 账户信息 -->
    <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card overflow-hidden">
      <div class="px-5 py-4 border-b border-divider dark:border-dark-divider flex items-center gap-3">
        <div class="w-12 h-12 rounded-full bg-brand/10 flex items-center justify-center text-xl">
          👤
        </div>
        <div>
          <p class="text-body font-medium text-text-primary dark:text-slate-100">{{ authStore.user?.username || '用户' }}</p>
          <p class="text-caption text-text-secondary dark:text-slate-400">{{ authStore.user?.email || '' }}</p>
        </div>
      </div>
    </div>

    <!-- 账户管理 -->
    <div class="space-y-1">
      <h3 class="text-caption text-text-secondary dark:text-slate-400 font-medium uppercase tracking-wider px-1">
        账户管理
      </h3>
      <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card overflow-hidden divide-y divide-divider dark:divide-dark-divider">
        <div
          v-for="acc in accounts"
          :key="acc.id"
          class="flex items-center justify-between px-5 py-3.5"
        >
          <div class="flex items-center gap-3">
            <span class="text-lg">{{ acc.icon || '💳' }}</span>
            <div>
              <span class="text-body text-text-primary dark:text-slate-100">{{ acc.name }}</span>
              <span class="text-caption text-text-secondary ml-2">{{ formatAmount(acc.balance) }}</span>
            </div>
          </div>
          <button class="text-expense text-sm" @click="deleteAccount(acc.id)">删除</button>
        </div>
        <div v-if="accounts.length === 0" class="px-5 py-4 text-caption text-text-secondary dark:text-slate-400">
          还没有账户，添加一个吧
        </div>
        <div class="px-5 py-4 space-y-3">
          <div class="flex gap-2">
            <input
              v-model="newAccount.name"
              type="text"
              placeholder="账户名称"
              class="flex-1 h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none"
            />
            <input
              v-model="newAccount.balance"
              type="number"
              placeholder="余额"
              class="w-28 h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none"
            />
          </div>
          <div class="flex gap-2">
            <select
              v-model="newAccount.account_type"
              class="h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
            >
              <option value="cash">现金</option>
              <option value="bank">银行卡</option>
              <option value="alipay">支付宝</option>
              <option value="wechat">微信</option>
              <option value="credit_card">信用卡</option>
            </select>
            <input
              v-model="newAccount.icon"
              type="text"
              placeholder="图标"
              class="w-24 h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none"
            />
            <button
              class="flex-1 h-10 rounded-card-sm bg-brand text-white text-body font-medium active:scale-95 transition-transform"
              @click="addAccount"
            >
              添加
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 预算设置 -->
    <div class="space-y-1">
      <h3 class="text-caption text-text-secondary dark:text-slate-400 font-medium uppercase tracking-wider px-1">
        预算设置（{{ currentYearMonth }}）
      </h3>
      <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card overflow-hidden divide-y divide-divider dark:divide-dark-divider">
        <div
          v-for="b in budgets"
          :key="b.id"
          class="flex items-center justify-between px-5 py-3.5"
        >
          <div class="flex items-center gap-3">
            <span class="text-body text-text-primary dark:text-slate-100">{{ getCategoryName(b.category_id) }}</span>
            <span class="text-caption text-text-secondary">¥{{ Number(b.limit_amount).toFixed(2) }}</span>
          </div>
          <button class="text-expense text-sm" @click="deleteBudget(b.id)">删除</button>
        </div>
        <div v-if="budgets.length === 0" class="px-5 py-4 text-caption text-text-secondary dark:text-slate-400">
          还没有设置预算
        </div>
        <div class="px-5 py-4 space-y-3">
          <div class="flex gap-2">
            <select
              v-model="newBudget.category_id"
              class="flex-1 h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
            >
              <option :value="null">选择分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <input
              v-model="newBudget.limit_amount"
              type="number"
              placeholder="预算金额"
              class="w-28 h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none"
            />
          </div>
          <button
            class="w-full h-10 rounded-card-sm bg-brand text-white text-body font-medium active:scale-95 transition-transform"
            @click="addBudget"
          >
            添加预算
          </button>
        </div>
      </div>
    </div>

    <!-- 导入导出 -->
    <div class="space-y-1">
      <h3 class="text-caption text-text-secondary dark:text-slate-400 font-medium uppercase tracking-wider px-1">
        导入导出
      </h3>
      <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card overflow-hidden divide-y divide-divider dark:divide-dark-divider">
        <div class="px-5 py-4 space-y-3">
          <p class="text-caption text-text-secondary">导入 CSV/OFX 交易记录</p>
          <div class="flex gap-2">
            <select
              v-model="importAccountId"
              class="h-10 px-3 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-primary dark:text-slate-100 outline-none"
            >
              <option :value="null">选择目标账户</option>
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
            </select>
            <label class="flex-1 h-10 flex items-center justify-center rounded-card-sm bg-brand/10 text-brand text-body font-medium cursor-pointer active:scale-95 transition-transform">
              <span>{{ importFileName || '选择文件' }}</span>
              <input type="file" accept=".csv,.ofx,.qfx" class="hidden" @change="handleFileSelect" />
            </label>
          </div>
          <button
            class="w-full h-10 rounded-card-sm bg-brand text-white text-body font-medium active:scale-95 transition-transform disabled:opacity-50"
            :disabled="!selectedFile || !importAccountId || importing"
            @click="importFile"
          >
            {{ importing ? '导入中...' : '开始导入' }}
          </button>
          <div v-if="importResult" class="text-caption" :class="importResult.error ? 'text-expense' : 'text-income'">
            {{ importResult.message }}
          </div>
        </div>
        <div class="px-5 py-4 space-y-3 border-t border-divider dark:border-dark-divider">
          <p class="text-caption text-text-secondary">导出交易记录</p>
          <button
            class="w-full h-10 rounded-card-sm bg-brand/10 text-brand text-body font-medium active:scale-95 transition-transform"
            @click="exportCSV"
          >
            导出 CSV
          </button>
        </div>
      </div>
    </div>

    <!-- 偏好设置 -->
    <div class="space-y-1">
      <h3 class="text-caption text-text-secondary dark:text-slate-400 font-medium uppercase tracking-wider px-1">
        偏好设置
      </h3>
      <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card overflow-hidden divide-y divide-divider dark:divide-dark-divider">
        <div class="flex items-center justify-between px-5 py-3.5">
          <div class="flex items-center gap-3">
            <MoonIcon class="w-5 h-5 text-text-secondary dark:text-slate-400" />
            <span class="text-body text-text-primary dark:text-slate-100">深色模式</span>
          </div>
          <ToggleSwitch :model-value="appStore.darkMode" @update:model-value="appStore.toggleDarkMode" />
        </div>
        <div class="flex items-center justify-between px-5 py-3.5">
          <div class="flex items-center gap-3">
            <BulbIcon class="w-5 h-5 text-text-secondary dark:text-slate-400" />
            <span class="text-body text-text-primary dark:text-slate-100">AI 建议</span>
          </div>
          <ToggleSwitch v-model="aiSuggestions" />
        </div>
      </div>
    </div>

    <!-- 关于 -->
    <div class="space-y-1">
      <h3 class="text-caption text-text-secondary dark:text-slate-400 font-medium uppercase tracking-wider px-1">
        关于
      </h3>
      <div class="bg-surface dark:bg-dark-surface rounded-card shadow-card overflow-hidden divide-y divide-divider dark:divide-dark-divider">
        <div class="px-5 py-3.5 flex items-center justify-between">
          <span class="text-body text-text-primary dark:text-slate-100">版本</span>
          <span class="text-caption text-text-secondary">v1.0.0</span>
        </div>
        <div class="px-5 py-3.5 flex items-center justify-between">
          <span class="text-body text-text-primary dark:text-slate-100">数据库迁移</span>
          <span class="text-caption text-income">Alembic 已配置</span>
        </div>
      </div>
    </div>

    <!-- 退出登录 -->
    <button
      class="w-full h-12 rounded-card bg-expense/10 text-expense font-medium text-body active:scale-[0.99] transition-transform"
      @click="logout"
    >
      退出登录
    </button>

    <div class="h-20 md:hidden" />
  </div>
</template>

<script setup lang="jsx">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { accountApi, budgetApi, categoryApi, importExportApi } from '@/api'
import { formatAmount, getCurrentYearMonth } from '@/utils/format'
import ToggleSwitch from '@/components/ToggleSwitch.vue'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const currentYearMonth = ref(getCurrentYearMonth())
const accounts = ref([])
const budgets = ref([])
const categories = ref([])
const aiSuggestions = ref(true)

const newAccount = ref({ name: '', account_type: 'cash', balance: '', icon: '💰' })
const newBudget = ref({ category_id: null, limit_amount: '', year_month: currentYearMonth.value })

const selectedFile = ref(null)
const importFileName = ref('')
const importAccountId = ref(null)
const importing = ref(false)
const importResult = ref(null)

function getCategoryName(id) {
  const cat = categories.value.find(c => c.id === id)
  return cat?.name || '未分类'
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    importFileName.value = file.name
    importResult.value = null
  }
}

async function importFile() {
  if (!selectedFile.value || !importAccountId.value) return
  importing.value = true
  importResult.value = null
  try {
    const res = await importExportApi.importFile(selectedFile.value, importAccountId.value)
    importResult.value = { message: res.data.message || `成功导入 ${res.data.imported} 条`, error: false }
    selectedFile.value = null
    importFileName.value = ''
  } catch (e) {
    importResult.value = { message: e.response?.data?.detail || '导入失败', error: true }
  } finally {
    importing.value = false
  }
}

async function exportCSV() {
  try {
    const res = await importExportApi.exportCSV()
    const blob = new Blob([res.data], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `coinwise_export_${currentYearMonth.value}.csv`
    a.click()
    URL.revokeObjectURL(url)
    appStore.showToast('导出成功', 'success')
  } catch (e) {
    appStore.showToast('导出失败', 'error')
  }
}

async function loadAccounts() {
  try {
    const res = await accountApi.list()
    accounts.value = res.data || []
  } catch (e) { console.error(e) }
}

async function addAccount() {
  if (!newAccount.value.name || !newAccount.value.balance) {
    appStore.showToast('请填写完整', 'error')
    return
  }
  try {
    await accountApi.create({
      name: newAccount.value.name,
      account_type: newAccount.value.account_type,
      balance: Number(newAccount.value.balance),
      icon: newAccount.value.icon || '💰',
      is_default: false
    })
    appStore.showToast('添加成功', 'success')
    newAccount.value = { name: '', account_type: 'cash', balance: '', icon: '💰' }
    loadAccounts()
  } catch (e) {
    appStore.showToast(e.response?.data?.detail || '添加失败', 'error')
  }
}

async function deleteAccount(id) {
  if (!confirm('确定删除该账户吗？')) return
  try {
    await accountApi.delete(id)
    appStore.showToast('已删除', 'success')
    loadAccounts()
  } catch (e) {
    appStore.showToast('删除失败', 'error')
  }
}

async function loadBudgets() {
  try {
    const res = await budgetApi.list({ year_month: currentYearMonth.value })
    budgets.value = res.data || []
  } catch (e) { console.error(e) }
}

async function addBudget() {
  if (!newBudget.value.category_id || !newBudget.value.limit_amount) {
    appStore.showToast('请填写完整', 'error')
    return
  }
  try {
    await budgetApi.create({
      category_id: newBudget.value.category_id,
      year_month: currentYearMonth.value,
      limit_amount: Number(newBudget.value.limit_amount)
    })
    appStore.showToast('添加成功', 'success')
    newBudget.value = { category_id: null, limit_amount: '', year_month: currentYearMonth.value }
    loadBudgets()
  } catch (e) {
    appStore.showToast(e.response?.data?.detail || '添加失败', 'error')
  }
}

async function deleteBudget(id) {
  if (!confirm('确定删除该预算吗？')) return
  try {
    await budgetApi.delete(id)
    appStore.showToast('已删除', 'success')
    loadBudgets()
  } catch (e) {
    appStore.showToast('删除失败', 'error')
  }
}

async function loadCategories() {
  try {
    const res = await categoryApi.list()
    categories.value = res.data || []
  } catch (e) { console.error(e) }
}

async function logout() {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  loadAccounts()
  loadBudgets()
  loadCategories()
})

function MoonIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
}
function BulbIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/><path d="M9 21h6"/></svg>
}
</script>
