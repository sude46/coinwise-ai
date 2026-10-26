import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TransactionConfirm from './TransactionConfirm.vue'

describe('TransactionConfirm', () => {
  const mockData = {
    type: 'expense',
    amount: 280,
    category_hint: '餐饮',
    remark: '海底捞聚餐'
  }

  it('渲染交易信息', () => {
    const wrapper = mount(TransactionConfirm, {
      props: { data: mockData }
    })
    expect(wrapper.text()).toContain('确认记账')
    expect(wrapper.text()).toContain('¥280.00')
    expect(wrapper.text()).toContain('餐饮')
    expect(wrapper.text()).toContain('海底捞聚餐')
  })

  it('点击确认触发 confirm 事件', async () => {
    const wrapper = mount(TransactionConfirm, {
      props: { data: mockData }
    })
    await wrapper.findAll('button').at(1).trigger('click')
    expect(wrapper.emitted()).toHaveProperty('confirm')
  })

  it('点击取消触发 cancel 事件', async () => {
    const wrapper = mount(TransactionConfirm, {
      props: { data: mockData }
    })
    await wrapper.findAll('button').at(0).trigger('click')
    expect(wrapper.emitted()).toHaveProperty('cancel')
  })

  it('收入类型显示绿色', () => {
    const wrapper = mount(TransactionConfirm, {
      props: { data: { ...mockData, type: 'income' } }
    })
    expect(wrapper.text()).toContain('收入')
  })
})
