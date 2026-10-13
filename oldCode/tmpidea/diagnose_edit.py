# -*- coding: utf-8 -*-
"""诊断编辑服务项目弹窗结构"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 900}, ignore_https_errors=True
    )
    page = await ctx.new_page()

    # 登录
    await page.goto(f"{BASE_URL}/adminLogin")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    await page.locator('input[placeholder="账号"]').fill("17695729351")
    await page.locator('input[type="password"]').fill("123456")
    await page.locator('button:has-text("登 录")').click(force=True)
    await page.wait_for_timeout(5000)

    # 导航到服务项目
    await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
    await page.wait_for_timeout(3000)

    # 点击第一个编辑按钮
    edit_btn = page.locator('button:has-text("编辑")')
    print(f"编辑按钮数量: {await edit_btn.count()}")
    await edit_btn.first.click()
    await page.wait_for_timeout(2000)

    # 检查弹窗是否打开
    modal_count = await page.locator(".ant-modal").count()
    print(f"弹窗数量: {modal_count}")

    # 查看弹窗内所有 input
    inputs = await page.evaluate("""
        () => {
            const modal = document.querySelector('.ant-modal');
            if (!modal) return [];
            const inputs = modal.querySelectorAll('input');
            return Array.from(inputs).map(i => ({
                id: i.id,
                type: i.type,
                placeholder: i.placeholder,
                codefield: i.getAttribute('codefield'),
                value: i.value.substring(0, 30)
            }));
        }
    """)
    print(f"\n弹窗内 inputs: {len(inputs)}")
    for i in inputs:
        print(f"  {i}")

    # 查看弹窗内所有 textarea
    textareas = await page.evaluate("""
        () => {
            const modal = document.querySelector('.ant-modal');
            if (!modal) return [];
            const tas = modal.querySelectorAll('textarea');
            return Array.from(tas).map(t => ({
                id: t.id,
                placeholder: t.placeholder,
                value: t.value.substring(0, 50)
            }));
        }
    """)
    print(f"\n弹窗内 textareas: {len(textareas)}")
    for t in textareas:
        print(f"  {t}")

    # 查看弹窗内所有按钮
    buttons = await page.evaluate("""
        () => {
            const modal = document.querySelector('.ant-modal');
            if (!modal) return [];
            const btns = modal.querySelectorAll('button');
            return Array.from(btns).map(b => b.textContent.trim());
        }
    """)
    print(f"\n弹窗内按钮: {buttons}")

    # 查看 codefield 属性的 input
    codefield_inputs = await page.evaluate("""
        () => {
            const modal = document.querySelector('.ant-modal');
            if (!modal) return [];
            return Array.from(modal.querySelectorAll('input[codefield]')).map(i => ({
                codefield: i.getAttribute('codefield'),
                id: i.id,
                value: i.value.substring(0, 30)
            }));
        }
    """)
    print(f"\ncodefield inputs: {len(codefield_inputs)}")
    for c in codefield_inputs:
        print(f"  {c}")

    await page.screenshot(path="edit_modal.png")
    print("\n截图: edit_modal.png")

    await browser.close()
    await pw.stop()


asyncio.run(main())
