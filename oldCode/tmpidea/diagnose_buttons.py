# -*- coding: utf-8 -*-
"""诊断脚本：检查服务项目和知识库页面的操作按钮实际DOM结构"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
USERNAME = "17695729351"
PASSWORD = "123456"


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
    await page.locator('input[placeholder="账号"]').fill(USERNAME)
    await page.locator('input[type="password"]').fill(PASSWORD)
    await page.locator('button:has-text("登 录")').click(force=True)
    await page.wait_for_timeout(5000)
    print(f"登录后URL: {page.url}\n")

    for name, path in [
        ("服务项目", "/smart-service/project-config"),
        ("知识库", "/content-manage/knowledge"),
    ]:
        await page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        print(f"\n{'='*60}")
        print(f"页面: {name} ({path})")
        print(f"当前URL: {page.url}")
        print(f"{'='*60}")

        # 1. 查看表格中所有的链接和按钮
        actions = await page.evaluate("""
            () => {
                const tbody = document.querySelector('.ant-table-tbody');
                if (!tbody) return {error: '未找到表格tbody'};
                const els = tbody.querySelectorAll('a, button, .ant-switch, [class*="action"], [class*="operate"]');
                return Array.from(els).map(el => ({
                    tag: el.tagName,
                    text: (el.textContent || '').trim().substring(0, 30),
                    class: el.className.substring(0, 80),
                    href: el.getAttribute('href') || ''
                }));
            }
        """)
        print(f"\n表格内元素 (a/button/switch): {len(actions)} 个")
        for i, a in enumerate(actions[:20]):
            print(f"  [{i}] <{a['tag']}> text='{a['text']}' class='{a['class']}'")

        # 2. 查看表头和操作列
        ths = await page.evaluate("""
            () => {
                const thead = document.querySelector('.ant-table-thead');
                if (!thead) return [];
                return Array.from(thead.querySelectorAll('th')).map(th => th.textContent.trim());
            }
        """)
        print(f"\n表头列: {ths}")

        # 3. 查看是否有 ant-switch
        switch_count = await page.locator(".ant-switch").count()
        print(f"ant-switch 数量: {switch_count}")

        # 4. 查看 a:has-text("编辑") 等
        for txt in ["编辑", "修改", "删除", "禁用", "启用", "详情", "查看"]:
            cnt = await page.locator(f'a:has-text("{txt}"), button:has-text("{txt}")').count()
            if cnt > 0:
                print(f"  文本'{txt}': {cnt} 个")

        # 5. 表格行数
        rows = await page.locator(".ant-table-tbody tr").count()
        print(f"\n表格行数: {rows}")

        # 6. 截取操作列的HTML
        action_html = await page.evaluate("""
            () => {
                const tbody = document.querySelector('.ant-table-tbody');
                if (!tbody) return '';
                const firstRow = tbody.querySelector('tr');
                if (!firstRow) return '';
                const lastTd = firstRow.querySelector('td:last-child');
                return lastTd ? lastTd.innerHTML.substring(0, 500) : '无最后一列';
            }
        """)
        print(f"\n第一行最后一列(操作列)HTML:\n{action_html}")

    await browser.close()
    await pw.stop()


asyncio.run(main())
