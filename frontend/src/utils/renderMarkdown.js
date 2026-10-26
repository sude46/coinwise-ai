/**
 * 安全 Markdown 渲染
 * 1. marked 转 HTML
 * 2. DOMPurify 过滤危险标签和事件属性
 */

import { marked } from 'marked'
import DOMPurify from 'dompurify'

const ALLOWED_TAGS = [
  'p', 'br', 'strong', 'em', 'ul', 'ol', 'li',
  'h1', 'h2', 'h3', 'blockquote', 'code', 'pre'
]

export function renderSafeMarkdown(raw) {
  if (!raw) return ''
  // marked 转 HTML
  const html = marked.parse(raw, { async: false, gfm: true })
  // DOMPurify 过滤
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR: [], // 不允许任何属性（防 onclick、onerror）
  })
  return clean
}
