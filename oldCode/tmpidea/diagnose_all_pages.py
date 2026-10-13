# -*- coding: utf-8 -*-
"""诊断所有页面的操作按钮、表单字段、搜索框等结构"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
USERNAME = "17695729351"
PASSWORD = "123456"

PAGES = [
    ("服务项目", "/smart-service/project-config"),
    ("合同服务", "/smart-service/contract-service"),
    ("经营范围", "/smart-service/scope-config"),
    ("知识库", "/content-manage/knowledge"),
]


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
    print(f"登录成功: {page.url}\n")

    for name, path in PAGES:
        await page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        print(f"\n{'='*70}")
        print(f"页面: {name} ({path})")
        print(f"{'='*70}")

        # 1. 顶部工具栏按钮
        toolbar = await page.evaluate("""
            () => {
                const toolbar = document.querySelector('.ant-table-tool-bar, .jeecg-basic-table-header, .ant-pro-table-list-toolbar');
                if (!toolbar) return '无工具栏';
                const btns = toolbar.querySelectorAll('button');
                return Array.from(btns).map(b => b.textContent.trim());
            }
        """)
        print(f"工具栏按钮: {toolbar}")

        # 2. 搜索框
        search = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('.ant-table-filter-trigger-container input, .ant-input, input[placeholder*="搜索"], input[placeholder*="请输入"]');
                return Array.from(inputs).filter(i => i.offsetParent !== null).map(i => ({
                    placeholder: i.placeholder,
                    id: i.id,
                    class: i.className.substring(0, 50)
                })).slice(0, 5);
            }
        """)
        print(f"搜索/输入框: {search}")

        # 3. 表头
        ths = await page.evaluate("""
            () => {
                const thead = document.querySelector('.ant-table-thead');
                if (!thead) return [];
                return Array.from(thead.querySelectorAll('th')).map(th => th.textContent.trim());
            }
        """)
        print(f"表头列: {ths}")

        # 4. 操作列按钮（第一行）
        actions = await page.evaluate("""
            () => {
                const tbody = document.querySelector('.ant-table-tbody');
                if (!tbody) return [];
                const firstRow = tbody.querySelector('tr');
                if (!firstRow) return [];
                const tds = firstRow.querySelectorAll('td');
                if (tds.length === 0) return [];
                const lastTd = tds[tds.length - 1];
                const btns = lastTd.querySelectorAll('button, a');
                return Array.from(btns).map(b => ({
                    tag: b.tagName,
                    text: b.textContent.trim(),
                    class: b.className.substring(0, 60)
                }));
            }
        """)
        print(f"操作列按钮(第一行): {actions}")

        # 5. 表格行数
        rows = await page.locator(".ant-table-tbody tr").count()
        print(f"表格行数: {rows}")

        # 6. 分页
        pagination = await page.evaluate("""
            () => {
                const p = document.querySelector('.ant-pagination');
                if (!p) return '无分页';
                const total = p.querySelector('.ant-pagination-total-text');
                const items = p.querySelectorAll('.ant-pagination-item');
                return {
                    total: total ? total.textContent.trim() : '无总数',
                    pages: items.length,
                    current: p.querySelector('.ant-pagination-item-active')?.textContent || 'unknown'
                };
            }
        """)
        print(f"分页: {pagination}")

        # 7. 新增弹窗表单字段
        # 尝试点击新增按钮
        add_clicked = False
        for btn_text in ["新增服务项目", "新增合同服务", "新增经营范围", "新增知识库", "新增"]:
            btn = page.locator(f'button:has-text("{btn_text}")')
            if await btn.count() > 0:
                await btn.first.click()
                await page.wait_for_timeout(2000)
                add_clicked = True
                break

        if add_clicked:
            modal_fields = await page.evaluate("""
                () => {
                    const modal = document.querySelector('.ant-modal');
                    if (!modal) return '弹窗未打开';
                    const labels = modal.querySelectorAll('.ant-form-item-label label');
                    const required = modal.querySelectorAll('.ant-form-item-required');
                    const inputs = modal.querySelectorAll('input');
                    const textareas = modal.querySelectorAll('textarea');
                    const selects = modal.querySelectorAll('.ant-select');
                    return {
                        labels: Array.from(labels).map(l => l.textContent.trim()),
                        requiredLabels: Array.from(required).map(r => {
                            const item = r.closest('.ant-form-item');
                            return item?.querySelector('.ant-form-item-label')?.textContent.trim() || '';
                        }),
                        inputCount: inputs.length,
                        textareaCount: textareas.length,
                        selectCount: selects.length
                    };
                }
            """)
            print(f"\n新增弹窗表单:")
            print(f"  所有字段: {modal_fields.get('labels', [])}")
            print(f"  必填字段: {modal_fields.get('requiredLabels', [])}")
            print(f"  input数: {modal_fields.get('inputCount', 0)}, textarea数: {modal_fields.get('textareaCount', 0)}, select数: {modal_fields.get('selectCount', 0)}")

            # 关闭弹窗
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)

    # 检查左侧导航菜单
    print(f"\n{'='*70}")
    print("左侧导航菜单")
    print(f"{'='*70}")
    menu = await page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-menu-item, .ant-menu-submenu-title');
            return Array.from(items).map(i => i.textContent.trim()).filter(t => t);
        }
    """)
    for m in menu:
        print(f"  {m}")

    await browser.close()
    await pw.stop()


asyncio.run(main())
