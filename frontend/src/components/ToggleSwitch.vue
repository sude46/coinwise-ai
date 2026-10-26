<template>
  <button
    class="relative w-11 h-6 rounded-full transition-colors duration-200"
    :class="modelValue ? 'bg-brand' : 'bg-text-muted/30 dark:bg-slate-600'"
    @click="$emit('update:modelValue', !modelValue)"
  >
    <span
      class="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200"
      :class="modelValue ? 'translate-x-5' : 'translate-x-0'"
    />
  </button>
</template>

<script setup lang="jsx">
defineProps({
  modelValue: { type: Boolean, default: false }
})
defineEmits(['update:modelValue'])
</script>
