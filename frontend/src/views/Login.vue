<template>
  <div class="min-h-screen flex bg-bg dark:bg-dark-bg">
    <!-- 左侧品牌区 (桌面端) -->
    <div class="hidden lg:flex lg:w-[40%] bg-brand items-center justify-center relative overflow-hidden">
      <div class="absolute inset-0 opacity-20">
        <svg viewBox="0 0 400 800" class="w-full h-full" preserveAspectRatio="none">
          <path d="M0 200 Q100 150 200 200 T400 200 L400 800 L0 800 Z" fill="#14B8A6"/>
          <path d="M0 300 Q150 250 300 300 T400 300 L400 800 L0 800 Z" fill="#0F766E" opacity="0.5"/>
          <path d="M0 400 Q200 350 400 400 L400 800 L0 800 Z" fill="#115E59" opacity="0.3"/>
        </svg>
      </div>
      <div class="relative z-10 text-white text-center px-10">
        <h1 class="text-4xl font-bold mb-4">CoinWise</h1>
        <p class="text-brand-lighter text-lg">个人智能记账平台</p>
        <p class="text-brand-lighter/80 mt-2 text-sm">让每一笔钱都清晰可见</p>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="flex-1 flex flex-col items-center justify-center px-6 py-12">
      <div class="w-full max-w-sm">
        <!-- 移动端 Logo -->
        <div class="lg:hidden text-center mb-8">
          <h1 class="text-2xl font-bold text-brand">CoinWise</h1>
          <span class="inline-block w-2 h-2 rounded-full bg-ai ml-1 align-top"/>
        </div>

        <h2 class="text-h1 text-text-primary dark:text-slate-100 mb-8 text-center lg:text-left">
          {{ isRegister ? '创建账本' : '进入账本' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div v-if="isRegister">
            <label class="block text-caption text-text-secondary dark:text-slate-400 mb-1.5">用户名</label>
            <input
              v-model="form.username"
              type="text"
              required
              class="w-full h-12 px-4 rounded-card-sm border border-divider dark:border-dark-divider bg-surface dark:bg-dark-surface text-body text-text-primary dark:text-slate-100 outline-none focus:border-brand focus:ring-3 focus:ring-brand/10 transition-all"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-caption text-text-secondary dark:text-slate-400 mb-1.5">
              {{ isRegister ? '邮箱' : '用户名或邮箱' }}
            </label>
            <input
              v-model="form.email"
              type="text"
              required
              class="w-full h-12 px-4 rounded-card-sm border border-divider dark:border-dark-divider bg-surface dark:bg-dark-surface text-body text-text-primary dark:text-slate-100 outline-none focus:border-brand focus:ring-3 focus:ring-brand/10 transition-all"
              :placeholder="isRegister ? '请输入邮箱' : '请输入用户名'"
            />
          </div>

          <div>
            <label class="block text-caption text-text-secondary dark:text-slate-400 mb-1.5">密码</label>
            <input
              v-model="form.password"
              type="password"
              required
              class="w-full h-12 px-4 rounded-card-sm border border-divider dark:border-dark-divider bg-surface dark:bg-dark-surface text-body text-text-primary dark:text-slate-100 outline-none focus:border-brand focus:ring-3 focus:ring-brand/10 transition-all"
              placeholder="请输入密码"
            />
          </div>

          <button
            type="submit"
            class="w-full h-12 rounded-card-sm bg-brand text-white font-medium shadow-btn hover:bg-brand-dark active:scale-[0.97] transition-all mt-2"
            :disabled="loading"
          >
            {{ loading ? '请稍候...' : (isRegister ? '创建账本' : '进入账本') }}
          </button>
        </form>

        <p class="mt-6 text-center text-body text-text-secondary dark:text-slate-400">
          {{ isRegister ? '已有账户？' : '还没有账户？' }}
          <button class="text-brand hover:underline" @click="isRegister = !isRegister">
            {{ isRegister ? '进入账本' : '创建账本' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="jsx">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const isRegister = ref(false)
const loading = ref(false)
const form = reactive({
  username: '',
  email: '',
  password: ''
})

async function handleSubmit() {
  loading.value = true
  try {
    if (isRegister.value) {
      await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password
      })
      appStore.showToast('注册成功，请登录', 'success')
      isRegister.value = false
    } else {
      await authStore.login({
        username: form.email,
        password: form.password
      })
      appStore.showToast('登录成功', 'success')
      router.push('/dashboard')
    }
  } catch (e) {
    const msg = e.response?.data?.detail || (isRegister.value ? '注册失败' : '登录失败')
    appStore.showToast(msg, 'error')
  } finally {
    loading.value = false
  }
}
</script>
