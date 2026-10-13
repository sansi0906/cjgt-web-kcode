import asyncio
import json
from playwright.async_api import async_playwright

BASE_URL = 'http://172.16.1.165:9100'
USERNAME = '15522719628'
PASSWORD = '123456'

async def explore_page(page, path, name):
    print(f"\n{'='*60}")
    print(f"正在探索: {name} ({path})")
    print(f"{'='*60}")
    
    await page.goto(f'{BASE_URL}{path}', wait_until='networkidle')
    
    if '/adminLogin' in page.url:
        print("  被重定向到登录页，重新登录")
        await page.wait_for_timeout(2000)
        await page.fill('input[placeholder="账号"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button:has-text("登 录")')
        await page.wait_for_timeout(3000)
        await page.goto(f'{BASE_URL}{path}', wait_until='networkidle')
    
    for i in range(10):
        await page.wait_for_timeout(2000)
        table_rows = await page.evaluate("""
            () => document.querySelectorAll('.ant-table-tbody tr').length
        """)
        print(f"  等待{i*2+2}s后表格行数: {table_rows}")
        if table_rows > 0:
            break
    
    info = {}
    info['url'] = page.url
    info['title'] = await page.title()
    
    info['table_headers'] = await page.evaluate("""
        () => {
            const ths = document.querySelectorAll('th, .ant-table-thead th');
            const texts = [];
            ths.forEach(th => {
                const text = th.textContent.trim();
                if (text) texts.push(text);
            });
            return texts;
        }
    """)
    
    info['table_rows'] = await page.evaluate("""
        () => document.querySelectorAll('.ant-table-tbody tr').length
    """)
    
    info['buttons'] = await page.evaluate("""
        () => {
            const buttons = [];
            document.querySelectorAll('button, .ant-btn, a.ant-btn').forEach(btn => {
                const text = btn.textContent.trim();
                if (text && text.length < 50) {
                    buttons.push(text.replace(/\\s+/g, ' '));
                }
            });
            return [...new Set(buttons)];
        }
    """)
    
    info['selects'] = await page.evaluate("""
        () => {
            const selects = [];
            document.querySelectorAll('.ant-select-selector').forEach(select => {
                const text = select.textContent.trim();
                if (text) selects.push(text.replace(/\\s+/g, ' '));
            });
            return [...new Set(selects)].slice(0, 10);
        }
    """)
    
    info['inputs'] = await page.evaluate("""
        () => {
            const inputs = [];
            document.querySelectorAll('input, textarea').forEach(input => {
                const placeholder = input.placeholder || input.getAttribute('placeholder') || '';
                const type = input.type || '';
                if (placeholder) {
                    inputs.push({placeholder, type});
                }
            });
            return inputs;
        }
    """)
    
    info['pagination'] = await page.evaluate("""
        () => {
            const pagination = document.querySelector('.ant-pagination');
            if (!pagination) return null;
            const total = pagination.querySelector('.ant-pagination-total-text');
            const items = pagination.querySelectorAll('.ant-pagination-item');
            return {
                total: total ? total.textContent : null,
                page_count: items.length,
            };
        }
    """)
    
    screenshot_path = f'E:/KiloAutoTest/cjgt_web/screenshots/explore_{name.replace("/", "_").replace(" ", "_")}.png'
    await page.screenshot(path=screenshot_path, full_page=True)
    info['screenshot'] = screenshot_path
    
    print(f"URL: {info['url']}")
    print(f"标题: {info['title']}")
    print(f"表格列头: {info['table_headers']}")
    print(f"数据行数: {info['table_rows']}")
    print(f"按钮: {info['buttons']}")
    print(f"输入框: {[i['placeholder'] for i in info['inputs'][:5]]}")
    print(f"下拉框: {info['selects']}")
    print(f"分页: {info['pagination']}")
    print(f"截图已保存: {screenshot_path}")
    
    return info

async def main():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()
    
    print("正在登录...")
    await page.goto(f'{BASE_URL}/adminLogin', wait_until='networkidle')
    await page.wait_for_timeout(2000)
    await page.fill('input[placeholder="账号"]', USERNAME)
    await page.fill('input[type="password"]', PASSWORD)
    await page.click('button:has-text("登 录")')
    await page.wait_for_timeout(3000)
    print("登录成功!")
    
    pages_to_explore = [
        ("订单管理", "/order/order-manage"),
        ("合同管理", "/contract/contract-manage"),
    ]
    
    all_info = {}
    for name, path in pages_to_explore:
        try:
            info = await explore_page(page, path, name)
            all_info[name] = info
        except Exception as e:
            print(f"探索 {name} 失败: {e}")
            all_info[name] = {"error": str(e)}
    
    with open('E:/KiloAutoTest/cjgt_web/screenshots/explore_order_contract.json', 'w', encoding='utf-8') as f:
        json.dump(all_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("探索完成!")
    print(f"{'='*60}")
    
    await browser.close()
    await pw.stop()

if __name__ == '__main__':
    asyncio.run(main())
