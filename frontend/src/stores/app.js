import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const darkMode = ref(localStorage.getItem('darkMode') === 'true')
  const showQuickAdd = ref(false)
  const toast = ref({ show: false, message: '', type: 'info' })

  const isDark = computed(() => darkMode.value)

  function toggleDarkMode() {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function initTheme() {
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    }
  }

  function openQuickAdd() {
    showQuickAdd.value = true
  }

  function closeQuickAdd() {
    showQuickAdd.value = false
  }

  function showToast(message, type = 'info') {
    toast.value = { show: true, message, type }
    setTimeout(() => {
      toast.value.show = false
    }, 2500)
  }

  return {
    darkMode,
    showQuickAdd,
    toast,
    isDark,
    toggleDarkMode,
    initTheme,
    openQuickAdd,
    closeQuickAdd,
    showToast
  }
})
