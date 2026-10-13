# -*- coding: utf-8 -*-
"""
诊断脚本：验证表单错误提示是否真的重复
详细输出 DOM 结构和截图
"""
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
USERNAME = "17695729351"
PASSWORD = "123456"
SHOT_DIR = f"E:/KiloAutoTest/cjgt_web/screenshots/form_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

import os
os.makedirs(SHOT_DIR, exist_ok=True)


async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    ctx = await browser.new_context(
        viewport={"width": 1440, "height": 900}, ignore_https_errors=True
    )
    page = await ctx.new_page()

    # ── 步骤1: 登录 ──
    print("=" * 60)
    print("步骤1: 登录")
    print("=" * 60)
    await page.goto(f"{BASE_URL}/adminLogin")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    await page.locator('input[placeholder="账号"]').fill(USERNAME)
    await page.locator('input[type="password"]').fill(PASSWORD)
    await page.locator('button:has-text("登 录")').click(force=True)
    await page.wait_for_timeout(5000)
    print(f"登录后URL: {page.url}")

    # ── 步骤2: 进入服务项目配置页 ──
    print("\n" + "=" * 60)
    print("步骤2: 进入服务项目配置页")
    print("=" * 60)
    await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    print(f"当前URL: {page.url}")

    # ── 步骤3: 点击新增服务项目 ──
    print("\n" + "=" * 60)
    print("步骤3: 点击新增服务项目按钮")
    print("=" * 60)
    await page.locator('button:has-text("新增服务项目")').click()
    await page.wait_for_timeout(2000)
    await page.screenshot(path=f"{SHOT_DIR}/01_modal_opened.png")
    print(f"截图: {SHOT_DIR}/01_modal_opened.png")

    # ── 步骤4: 不填表单直接点确认 ──
    print("\n" + "=" * 60)
    print("步骤4: 不填表单直接点确认按钮")
    print("=" * 60)
    confirm_btn = page.locator('.ant-modal button:has-text("确 认")')
    if await confirm_btn.count() == 0:
        confirm_btn = page.locator('.ant-modal button:has-text("确定")')
    if await confirm_btn.count() == 0:
        confirm_btn = page.locator('.ant-modal button:has-text("确 定")')
    print(f"找到确认按钮: {await confirm_btn.count() > 0}")
    await confirm_btn.first.click()
    await page.wait_for_timeout(1500)
    await page.screenshot(path=f"{SHOT_DIR}/02_after_submit_empty.png")
    print(f"截图: {SHOT_DIR}/02_after_submit_empty.png")

    # ── 步骤5: 详细分析DOM中的错误元素 ──
    print("\n" + "=" * 60)
    print("步骤5: 详细分析DOM中的错误元素")
    print("=" * 60)

    # 方法A: 查询 .ant-form-item-explain-error（Ant Design 4.x 的错误文本）
    errors_a = await page.evaluate("""
        () => {
            const els = document.querySelectorAll('.ant-form-item-explain-error');
            return Array.from(els).filter(e => e.offsetParent !== null).map(e => ({
                tag: e.tagName,
                class: e.className,
                text: e.textContent.trim(),
                parentClass: e.parentElement?.className || ''
            }));
        }
    """)
    print(f"\n方法A: 只查 .ant-form-item-explain-error")
    print(f"  数量: {len(errors_a)}")
    for e in errors_a:
        print(f"  - text='{e['text']}', class='{e['class']}', parent='{e['parentClass'][:60]}'")

    # 方法B: 查询 .ant-form-item-explain（外层容器）
    errors_b = await page.evaluate("""
        () => {
            const els = document.querySelectorAll('.ant-form-item-explain');
            return Array.from(els).filter(e => e.offsetParent !== null).map(e => ({
                tag: e.tagName,
                class: e.className,
                text: e.textContent.trim(),
                childCount: e.children.length
            }));
        }
    """)
    print(f"\n方法B: 只查 .ant-form-item-explain（容器）")
    print(f"  数量: {len(errors_b)}")
    for e in errors_b:
        print(f"  - text='{e['text']}', class='{e['class'][:60]}', childCount={e['childCount']}")

    # 方法C: 当前代码的方式（同时查两个选择器）
    errors_c = await page.evaluate("""
        () => {
            const els = document.querySelectorAll('.ant-form-item-explain-error, .ant-form-item-explain');
            return Array.from(els).filter(e => e.offsetParent !== null).map(e => e.textContent.trim());
        }
    """)
    print(f"\n方法C: 当前代码方式 (.ant-form-item-explain-error, .ant-form-item-explain)")
    print(f"  数量: {len(errors_c)}")
    print(f"  内容: {errors_c}")

    # 方法D: 完整的DOM结构
    print(f"\n方法D: 完整的表单错误DOM结构:")
    dom_info = await page.evaluate("""
        () => {
            const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
            return Array.from(formItems).map(item => {
                const label = item.querySelector('.ant-form-item-label')?.textContent.trim() || '';
                const explain = item.querySelector('.ant-form-item-explain');
                const explainError = item.querySelector('.ant-form-item-explain-error');
                return {
                    label: label,
                    hasExplain: !!explain,
                    explainText: explain?.textContent.trim() || '',
                    explainClass: explain?.className || '',
                    hasExplainError: !!explainError,
                    explainErrorText: explainError?.textContent.trim() || '',
                    explainErrorClass: explainError?.className || '',
                    explainHTML: explain?.outerHTML?.substring(0, 200) || ''
                };
            });
        }
    """)
    for item in dom_info:
        if item['hasExplain'] or item['hasExplainError']:
            print(f"\n  字段: {item['label']}")
            print(f"    .ant-form-item-explain 存在: {item['hasExplain']}, text='{item['explainText']}', class='{item['explainClass'][:60]}'")
            print(f"    .ant-form-item-explain-error 存在: {item['hasExplainError']}, text='{item['explainErrorText']}'")
            print(f"    HTML: {item['explainHTML'][:150]}")

    # ── 步骤6: 截取弹窗区域特写 ──
    print("\n" + "=" * 60)
    print("步骤6: 截取弹窗区域特写")
    print("=" * 60)
    modal = page.locator('.ant-modal')
    if await modal.count() > 0:
        await modal.first.screenshot(path=f"{SHOT_DIR}/03_modal_error_closeup.png")
        print(f"截图: {SHOT_DIR}/03_modal_error_closeup.png")

    print(f"\n所有截图保存在: {SHOT_DIR}")
    print("\n结论:")
    print(f"  .ant-form-item-explain-error 数量: {len(errors_a)}（实际错误条数）")
    print(f"  .ant-form-item-explain 数量: {len(errors_b)}（容器数）")
    print(f"  当前代码返回数量: {len(errors_c)}（重复！因为容器和文本都被匹配）")

    await browser.close()
    await pw.stop()


asyncio.run(main())
