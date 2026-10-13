# 超级个体后台管理系统 - Web 自动化测试框架

基于 Playwright + pytest 的 Web UI 自动化测试框架，用于测试超级个体后台管理系统的各项功能。

## 项目结构

```
cjgt-web-kcode/
├── web_auto/                    # 主测试代码目录
│   ├── config/                  # 配置管理
│   │   ├── .env.example         # 环境变量模板（复制为 .env 并填写实际值）
│   │   ├── env_config.py        # 环境配置加载
│   │   └── __init__.py
│   ├── pages/                   # 页面对象模式 (Page Object Model)
│   │   ├── base_page.py         # 页面基类
│   │   ├── login_page.py        # 登录页
│   │   ├── home_page.py         # 首页
│   │   ├── knowledge_page.py    # 知识库页
│   │   ├── provider_page.py     # 服务商页
│   │   ├── service_project_page.py   # 服务项目页
│   │   ├── project_price_page.py     # 服务定价页
│   │   ├── contract_service_page.py  # 合同服务页
│   │   └── __init__.py
│   ├── tests/                   # pytest 测试用例
│   │   ├── conftest.py          # pytest 固件配置
│   │   ├── test_login.py        # 登录测试
│   │   ├── test_business_flow.py    # 业务流程测试
│   │   ├── test_ui_validation.py    # UI 验证测试
│   │   └── __init__.py
│   ├── utils/                   # 工具类
│   │   ├── logger.py            # 日志工具
│   │   ├── notify.py            # 通知工具
│   │   ├── file_helper.py       # 文件操作工具
│   │   └── __init__.py
│   └── reports/                 # 测试报告输出目录（自动生成）
├── run_tests.py                 # 主入口：运行所有模块测试并生成报告
├── test_base.py                 # 测试基类（浏览器管理、登录复用）
├── test_smart_service_config.py # 智能服务配置测试
├── test_content_management.py   # 内容管理测试
├── test_customer_management.py  # 客户管理测试
├── test_order_contract_management.py  # 订单/合同管理测试
└── .gitignore
```

## 功能模块

| 模块 | 测试文件 | 覆盖功能 |
|------|---------|---------|
| 登录认证 | `web_auto/tests/test_login.py` | 正常登录、错误密码、空账号、空密码、不存在账号、UI 元素验证 |
| 智能服务配置 | `test_smart_service_config.py` | 服务项目、服务定价、合同服务的增删改查、搜索、分页 |
| 内容管理 | `test_content_management.py` | 知识库的增删改查、搜索、详情、分页 |
| 客户管理 | `test_customer_management.py` | 超级个体档案、服务工单的查询、详情、分页 |
| 订单管理 | `test_order_contract_management.py` | 订单查询、筛选、详情、分页 |
| 合同管理 | `test_order_contract_management.py` | 合同查询、筛选、展开详情、协议查看、分页 |

## 环境要求

- Python 3.10+
- Playwright 支持的浏览器

## 安装依赖

```bash
pip install playwright pytest pytest-asyncio allure-pytest python-dotenv
playwright install chromium
```

## 配置说明

1. 复制配置模板：
   ```bash
   cp web_auto/config/.env.example web_auto/config/.env
   ```

2. 编辑 `.env` 文件，填写实际环境信息：
   ```ini
   # 被测系统地址
   BASE_URL=http://your-test-url:port
   
   # 登录账号
   USERNAME=your_username
   PASSWORD=your_password
   
   # 浏览器配置
   HEADLESS=false          # true=无头模式，false=有界面
   BROWSER=chromium        # 浏览器类型
   VIEWPORT_WIDTH=1440
   VIEWPORT_HEIGHT=900
   
   # 超时设置（毫秒）
   TIMEOUT=30000
   
   # 并行工作进程数
   PARALLEL_WORKERS=1
   ```

> ⚠️ **注意**：`.env` 文件包含敏感信息，**不要提交到版本控制**。已在 `.gitignore` 中忽略。

## 运行测试

### 运行所有测试（推荐）
```bash
python run_tests.py
```
- 共享单个浏览器实例
- 登录一次，所有模块复用登录状态
- 生成 JSON 和 Markdown 格式测试报告到 `reports/` 目录

### 运行单个测试文件（pytest 方式）
```bash
# 运行登录测试
pytest web_auto/tests/test_login.py -v

# 运行所有 pytest 测试
pytest web_auto/tests/ -v

# 生成 Allure 报告
pytest web_auto/tests/ --alluredir=web_auto/reports/allure-results
allure serve web_auto/reports/allure-results
```

### 运行特定模块测试
```bash
# 智能服务配置
python -m pytest test_smart_service_config.py -v

# 内容管理
python -m pytest test_content_management.py -v
```

## 测试报告

运行 `run_tests.py` 后，会在 `reports/` 目录生成：
- `test_report_<timestamp>.json` - 结构化 JSON 报告
- `test_report_<timestamp>.md` - 人类可读的 Markdown 报告

Allure 报告在 `web_auto/reports/allure-results/`，使用 `allure serve` 查看。

## 核心特性

1. **页面对象模式 (POM)** - 页面元素与操作封装，提高维护性
2. **浏览器复用** - 单浏览器实例，登录状态跨模块共享，大幅提升执行速度
3. **配置外部化** - `.env` 管理环境差异，敏感信息不入库
4. **丰富报告** - 支持 JSON、Markdown、Allure 多种报告格式
5. **详细日志** - 结构化日志，便于问题排查
6. **截图记录** - 失败自动截图，Allure 报告内嵌截图

## 目标系统

- **系统名称**: 超级个体后台管理系统
- **测试地址**: 配置在 `.env` 的 `BASE_URL`
- **技术栈**: React + Ant Design (基于选择器推断)

## 贡献指南

1. 新增页面对象：在 `web_auto/pages/` 下创建，继承 `BasePage`
2. 新增测试用例：在 `web_auto/tests/` 或根目录测试文件中添加
3. 遵循命名规范：`test_<功能>_<场景>`
4. 使用 Allure 装饰器标注 feature/story/severity/title
5. 提交前运行完整测试套件确保无回归

## 许可证

内部项目，仅供团队使用。