<template>
  <router-view v-slot="{ Component }">
    <transition name="page" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
  <Toast />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const appStore = useAppStore()

onMounted(() => {
  appStore.initTheme()
})
</script>
