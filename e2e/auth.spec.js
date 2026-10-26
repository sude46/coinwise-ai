import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('redirects unauthenticated user to login', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })

  test('shows login page', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('button')).toContainText(/登录|Login/i)
  })
})

test.describe('Navigation', () => {
  test('home page loads with login', async ({ page }) => {
    const response = await page.goto('/')
    expect(response?.ok()).toBeTruthy()
  })
})
