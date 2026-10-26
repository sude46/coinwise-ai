import { describe, it, expect } from 'vitest'
import { renderSafeMarkdown } from './renderMarkdown'

describe('renderSafeMarkdown', () => {
  it('正常 Markdown 文本', () => {
    const input = '**粗体** 和 *斜体*'
    const result = renderSafeMarkdown(input)
    expect(result).toContain('<strong>粗体</strong>')
    expect(result).toContain('<em>斜体</em>')
  })

  it('过滤 script 标签', () => {
    const input = '正常文本<script>alert(1)</script>'
    const result = renderSafeMarkdown(input)
    expect(result).not.toContain('<script>')
    expect(result).toContain('正常文本')
  })

  it('过滤 style 标签', () => {
    const input = '<style>body{color:red}</style>内容'
    const result = renderSafeMarkdown(input)
    expect(result).not.toContain('<style>')
    expect(result).toContain('内容')
  })

  it('过滤事件属性', () => {
    const input = '<p onclick="evil()">点击</p>'
    const result = renderSafeMarkdown(input)
    expect(result).not.toContain('onclick')
    expect(result).toContain('点击')
  })

  it('过滤 javascript: 伪协议', () => {
    const input = '[链接](javascript:void(0))'
    const result = renderSafeMarkdown(input)
    expect(result).not.toContain('javascript:')
  })

  it('允许白名单标签', () => {
    const input = '# 标题\n\n> 引用\n\n```code```'
    const result = renderSafeMarkdown(input)
    expect(result).toContain('<h1>')
    expect(result).toContain('<blockquote>')
    expect(result).toContain('<code>')
  })

  it('空输入返回空字符串', () => {
    expect(renderSafeMarkdown('')).toBe('')
    expect(renderSafeMarkdown(null)).toBe('')
    expect(renderSafeMarkdown(undefined)).toBe('')
  })
})
