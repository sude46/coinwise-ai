<template>
  <div class="prose prose-sm dark:prose-invert max-w-none" v-html="safeHtml" />
</template>

<script setup>
import { computed } from 'vue'
import { renderSafeMarkdown } from '@/utils/renderMarkdown'

const props = defineProps({
  content: { type: String, default: '' }
})

const safeHtml = computed(() => renderSafeMarkdown(props.content))
</script>
