<template>
  <div class="h-[calc(100vh-120px)] md:h-[calc(100vh-80px)] flex flex-col">
    <!-- 顶部 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-h1 text-text-primary dark:text-slate-100">CoinWise 助手</h2>
    </div>

    <!-- 消息区 -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto space-y-4 pr-1 pb-4">
      <!-- 首次引导 -->
      <div v-if="messages.length === 0" class="text-center py-8">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-ai/10 flex items-center justify-center">
          <BulbIcon class="w-8 h-8 text-ai" />
        </div>
        <p class="text-body text-text-primary dark:text-slate-100 mb-2">我是你的财务助手</p>
        <p class="text-caption text-text-secondary dark:text-slate-400">可以帮你记账、分析消费、制定存钱策略</p>
      </div>

      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="flex gap-3"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <!-- AI 头像 -->
        <div
          v-if="msg.role === 'assistant'"
          class="w-8 h-8 rounded-full bg-ai/10 flex items-center justify-center shrink-0 mt-1"
        >
          <BulbIcon class="w-4 h-4 text-ai" />
        </div>

        <div
          class="max-w-[80%] px-4 py-3 rounded-2xl text-body"
          :class="msg.role === 'user'
            ? 'bg-surface dark:bg-dark-surface border-l-4 border-brand text-text-primary dark:text-slate-100'
            : 'bg-bg dark:bg-dark-divider text-text-primary dark:text-slate-100'"
        >
          <!-- 文本消息：安全渲染 Markdown -->
          <MarkdownRenderer v-if="msg.type === 'text'" :content="msg.content" />

          <!-- 记账确认卡片：不用 v-html -->
          <TransactionConfirm
            v-else-if="msg.type === 'transaction_confirm'"
            :data="msg.parsed_data"
            @confirm="confirmTransaction(msg, idx)"
            @cancel="cancelTransaction(idx)"
          />

          <!-- 默认文本 -->
          <p v-else>{{ msg.content }}</p>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-ai/10 flex items-center justify-center shrink-0">
          <BulbIcon class="w-4 h-4 text-ai animate-pulse" />
        </div>
        <div class="bg-bg dark:bg-dark-divider px-4 py-3 rounded-2xl">
          <div class="flex gap-1">
            <span class="w-2 h-2 rounded-full bg-text-muted animate-bounce" style="animation-delay: 0ms" />
            <span class="w-2 h-2 rounded-full bg-text-muted animate-bounce" style="animation-delay: 150ms" />
            <span class="w-2 h-2 rounded-full bg-text-muted animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷问题 -->
    <div v-if="messages.length === 0" class="flex gap-2 overflow-x-auto pb-3 scrollbar-hide">
      <button
        v-for="q in quickQuestions"
        :key="q"
        class="flex-shrink-0 px-4 py-2 rounded-full bg-brand/10 dark:bg-brand/20 text-brand text-caption font-medium hover:bg-brand/20 transition-colors"
        @click="sendMessage(q)"
      >
        {{ q }}
      </button>
    </div>

    <!-- 输入区 -->
    <div class="pt-3 border-t border-divider dark:border-dark-divider">
      <div class="flex items-center gap-2">
        <input
          v-model="input"
          type="text"
          placeholder="试试：今天中午和同事吃了海底捞，花了280"
          class="flex-1 h-11 px-4 rounded-full bg-surface dark:bg-dark-surface border border-divider dark:border-dark-divider text-body text-text-primary dark:text-slate-100 placeholder:text-text-muted outline-none focus:border-brand transition-colors"
          @keyup.enter="sendMessage()"
        />
        <button
          class="w-11 h-11 rounded-full bg-brand text-white flex items-center justify-center shrink-0 active:scale-95 transition-transform disabled:opacity-50"
          :disabled="!input.trim() || loading"
          @click="sendMessage()"
        >
          <SendIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="jsx">
import { ref, computed, watch, nextTick } from 'vue'
import { aiApi, transactionApi } from '@/api'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import MarkdownRenderer from '@/components/business/MarkdownRenderer.vue'
import TransactionConfirm from '@/components/business/TransactionConfirm.vue'
function decodeJwtSub(token) {
  try {
    return JSON.parse(atob(token.split('.')[1])).sub
  } catch {
    return 'anonymous'
  }
}

const appStore = useAppStore()
const authStore = useAuthStore()
const userId = computed(() => decodeJwtSub(authStore.accessToken))

function storageKey() {
  return `ai_messages_${userId.value}`
}
function convKey() {
  return `ai_conversation_id_${userId.value}`
}

const input = ref('')
const messages = ref(loadMessages())
const loading = ref(false)
const chatContainer = ref(null)
const conversationId = ref(localStorage.getItem(convKey()) || Date.now().toString())

function loadMessages() {
  try {
    return JSON.parse(localStorage.getItem(storageKey()) || '[]')
  } catch {
    return []
  }
}

function saveMessages() {
  localStorage.setItem(storageKey(), JSON.stringify(messages.value.slice(-50)))
  localStorage.setItem(convKey(), conversationId.value)
}

const quickQuestions = [
  '本月超支了吗？',
  '餐饮花了多少？',
  '怎么省钱？',
  '中午吃了碗面15块'
]

async function sendMessage(text) {
  const msg = text || input.value.trim()
  if (!msg || loading.value) return

  messages.value.push({ role: 'user', content: msg, type: 'text' })
  saveMessages()
  input.value = ''
  loading.value = true
  scrollToBottom()

  try {
    // 调用后端 AI 接口
    const res = await aiApi.chat({
      intent: inferIntent(msg),
      text: msg,
      conversation_id: conversationId.value
    })
    const data = res.data

    if (data.type === 'transaction_confirm') {
      messages.value.push({
        role: 'assistant',
        type: 'transaction_confirm',
        parsed_data: data.parsed_data,
        content: ''
      })
    } else {
      messages.value.push({
        role: 'assistant',
        type: 'text',
        content: data.content || '收到，我理解了。'
      })
    }
    saveMessages()
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      type: 'text',
      content: '抱歉，服务暂时不可用，请稍后再试。'
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function inferIntent(text) {
  // 简单意图识别：包含金额和吃喝/交通等关键词 → bookkeeping
  if (/\d+\s*(?:元|块|¥)/.test(text) && /吃|喝|买|花|地铁|公交|打车/.test(text)) {
    return 'bookkeeping'
  }
  if (/超支|预算|花了多少|消费/.test(text)) {
    return 'strategy'
  }
  if (/异常|奇怪|不对/.test(text)) {
    return 'anomaly_check'
  }
  if (/报告|总结|月度/.test(text)) {
    return 'report'
  }
  return 'strategy'
}

async function confirmTransaction(msg, idx) {
  const data = msg.parsed_data
  try {
    await transactionApi.create({
      type: data.type,
      amount: data.amount,
      remark: data.remark,
      category_id: null, // 用户可后续手动调整分类
      transaction_date: new Date().toISOString(),
      source: 'ai'
    })
    appStore.showToast('记账成功', 'success')
    // 替换确认卡片为成功提示
    messages.value.splice(idx, 1, {
      role: 'assistant',
      type: 'text',
      content: `✅ 已记账：${data.type === 'income' ? '收入' : '支出'} ¥${Number(data.amount).toFixed(2)}（${data.category_hint}）`
    })
    saveMessages()
    window.dispatchEvent(new CustomEvent('transaction-created'))
  } catch (e) {
    appStore.showToast(e.response?.data?.message || '记账失败', 'error')
  }
}

function cancelTransaction(idx) {
  messages.value.splice(idx, 1, {
    role: 'assistant',
    type: 'text',
    content: '已取消记账，你可以重新描述。'
  })
  saveMessages()
}

// 清除旧版共享 localStorage 残留，隔离不同用户
localStorage.removeItem('ai_messages')
localStorage.removeItem('ai_conversation_id')

// 用户切换时重载消息
watch(userId, () => {
  conversationId.value = localStorage.getItem(convKey()) || Date.now().toString()
  messages.value = loadMessages()
})

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function BulbIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"/><path d="M9 21h6"/></svg>
}
function SendIcon(props) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
