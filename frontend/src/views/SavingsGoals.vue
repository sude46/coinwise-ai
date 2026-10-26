<template>
  <div class="space-y-4">
    <!-- 顶部 -->
    <div class="flex items-center justify-between">
      <h2 class="text-h1 text-text-primary dark:text-slate-100">存钱计划</h2>
      <button
        class="h-10 px-4 rounded-card-sm bg-brand text-white text-body font-medium active:scale-95 transition-transform"
        @click="showCreate = true"
      >
        新建计划
      </button>
    </div>

    <!-- 计划列表 -->
    <div v-if="goals.length === 0" class="text-center py-16">
      <p class="text-4xl mb-4">🎯</p>
      <p class="text-body text-text-secondary dark:text-slate-400 mb-4">还没有存钱计划</p>
      <p class="text-caption text-text-muted">设定一个目标，比如"演唱会"或"旅游"，开始存钱吧</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="goal in goals"
        :key="goal.id"
        class="bg-surface dark:bg-dark-surface rounded-card shadow-card p-4 space-y-3"
      >
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-body font-semibold text-text-primary dark:text-slate-100">{{ goal.name }}</h3>
            <p class="text-caption text-text-secondary dark:text-slate-400">
              {{ formatDate(goal.start_date) }} ~ {{ formatDate(goal.end_date) }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-h2 text-brand font-bold">¥{{ Number(goal.current_amount || 0).toFixed(2) }}</p>
            <p class="text-caption text-text-secondary">/ ¥{{ Number(goal.target_amount).toFixed(2) }}</p>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="h-2 rounded-full bg-bg dark:bg-dark-divider overflow-hidden">
          <div
            class="h-full rounded-full bg-brand transition-all"
            :style="{ width: Math.min(progress(goal), 100) + '%' }"
          />
        </div>

        <div class="flex items-center justify-between text-caption">
          <span class="text-text-secondary dark:text-slate-400">进度 {{ progress(goal).toFixed(1) }}%</span>
          <span
            class="font-medium"
            :class="goal.status === 'completed' ? 'text-income' : 'text-text-secondary'"
          >
            {{ statusText(goal.status) }}
          </span>
        </div>

        <!-- 预测结果 -->
        <div v-if="predictions[goal.id]" class="rounded-card-sm bg-bg dark:bg-dark-divider p-3 space-y-1">
          <p class="text-caption font-medium" :class="riskColor(predictions[goal.id].risk)">
            {{ predictions[goal.id].message }}
          </p>
          <p v-if="predictions[goal.id].daily_required > 0" class="text-caption text-text-secondary">
            每日需存：¥{{ Number(predictions[goal.id].daily_required).toFixed(1) }}
            <span v-if="predictions[goal.id].ema_daily_avg > 0" class="ml-2">
              近期日均：¥{{ Number(predictions[goal.id].ema_daily_avg).toFixed(1) }}
            </span>
          </p>
        </div>

        <div class="flex gap-2 pt-1">
          <button
            class="flex-1 h-9 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-secondary dark:text-slate-400 hover:bg-divider transition-colors"
            @click="loadPredict(goal)"
          >
            预测分析
          </button>
          <button
            class="flex-1 h-9 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-secondary dark:text-slate-400 hover:bg-divider transition-colors"
            @click="deleteGoal(goal)"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 创建弹窗 -->
    <teleport to="body">
      <transition name="fade">
        <div v-if="showCreate" class="fixed inset-0 bg-black/30 z-[60] flex items-center justify-center p-4" @click="showCreate = false">
          <div class="bg-surface dark:bg-dark-surface rounded-card shadow-2xl w-full max-w-md p-6 space-y-4" @click.stop>
            <h3 class="text-h2 text-text-primary dark:text-slate-100">新建存钱计划</h3>
            <div class="space-y-3">
              <input v-model="form.name" placeholder="计划名称，如：演唱会" class="w-full h-11 px-3 rounded-card-sm bg-bg dark:bg-dark-divider border border-divider text-body outline-none focus:border-brand" />
              <input v-model="form.target_amount" type="number" placeholder="目标金额" class="w-full h-11 px-3 rounded-card-sm bg-bg dark:bg-dark-divider border border-divider text-body outline-none focus:border-brand" />
              <input v-model="form.start_date" type="date" class="w-full h-11 px-3 rounded-card-sm bg-bg dark:bg-dark-divider border border-divider text-body outline-none focus:border-brand" />
              <input v-model="form.end_date" type="date" class="w-full h-11 px-3 rounded-card-sm bg-bg dark:bg-dark-divider border border-divider text-body outline-none focus:border-brand" />
              <select v-model="form.category_id" class="w-full h-11 px-3 rounded-card-sm bg-bg dark:bg-dark-divider border border-divider text-body outline-none focus:border-brand">
                <option :value="null">关联消费分类（可选）</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div class="flex gap-2 pt-2">
              <button class="flex-1 h-10 rounded-card-sm bg-bg dark:bg-dark-divider text-body text-text-secondary" @click="showCreate = false">取消</button>
              <button class="flex-1 h-10 rounded-card-sm bg-brand text-white text-body font-medium" @click="submitCreate">创建</button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup lang="jsx">
import { ref, reactive, onMounted } from 'vue'
import { savingsGoalApi, categoryApi } from '@/api'
import { useAppStore } from '@/stores/app'
import { formatDate } from '@/utils/format'

const appStore = useAppStore()
const goals = ref([])
const categories = ref([])
const predictions = ref({})
const showCreate = ref(false)
const form = reactive({ name: '', target_amount: '', start_date: '', end_date: '', category_id: null })

async function loadGoals() {
  try {
    const res = await savingsGoalApi.list({ page: 1, size: 100 })
    goals.value = res.data.items || []
  } catch (e) {
    console.error(e)
  }
}

async function loadCategories() {
  try {
    const res = await categoryApi.list()
    categories.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadPredict(goal) {
  try {
    const res = await savingsGoalApi.predict(goal.id)
    predictions.value[goal.id] = res.data
  } catch (e) {
    appStore.showToast('预测失败', 'error')
  }
}

async function submitCreate() {
  if (!form.name || !form.target_amount || !form.start_date || !form.end_date) {
    appStore.showToast('请填写完整信息', 'error')
    return
  }
  try {
    await savingsGoalApi.create({
      name: form.name,
      target_amount: parseFloat(form.target_amount),
      start_date: new Date(form.start_date).toISOString(),
      end_date: new Date(form.end_date).toISOString(),
      category_id: form.category_id
    })
    appStore.showToast('创建成功', 'success')
    showCreate.value = false
    Object.assign(form, { name: '', target_amount: '', start_date: '', end_date: '', category_id: null })
    loadGoals()
  } catch (e) {
    const msg = e.response?.data?.detail
      ? (Array.isArray(e.response.data.detail)
          ? e.response.data.detail.map(d => d.msg || d).join('；')
          : e.response.data.detail)
      : (e.response?.data?.message || e.message || '创建失败')
    console.error('创建存钱计划失败:', e.response?.data || e)
    appStore.showToast(msg, 'error')
  }
}

async function deleteGoal(goal) {
  if (!confirm('确定删除这个存钱计划吗？已存入的金额不会退回。')) return
  try {
    await savingsGoalApi.delete(goal.id)
    appStore.showToast('已删除', 'success')
    loadGoals()
  } catch (e) {
    appStore.showToast('删除失败', 'error')
  }
}

function progress(goal) {
  const t = parseFloat(goal.target_amount) || 1
  const c = parseFloat(goal.current_amount) || 0
  return (c / t) * 100
}

function statusText(s) {
  const map = { active: '进行中', completed: '已达成', cancelled: '已取消' }
  return map[s] || s
}

function riskColor(risk) {
  const map = {
    low: 'text-income',
    medium: 'text-brand',
    high: 'text-ai',
    critical: 'text-expense',
    expired: 'text-expense',
    unknown: 'text-text-secondary'
  }
  return map[risk] || 'text-text-secondary'
}

onMounted(() => {
  loadGoals()
  loadCategories()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
