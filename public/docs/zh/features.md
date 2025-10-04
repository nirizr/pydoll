# 核心特性

Pydoll为浏览器自动化带来了突破性的功能，比传统浏览器自动化工具更加强大更易于使用。

## 核心功能

### 无WebDriver依赖

与传统浏览器自动化框架（例如Selenium）不同的是，Pydoll完全消除了对WebDriver的依赖。通过 Chrome DevTools 协议直接连接到浏览器，Pydoll 可以：

- 消除浏览器和驱动程序之间的版本兼容性问题
- 降低设置复杂性和维护开销
- 提供更可靠的连接，避免驱动程序相关问题
- 允许使用统一的 API 实现所有基于 Chromium 的浏览器的自动化

不再出现“chromedriver 版本与 Chrome 版本不匹配”的错误或神秘的 webdriver 崩溃。

### 异步优先架构

Pydoll 基于 Python 的 asyncio 全新构建，提供以下功能：

- **真正的并发**：并行运行多个操作，无阻塞
- **高效的资源利用**：以最小的开销管理多个浏览器实例
- **现代 Python 模式**：上下文管理器、异步迭代器和其他异步友好接口
- **性能优化**：降低自动化任务的延迟并提高吞吐量

### 模拟真人交互

通过模仿真实用户行为来绕过反爬行为检测：

- **自然输入**：以随机的按键时间输入文本
- **仿真点击**：以模拟真人的点击时间和移动方式进行点击，包括坐标偏移

### 事件驱动功能

实时响应浏览器事件：

- **网络监控**：跟踪请求、响应和失败的加载
- **DOM 结构观测**: 响应页面结构的变化
- **页面生命周期事件**: 捕获导航、加载和渲染事件
- **自定义事件处理程序**: 为感兴趣的特定事件注册回调


### 多浏览器支持

Pydoll支持操作任何Chromium核心的浏览器:

- **Google Chrome**：主要支持所有可用功能
- **Microsoft Edge**：全面支持 Edge 特定功能
- **Chromium**：支持其他基于 Chromium 的浏览器


### 导出网页截图和PDF

从网页截图：

- **全页截图**：截取整个页面内容包括超出视口范围的
- **元素截图**：截取特定元素
- **高质量 PDF 导出**：从网页生成 PDF 文档
- **自定义格式**：即将推出！

!!! 信息 "关于 iframe 与顶层目标的截图"
    `tab.take_screenshot()` 仅适用于顶层目标（top-level target）。在 `iframe` 内（通过 `await tab.get_frame(iframe_element)` 获取的子目标）时，Chrome 的 `Page.captureScreenshot` 无法直接对该子目标截图。这种情况下请改用 `WebElement.take_screenshot()`，它基于视口（viewport）进行捕获，适用于 iframe 内部。

## 远程连接与混合自动化

### 通过 WebSocket 连接已运行的浏览器

只需提供 DevTools 的 WebSocket 地址，即可远程控制已经在运行的浏览器实例：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def main():
    chrome = Chrome()
    tab = await chrome.connect('ws://YOUR_HOST:9222/devtools/browser/XXXX')

    await tab.go_to('https://example.com')
    title = await tab.execute_script('return document.title')
    print(title)

asyncio.run(main())
```

非常适合 CI、容器、远程主机或共享调试目标——无需本地启动，只需指向 WS 端点即可自动化。

### 自带 CDP：用 Pydoll 封装已有会话

如果你已经有自己的 CDP 集成，也可以将其与 Pydoll 的高级 API 结合使用。只要你知道元素的 `objectId`，就能直接构造 `WebElement`：

```python
from pydoll.connection import ConnectionHandler
from pydoll.elements.web_element import WebElement

# 你的 DevTools WebSocket 地址，以及通过 CDP 获取到的元素 objectId
ws = 'ws://YOUR_HOST:9222/devtools/page/ABCDEF...'
object_id = 'REMOTE_ELEMENT_OBJECT_ID'

connection_handler = ConnectionHandler(ws_address=ws)
element = WebElement(object_id=object_id, connection_handler=connection_handler)

# 立刻使用完整的 WebElement API
visible = await element.is_visible()
await element.wait_until(is_interactable=True, timeout=10)
await element.click()
text = await element.text
```

这种混合模式让你可以将底层的 CDP 能力（用于发现、注入或自定义流程）与 Pydoll 更易用的元素 API 顺畅结合。

## 直观的元素查找

Pydoll v2.0+ 引入了一种革命性的元素查找方法，比传统的基于选择器的方法更直观、更强大。

### 现代化的 find() 方法

全新的 `find()` 方法允许您使用自然属性搜索元素：


```python
import asyncio
from pydoll.browser.chromium import Chrome

async def element_finding_examples():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://example.com')
        
        # Find by tag name and class
        submit_button = await tab.find(tag_name='button', class_name='btn-primary')
        
        # Find by ID (most common)
        username_field = await tab.find(id='username')
        
        # Find by text content
        login_link = await tab.find(tag_name='a', text='Login')
        
        # Find by multiple attributes
        search_input = await tab.find(
            tag_name='input',
            type='text',
            placeholder='Search...'
        )
        
        # Find with custom data attributes
        custom_element = await tab.find(
            data_testid='submit-button',
            aria_label='Submit form'
        )
        
        # Find multiple elements
        all_links = await tab.find(tag_name='a', find_all=True)
        
        # With timeout and error handling
        delayed_element = await tab.find(
            class_name='dynamic-content',
            timeout=10,
            raise_exc=False  # Returns None if not found
        )

asyncio.run(element_finding_examples())
```

### 使用 query() 实现 CSS 选择器和 XPath

对于喜欢传统选择器的开发者，`query()` 方法提供了直接的 CSS 选择器和 XPath 支持：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def query_examples():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://example.com')
        
        # CSS selectors
        nav_menu = await tab.query('nav.main-menu')
        first_article = await tab.query('article:first-child')
        submit_button = await tab.query('button[type="submit"]')
        
        # XPath expressions
        specific_item = await tab.query('//div[@data-testid="item-123"]')
        text_content = await tab.query('//span[contains(text(), "Welcome")]')
        
        # Complex selectors
        nested_element = await tab.query('div.container > .content .item:nth-child(2)')

asyncio.run(query_examples())
```

### DOM 遍历助手：get_children_elements() 与 get_siblings_elements()

从已知锚点按树形结构遍历 DOM，更加明确且安全：

- get_children_elements(max_depth: int = 1, tag_filter: list[str] | None = None, raise_exc: bool = False) -> list[WebElement]
  - 使用先序遍历返回后代元素（先直接子元素，再其后代），深度不超过 max_depth
  - max_depth=1 仅返回直接子元素；2 包含孙辈元素，以此类推
  - tag_filter 用于按标签名过滤（小写，如 ['a', 'li']）
  - 当 raise_exc=True 且脚本解析失败时会抛出 ElementNotFound

- get_siblings_elements(tag_filter: list[str] | None = None, raise_exc: bool = False) -> list[WebElement]
  - 返回与当前元素同一父节点下的兄弟元素（不包含当前元素）
  - tag_filter 可按标签名过滤；返回顺序与父节点的子元素顺序一致

```python
# 文档顺序的直接子元素
container = await tab.find(id='cards')
children = await container.get_children_elements(max_depth=1)

# 包含孙辈
descendants = await container.get_children_elements(max_depth=2)

# 按标签过滤
links = await container.get_children_elements(max_depth=4, tag_filter=['a'])

# 横向遍历
active = await tab.find(class_name='item-active')
siblings = await active.get_siblings_elements()
link_siblings = await active.get_siblings_elements(tag_filter=['a'])
```

性能与正确性提示：

- DOM 是树结构：深度增加会迅速扩展宽度。优先使用较小的 max_depth，并结合 tag_filter 限制范围。
- 顺序：子元素遵循文档顺序；兄弟元素遵循父节点的子元素顺序，便于稳定迭代。
- iFrame：每个 iframe 是独立的 DOM 树。使用 `tab.get_frame(iframe_element)` 进入后，再在该 frame 内调用这些助手。
- 大型文档：深层遍历可能访问大量节点。建议将浅层遍历与基于锚点的精确 `find()`/`query()` 结合，以获得更佳性能。

## 原生 Cloudflare 验证码绕过

!!! 警告“关于验证码绕过的重要信息”
Cloudflare Turnstile 绕过的有效性取决于以下几个因素：

- **IP可信度**：Cloudflare 为每个 IP 地址分配一个“可信度”。干净的住宅 IP 通常会获得更高的分数。
- **过往历史记录**：有可疑活动历史记录的 IP 可能会被永久标记。

Pydoll 可以获得与常规浏览器会话相当的分数，但无法解决IP质量导致的风控。为了获得最佳效果，请使用质量良好的住宅 IP。

请记住，验证码绕过技术处于灰色地带，应谨慎使用。

Pydoll 最强大的功能之一是它能够自动绕过阻止大多数自动化工具的 Cloudflare Turnstile 验证码：

### 上下文管理器方法（同步）

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def bypass_cloudflare_example():
    async with Chrome() as browser:
        tab = await browser.start()
    
    # The context manager will wait for the captcha to be processed
    # before continuing execution
        async with tab.expect_and_bypass_cloudflare_captcha():
            await tab.go_to('https://site-with-cloudflare.com')
        print("Waiting for captcha to be handled...")
    
    # This code runs only after the captcha is successfully bypassed
    print("Captcha bypassed! Continuing with automation...")
        protected_content = await tab.find(id='protected-content')
        content_text = await protected_content.text
        print(f"Protected content: {content_text}")

asyncio.run(bypass_cloudflare_example())
```

### 后台自动处理验证码

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def background_bypass_example():
    async with Chrome() as browser:
        tab = await browser.start()
    
    # Enable automatic captcha solving before navigating
        await tab.enable_auto_solve_cloudflare_captcha()
    
    # Navigate to the protected site - captcha handled automatically in background
        await tab.go_to('https://site-with-cloudflare.com')
    print("Page loaded, captcha will be handled in the background...")
    
    # Add a small delay to allow captcha solving to complete
    await asyncio.sleep(3)
    
    # Continue with automation
        protected_content = await tab.find(id='protected-content')
        content_text = await protected_content.text
        print(f"Protected content: {content_text}")
    
    # Disable auto-solving when no longer needed
        await tab.disable_auto_solve_cloudflare_captcha()

asyncio.run(background_bypass_example())
```

无需使用第三方验证码服务，即可访问屏蔽自动化工具的网站。

## 可靠的下载处理：expect_download

`tab.expect_download()` 提供稳健的、基于事件的文件下载捕获方式。

- 自动为您配置浏览器下载行为
- 支持持久化目录（`keep_file_at`），或使用临时目录并在退出上下文后自动清理
- 提供 `_DownloadHandle` 便捷接口
- 内置超时保护，避免无限等待

### API 概览

```python
async with tab.expect_download(
    keep_file_at: Optional[str | Path] = None,
    timeout: Optional[float] = None,
) as handle:
    ... # 在页面中触发下载
```

- `keep_file_at`：指定持久化目录。若为 `None`，则使用临时目录并在退出上下文后自动清理。
- `timeout`：完成等待的最大秒数（未提供时默认 60）。

`handle` 提供：

- `handle.file_path: Optional[str]` — 完成后解析出的最终文件路径
- `await handle.read_bytes() -> bytes`
- `await handle.read_base64() -> str`
- `await handle.wait_started(timeout: Optional[float] = None) -> None`
- `await handle.wait_finished(timeout: Optional[float] = None) -> None`

### 使用示例

在指定目录中持久化下载文件：

```python
async with tab.expect_download(keep_file_at='/tmp/dl', timeout=15) as dl:
    await (await tab.find(text='Export CSV')).click()
    data = await dl.read_bytes()
    print('Saved at:', dl.file_path)
```

用于测试的临时目录（自动清理）：

```python
async with tab.expect_download() as dl:
    await (await tab.find(text='Download PDF')).click()
    pdf_b64 = await dl.read_base64()
    # 退出上下文后临时目录会被自动清理
```

注意：

- 如果在配置的 `timeout` 内页面未发出完成事件，将抛出 `DownloadTimeout` 异常。
- 如果浏览器未提供 `filePath`，管理器将回退到使用建议文件名并写入选定目录。

## 多标签页管理

Pydoll 采用单例模式提供完善的标签页管理功能，确保资源高效利用，并防止同一浏览器标签页出现重复的标签页实例。

### 标签页单例模式

Pydoll 根据浏览器的目标 ID 为标签页实例实现单例模式。这意味着：

- **标签页对象唯一性**：对同一浏览器标签页的多次引用将返回相同的标签页对象
- **自动化资源治理**：同一标签页不会出现重复的连接或处理程序
- **全局状态一致性**：对同一标签页的所有引用共享相同的状态和事件处理程序

```python
import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.browser.tab import Tab

async def singleton_demonstration():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Get the same tab through different methods - they're identical objects
        same_tab = Tab(browser, browser._connection_port, tab._target_id)
        opened_tabs = await browser.get_opened_tabs()
        
        # All references point to the same singleton instance
        print(f"Same object? {tab is same_tab}")  # May be True if same target_id
        print(f"Tab instances are managed as singletons")

asyncio.run(singleton_demonstration())
```


### 程序化创建新标签页

使用 `new_tab()` 程序化创建拥有完全控制权的新标签页: 

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def programmatic_tab_creation():
    async with Chrome() as browser:
        # Start with the initial tab
        main_tab = await browser.start()
        
        # Create additional tabs with specific URLs
        search_tab = await browser.new_tab('https://google.com')
        news_tab = await browser.new_tab('https://news.ycombinator.com')
        docs_tab = await browser.new_tab('https://docs.python.org')
        
        # Work with multiple tabs simultaneously
        await search_tab.find(name='q').type_text('Python automation')
        await news_tab.find(class_name='storylink', find_all=True)
        await docs_tab.find(id='search-field').type_text('asyncio')
        
        # Get all opened tabs
        all_tabs = await browser.get_opened_tabs()
        print(f"Total tabs open: {len(all_tabs)}")
        
        # Close specific tabs when done
        await search_tab.close()
        await news_tab.close()

asyncio.run(programmatic_tab_creation())
```

### 处理用户打开的标签页

当用户点击打开新标签页 (target="_blank") 的链接时，使用 `get_opened_tabs()` 来检测和管理它们：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def handle_user_opened_tabs():
    async with Chrome() as browser:
        main_tab = await browser.start()
        await main_tab.go_to('https://example.com')
        
        # Get initial tab count
        initial_tabs = await browser.get_opened_tabs()
        initial_count = len(initial_tabs)
        print(f"Initial tabs: {initial_count}")
        
        # Click a link that opens a new tab (target="_blank")
        external_link = await main_tab.find(text='Open in New Tab')
        await external_link.click()
        
        # Wait for new tab to open
        await asyncio.sleep(2)
        
        # Detect new tabs
        current_tabs = await browser.get_opened_tabs()
        new_tab_count = len(current_tabs)
        
        if new_tab_count > initial_count:
            print(f"New tab detected! Total tabs: {new_tab_count}")
            
            # Get the newly opened tab (last in the list)
            new_tab = current_tabs[-1]
            
            # Work with the new tab
            await new_tab.go_to('https://different-site.com')
            title = await new_tab.execute_script('return document.title')
            print(f"New tab title: {title}")
            
            # Close the new tab when done
            await new_tab.close()

asyncio.run(handle_user_opened_tabs())
```

### Pydoll 标签页管理的主要优势

1. **单例模式**：防止资源重复并确保状态一致
2. **自动检测**：`get_opened_tabs()` 查找所有标签页，包括用户打开的标签页
3. **并发处理**：使用 asyncio 同时处理多个标签页
4. **资源管理**：适当的清理可防止内存泄漏
5. **事件隔离**：每个标签页都维护自己的事件处理程序和状态

这种复杂的标签页管理功能使 Pydoll 非常适合：
- 需要标签页之间协调的**多页面工作流**
- 从多个来源**并行提取数据**
- 使用弹出窗口或新标签页的**测试应用程序**
- 跨多个浏览器标签页**监控用户行为**

## 并发抓取

Pydoll 的异步架构允许您同时抓取多个页面或网站，以实现最高效率：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def scrape_page(browser, url):
    """Process a single page and extract data using a shared browser"""
    # Create a new tab for this URL
    tab = await browser.new_tab()
    
    try:
        await tab.go_to(url)
        
        # Extract data
        title = await tab.execute_script('return document.title')
        
        # Find elements and extract content
        elements = await tab.find(class_name='article-content', find_all=True)
        content = []
        for element in elements:
            text = await element.text
            content.append(text)
            
        return {
            "url": url,
            "title": title,
            "content": content
        }
    finally:
        # Close the tab when done to free resources
        await tab.close()

async def main():
    # List of URLs to scrape in parallel
    urls = [
        'https://example.com/page1',
        'https://example.com/page2',
        'https://example.com/page3',
        'https://example.com/page4',
        'https://example.com/page5',
    ]
    
    async with Chrome() as browser:
        # Start the browser once
        await browser.start()
        
        # Process all URLs concurrently using the same browser
        results = await asyncio.gather(*(scrape_page(browser, url) for url in urls))
    
    # Print results
    for result in results:
        print(f"Scraped {result['url']}: {result['title']}")
        print(f"Found {len(result['content'])} content blocks")
    
    return results

# Run the concurrent scraping
all_data = asyncio.run(main())
```


与单线程控制标签页抓取相比，这种方法显著提升了性能，尤其适用于像网页抓取这样 I/O 密集型任务。Pydoll 无需等待每个页面逐个加载，而是同时处理所有页面，从而显著缩短了总执行时间。例如，如果抓取 10 个页面，每个页面加载时间为 2 秒，那么总共只需 2 秒多一点，而单线程处理则需要 20 多秒。

## 高级键盘控制

Pydoll 提供仿真的键盘交互，并可精确控制输入行为：


```python
import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.common.keys import Keys

async def realistic_typing_example():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://example.com/login')
        
        # Find login form elements
        username = await tab.find(id='username')
        password = await tab.find(id='password')
        
        # Type with realistic timing (interval between keystrokes)
        await username.type_text("user@example.com", interval=0.15)
        
        # Use special key combinations
        await password.click()
        await password.key_down(Keys.SHIFT)
        await password.type_text("PASSWORD")
        await password.key_up(Keys.SHIFT)
        
        # Press Enter to submit
        await password.press_keyboard_key(Keys.ENTER)
        
        # Wait for navigation
        await asyncio.sleep(2)
        print("Logged in successfully!")

asyncio.run(realistic_typing_example())
```

这种仿真的输入方式有助于避免被那些有用户行为检测的网站检测到。模拟真人操作和使用特殊组合键的能力使得 Pydoll 的交互几乎与人类用户难以区分。

## 强大的事件系统

Pydoll 的事件系统允许您实时响应浏览器事件：


```python
import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.protocol.page.events import PageEvent

async def event_monitoring_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Monitor page load events
        async def on_page_loaded(event):
            print(f"🌐 Page loaded: {event['params'].get('url')}")
            
        await tab.enable_page_events()
        await tab.on(PageEvent.LOAD_EVENT_FIRED, on_page_loaded)
        
        # Monitor network requests
        async def on_request(event):
            url = event['params']['request']['url']
            print(f"🔄 Request to: {url}")
            
        await tab.enable_network_events()
        await tab.on('Network.requestWillBeSent', on_request)
        
        # Navigate and see events in action
        await tab.go_to('https://example.com')
        await asyncio.sleep(5)  # Allow time to see events
        
asyncio.run(event_monitoring_example())
```

事件系统使 Pydoll 在监控 API 请求和响应、创建响应式自动化、调试复杂的 Web 应用程序以及构建全面的 Web 监控工具方面拥有独特的强大功能。

## 网络分析和响应提取

Pydoll 提供了强大的方法来分析网络流量并从 Web 应用程序中提取响应数据。这些功能适用于API 监控、数据提取和调试网络相关问题。

### 网络日志分析

`get_network_logs()` 方法允许您查找和分析页面发出的所有网络请求：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def network_analysis_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Enable network monitoring
        await tab.enable_network_events()
        
        # Navigate to a page with API calls
        await tab.go_to('https://example.com/dashboard')
        
        # Wait for page to load and make requests
        await asyncio.sleep(3)
        
        # Get all network logs
        all_logs = await tab.get_network_logs()
        print(f"Total network requests: {len(all_logs)}")
        
        # Filter logs for API requests only
        api_logs = await tab.get_network_logs(filter='api')
        print(f"API requests: {len(api_logs)}")
        
        # Filter logs for specific domain
        domain_logs = await tab.get_network_logs(filter='example.com')
        print(f"Requests to example.com: {len(domain_logs)}")
        
        # Analyze request patterns
        for log in api_logs:
            request = log['params'].get('request', {})
            url = request.get('url', 'Unknown')
            method = request.get('method', 'Unknown')
            print(f"📡 {method} {url}")

asyncio.run(network_analysis_example())
```

### 响应体提取

`get_network_response_body()` 方法可让您从网络请求中提取实际的响应内容：

```python
import asyncio
import json
from functools import partial
from pydoll.browser.chromium import Chrome
from pydoll.protocol.network.events import NetworkEvent

async def response_extraction_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Storage for API responses
        api_responses = {}
        
        async def capture_api_responses(tab, event):
            """Capture API response bodies"""
            request_id = event['params']['requestId']
            response = event['params']['response']
            url = response['url']
            
            # Only capture successful API responses
            if '/api/' in url and response['status'] == 200:
                try:
                    # Extract the response body
                    body = await tab.get_network_response_body(request_id)
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(body)
                        api_responses[url] = data
                        print(f"✅ Captured API response from: {url}")
                        print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                    except json.JSONDecodeError:
                        # Handle non-JSON responses
                        api_responses[url] = body
                        print(f"📄 Captured text response from: {url} ({len(body)} chars)")
                        
                except Exception as e:
                    print(f"❌ Failed to get response body for {url}: {e}")
        
        # Enable network monitoring and register callback
        await tab.enable_network_events()
        await tab.on(NetworkEvent.RESPONSE_RECEIVED, partial(capture_api_responses, tab))
        
        # Navigate to a page with API calls
        await tab.go_to('https://jsonplaceholder.typicode.com')
        
        # Trigger some API calls by interacting with the page
        await asyncio.sleep(5)
        
        # Display captured responses
        print(f"\n📊 Analysis Results:")
        print(f"Captured {len(api_responses)} API responses")
        
        for url, data in api_responses.items():
            if isinstance(data, dict):
                print(f"🔗 {url}: {len(data)} fields")
            else:
                print(f"🔗 {url}: {len(str(data))} characters")
        
        return api_responses

asyncio.run(response_extraction_example())
```

### 高级网络监控

结合两种方法进行全面的网络分析：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def comprehensive_network_monitoring():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Enable network monitoring
        await tab.enable_network_events()
        
        # Navigate to a complex web application
        await tab.go_to('https://example.com/app')
        
        # Wait for initial page load and API calls
        await asyncio.sleep(5)
        
        # Get comprehensive network analysis
        all_logs = await tab.get_network_logs()
        api_logs = await tab.get_network_logs(filter='api')
        static_logs = await tab.get_network_logs(filter='.js')
        
        print(f"📈 Network Traffic Summary:")
        print(f"   Total requests: {len(all_logs)}")
        print(f"   API calls: {len(api_logs)}")
        print(f"   JavaScript files: {len(static_logs)}")
        
        # Analyze request types
        request_types = {}
        for log in all_logs:
            request = log['params'].get('request', {})
            url = request.get('url', '')
            
            if '/api/' in url:
                request_types['API'] = request_types.get('API', 0) + 1
            elif any(ext in url for ext in ['.js', '.css', '.png', '.jpg']):
                request_types['Static'] = request_types.get('Static', 0) + 1
            else:
                request_types['Other'] = request_types.get('Other', 0) + 1
        
        print(f"📊 Request breakdown: {request_types}")
        
        # Show API endpoints
        print(f"\n🔗 API Endpoints Called:")
        for log in api_logs[:10]:  # Show first 10
            request = log['params'].get('request', {})
            method = request.get('method', 'GET')
            url = request.get('url', 'Unknown')
            print(f"   {method} {url}")

asyncio.run(comprehensive_network_monitoring())
```

网络分析功能非常适合以下情况：

- **API 测试**：监控和验证 API 响应
- **性能分析**：跟踪请求时间和大小
- **数据提取**：提取通过 AJAX 加载的动态内容
- **调试**：识别失败的请求和网络问题
- **安全测试**：分析请求/响应模式

## 浏览器上下文 HTTP 请求

Pydoll 通过 `tab.request` 属性提供了类似 `requests` 的强大接口，使 HTTP 请求在浏览器的 JavaScript 上下文中执行。这种混合模式将 Python `requests` 的熟悉体验与浏览器上下文执行的优势结合起来。

### 关键优势

- **继承浏览器会话状态**：自动包含 Cookie、认证和会话数据
- **符合 CORS**：请求源自浏览器上下文，避免跨域限制  
- **非常适合 SPA**：适配大量使用 JavaScript 与动态认证的单页应用
- **无需会话搬运**：不必在自动化与 API 客户端之间转移 Cookie 或 Token

### 基本 HTTP 方法

所有标准 HTTP 方法都以熟悉的接口提供：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def browser_requests_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # 先建立会话上下文
        await tab.go_to('https://api.example.com')
        
        # GET 请求
        response = await tab.request.get('https://api.example.com/users')
        print(f"Status: {response.status_code}")
        print(f"Data: {response.json()}")
        
        # POST 请求（JSON）
        user_data = {"name": "John Doe", "email": "john@example.com"}
        response = await tab.request.post(
            'https://api.example.com/users',
            json=user_data
        )
        
        # 带自定义头的 PUT 请求
        response = await tab.request.put(
            'https://api.example.com/users/123',
            json=user_data,
            headers={'X-Custom-Header': 'value'}
        )
        
        # DELETE 请求
        response = await tab.request.delete('https://api.example.com/users/123')

asyncio.run(browser_requests_example())
```

### 响应对象接口

响应对象与 Python `requests` 库接口一致：

```python
async def response_handling_example():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://api.example.com')
        
        response = await tab.request.get('https://api.example.com/data')
        
        # 状态信息
        print(f"Status Code: {response.status_code}")
        print(f"OK: {response.ok}")  # 2xx/3xx 为 True
        
        # 响应内容
        print(f"Raw content: {response.content}")     # bytes
        print(f"Text content: {response.text}")       # str
        print(f"JSON data: {response.json()}")        # dict/list
        
        # 响应头
        print(f"Response headers: {response.headers}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        # 实际发送的请求头
        print(f"Request headers: {response.request_headers}")
        
        # 响应设置的 Cookies
        for cookie in response.cookies:
            print(f"Cookie: {cookie.name}={cookie.value}")
        
        # 重定向后的最终 URL
        print(f"Final URL: {response.url}")
        
        # 为 HTTP 错误抛出异常
        response.raise_for_status()  # 4xx/5xx 抛出 HTTPError

asyncio.run(response_handling_example())
```

### 高级请求配置

使用完整的 HTTP 选项配置请求：

```python
async def advanced_requests_example():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://api.example.com')
        
        # 复杂 POST，包含所有选项
        response = await tab.request.post(
            'https://api.example.com/submit',
            json={
                "user": "test",
                "action": "create"
            },
            headers={
                'Authorization': 'Bearer token-123',
                'X-API-Version': '2.0',
                'Content-Language': 'en-US'
            },
            params={
                'format': 'json',
                'version': '2'
            }
        )
        
        # 表单提交
        form_response = await tab.request.post(
            'https://api.example.com/form',
            data={
                'username': 'testuser',
                'password': 'secret123'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        # 文件上传模拟
        file_response = await tab.request.post(
            'https://api.example.com/upload',
            data={'file_content': 'base64-encoded-data'},
            headers={'Content-Type': 'multipart/form-data'}
        )

asyncio.run(advanced_requests_example())
```

### 混合自动化工作流

将 UI 自动化与直接 API 调用结合，以获得最大效率：

```python
async def hybrid_automation_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # 第一步：基于 UI 的登录（处理复杂认证流程）
        await tab.go_to('https://app.example.com/login')
        
        username_field = await tab.find(id='username')
        password_field = await tab.find(id='password')
        login_button = await tab.find(id='login-btn')
        
        await username_field.type_text('admin@example.com')
        await password_field.type_text('secure_password')
        await login_button.click()
        
        # 等待登录跳转
        await asyncio.sleep(3)
        
        # 第二步：利用继承的认证调用 API（无需手动提取 Token）
        dashboard_response = await tab.request.get('https://app.example.com/api/dashboard')
        dashboard_data = dashboard_response.json()
        
        # 批量操作（比 UI 更快）
        for item_id in dashboard_data.get('item_ids', []):
            update_response = await tab.request.put(
                f'https://app.example.com/api/items/{item_id}',
                json={'status': 'processed', 'updated_by': 'automation'}
            )
            print(f"Updated item {item_id}: {update_response.status_code}")
        
        # 第三步：回到 UI 验证
        await tab.go_to('https://app.example.com/dashboard')
        
        updated_items = await tab.find(class_name='item-status', find_all=True)
        for item in updated_items:
            status = await item.text
            print(f"UI shows item status: {status}")

asyncio.run(hybrid_automation_example())
```

这种浏览器上下文 HTTP 接口让 Pydoll 在现代 Web 自动化中更具优势，打破了传统的 UI 自动化与 API 交互之间的边界。

## 自定义浏览器首选项

Pydoll 通过 `ChromiumOptions.browser_preferences` 提供对 Chromium 内部首选项系统的直接访问。你可以根据 Chromium 源码中可用的设置配置浏览器，实现对浏览器行为的精细控制。

### 工作原理

Chromium 首选项使用点号分隔的键映射到嵌套的 Python 字典。每个 `.` 都表示一个新的字典层级。

源码参考：[chromium 的 pref_names.cc](https://chromium.googlesource.com/chromium/src/+/4aaa9f29d8fe5eac55b8632fa8fcb05a68d9005b/chrome/common/pref_names.cc)

### 从源码构建首选项

```cpp
// 来自 Chromium 源码（pref_names.cc）
const char kDownloadDefaultDirectory[] = "download.default_directory";
const char kPromptForDownload[] = "download.prompt_for_download";
const char kSearchSuggestEnabled[] = "search.suggest_enabled";
const char kSiteEngagementLastUpdateTime[] = "profile.last_engagement_time";
const char kNewTabPageLocationOverride[] = "newtab_page_location_override";
```

转换为 Python 字典：

```python
from pydoll.browser.options import ChromiumOptions

options = ChromiumOptions()
options.browser_preferences = {
    'download': {
        'default_directory': '/tmp/downloads',
        'prompt_for_download': False
    },
    'search': {
        'suggest_enabled': False
    },
    'profile': {
        'last_engagement_time': 1640995200  # timestamp
    },
    'newtab_page_location_override': 'https://www.google.com'
}
```

### 重要配置示例

#### 性能优化

```python
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions

options = ChromiumOptions()
options.browser_preferences = {
    # 关闭网络预测和预取
    'net': {
        'network_prediction_options': 2  # Never predict
    },
    # 为速度关闭图片加载
    'webkit': {
        'webprefs': {
            'loads_images_automatically': False,
            'plugins_enabled': False
        }
    },
    # 关闭错误页建议
    'alternate_error_pages': {
        'enabled': False
    }
}
```

#### 隐身自动化

```python
import time
from pydoll.browser.options import ChromiumOptions

options = ChromiumOptions()
fake_timestamp = int(time.time()) - (90 * 24 * 60 * 60)  # 90 天前

options.browser_preferences = {
    # 模拟真实的浏览器使用历史
    'profile': {
        'last_engagement_time': fake_timestamp,
        'exited_cleanly': True,
        'exit_type': 'Normal'
    },
    # 覆盖新标签页
    'newtab_page_location_override': 'https://www.google.com',
    # 禁用遥测
    'user_experience_metrics': {
        'reporting_enabled': False
    }
}
```

#### 隐私与安全

```python
from pydoll.browser.options import ChromiumOptions

options = ChromiumOptions()
options.browser_preferences = {
    # 隐私设置
    'enable_do_not_track': True,
    'enable_referrers': False,
    'safebrowsing': {
        'enabled': False
    },
    # 关闭数据收集
    'profile': {
        'password_manager_enabled': False
    },
    'autofill': {
        'enabled': False
    },
    'search': {
        'suggest_enabled': False
    }
}
```

#### 下载与界面

```python
from pydoll.browser.options import ChromiumOptions

options = ChromiumOptions()
options.browser_preferences = {
    # 静默下载
    'download': {
        'default_directory': '/tmp/automation-downloads',
        'prompt_for_download': False
    },
    # 会话行为
    'session': {
        'restore_on_startup': 5,  # Open New Tab Page
        'startup_urls': ['about:blank']
    },
    # 首页
    'homepage': 'https://www.google.com',
    'homepage_is_newtabpage': False
}
```

### 便捷方法

对于常见场景，你可以结合便捷方法与直接首选项：

```python
from pydoll.browser.options import ChromiumOptions

options = ChromiumOptions()

# 下载管理
options.set_default_download_directory('/tmp/downloads')
options.prompt_for_download = False
options.allow_automatic_downloads = True

# 内容拦截与隐私
options.block_notifications = True
options.block_popups = True
options.password_manager_enabled = False

# 国际化
options.set_accept_languages('pt-BR,en-US')
# PDF 与文件处理
options.open_pdf_externally = True

# 直接首选项（高级设置）
options.browser_preferences = {
    'net': {'network_prediction_options': 2},
    'enable_do_not_track': True
}
```

### 影响与收益

- **性能**：通过禁用图片、预测和不必要的功能，可实现 3–5 倍更快的页面加载
- **隐身**：构造更真实的浏览器指纹，绕过自动化检测
- **隐私**：全面控制数据收集、跟踪与遥测
- **自动化**：消除打断自动化流程的弹窗与提示
- **企业**：配置数百项过去只有组策略才能控制的设置

这种对 Chromium 首选项系统的直接访问让你拥有与企业管理员、扩展开发者同级别的控制力，使复杂的浏览器定制在自动化脚本中成为可能。

## 上传文件支持

在您的自动化脚本中无缝上传文件:

```python
import asyncio
import os
from pydoll.browser.chromium import Chrome

async def file_upload_example():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://example.com/upload')
        
        # Method 1: Direct file input
        file_input = await tab.find(tag_name='input', type='file')
        await file_input.set_input_files('path/to/document.pdf')
        
        # Method 2: Using file chooser with an upload button
        sample_file = os.path.join(os.getcwd(), 'sample.jpg')
        async with tab.expect_file_chooser(files=sample_file):
            upload_button = await tab.find(id='upload-button')
            await upload_button.click()
            
        # Submit the form
        submit = await tab.find(id='submit-button')
        await submit.click()
        
        print("Files uploaded successfully!")

asyncio.run(file_upload_example())
```

在其他框架中，文件上传的自动化难度非常高，通常需要一些变通方法。Pydoll 通过直接文件输入和文件选择器对话框支持，让这项工作变得简单易行。

## 多浏览器示例

Pydoll通过一致的API兼容不同的浏览器：

```python
import asyncio
from pydoll.browser.chromium import Chrome, Edge

async def multi_browser_example():
    # Run the same automation in Chrome
    async with Chrome() as chrome:
        chrome_tab = await chrome.start()
        await chrome_tab.go_to('https://example.com')
        chrome_title = await chrome_tab.execute_script('return document.title')
        print(f"Chrome title: {chrome_title}")
    
    # Run the same automation in Edge
    async with Edge() as edge:
        edge_tab = await edge.start()
        await edge_tab.go_to('https://example.com')
        edge_title = await edge_tab.execute_script('return document.title')
        print(f"Edge title: {edge_title}")

asyncio.run(multi_browser_example())
```

无需更改代码即可实现跨浏览器兼容性。跨不同浏览器测试您的自动化功能，确保其在所有浏览器中都能正常运行。  

## 集成代理

与许多自动化工具在代理实现方面遇到困难不同，Pydoll 提供原生代理支持和完整的身份验证功能。这使其成为以下应用的理想之选：  

- 需要轮换 IP 地址的 **Web 数据抓取** 项目
- 跨不同区域进行应用程序的 **地理定位测试**
- 需要匿名流量的 **注重隐私的自动化**
- 通过企业代理进行 **Web 应用程序测试**

在 Pydoll中配置代理非常简单：  

```python
import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions

async def proxy_example():
    # Create browser options
    options = ChromiumOptions()
    
    # Simple proxy without authentication
    options.add_argument('--proxy-server=192.168.1.100:8080')
    # Or proxy with authentication
    # options.add_argument('--proxy-server=username:password@192.168.1.100:8080')
    
    # Bypass proxy for specific domains
    options.add_argument('--proxy-bypass-list=*.internal.company.com,localhost')

    # Start browser with proxy configuration
    async with Chrome(options=options) as browser:
        tab = await browser.start()
        
        # Test the proxy by visiting an IP echo service
        await tab.go_to('https://api.ipify.org')
        ip_address = await tab.execute_script('return document.body.textContent')
        print(f"Current IP address: {ip_address}")
        
        # Continue with your automation
        await tab.go_to('https://example.com')
        title = await tab.execute_script('return document.title')
        print(f"Page title: {title}")

asyncio.run(proxy_example())
```

## 使用iFrames

Pydoll 通过 `get_frame()` 方法提供无缝的 iframe 交互：

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def iframe_interaction():
    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to('https://example.com/page-with-iframe')
        
        # Find the iframe element
        iframe_element = await tab.query('.hcaptcha-iframe', timeout=10)
        
        # Get a Tab instance for the iframe content
        frame = await tab.get_frame(iframe_element)
        
        # Now interact with elements inside the iframe
        submit_button = await frame.find(tag_name='button', class_name='submit')
        await submit_button.click()
        
        # You can use all Tab methods on the frame
        form_input = await frame.find(id='captcha-input')
        await form_input.type_text('verification-code')
        
        # Find elements by various methods
        links = await frame.find(tag_name='a', find_all=True)
        specific_element = await frame.query('#specific-id')

asyncio.run(iframe_interaction())
```

## 请求拦截

在网络请求发送之前拦截并修改它们：

### 简单请求修改例子

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def request_interception_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Define the request interceptor
        async def intercept_request(event):
            request_id = event['params']['requestId']
            url = event['params']['request']['url']
            
            if '/api/' in url:
                # Get original headers
                original_headers = event['params']['request'].get('headers', {})
                
                # Add custom headers
                custom_headers = {
                    **original_headers,
                    'Authorization': 'Bearer my-token-123',
                    'X-Custom-Header': 'CustomValue'
                }
                
                print(f"🔄 Modifying request to: {url}")
                await tab.continue_request(
                        request_id=request_id,
                        headers=custom_headers
                )
            else:
                # Continue normally for non-API requests
                await tab.continue_request(request_id=request_id)
        
        # Enable interception and register handler
        await tab.enable_request_interception()
        await tab.on('Fetch.requestPaused', intercept_request)
        
        # Navigate to trigger requests
        await tab.go_to('https://example.com')
        await asyncio.sleep(5)  # Allow time for requests to process

asyncio.run(request_interception_example())
```

### 拦截指定请求

使用 `fail_request` 可以拦截指定请求例如广告、隐私追踪器、不想要的网页资源:

```python
import asyncio
from pydoll.browser.chromium import Chrome

async def block_requests_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        # Define blocked domains and resource types
        blocked_domains = ['doubleclick.net', 'googletagmanager.com', 'facebook.com']
        blocked_resources = ['image', 'stylesheet', 'font']
        
        async def block_unwanted_requests(event):
            request_id = event['params']['requestId']
            url = event['params']['request']['url']
            resource_type = event['params'].get('resourceType', '').lower()
            
            # Block requests from specific domains
            if any(domain in url for domain in blocked_domains):
                print(f"🚫 Blocking request to: {url}")
                await tab.fail_request(
                    request_id=request_id,
                    error_reason='BlockedByClient'
                )
                return
            
            # Block specific resource types (images, CSS, fonts)
            if resource_type in blocked_resources:
                print(f"🚫 Blocking {resource_type}: {url}")
                await tab.fail_request(
                    request_id=request_id,
                    error_reason='BlockedByClient'
                )
                return
            
            # Continue with allowed requests
            await tab.continue_request(request_id=request_id)
        
        # Enable interception and register handler
        await tab.enable_request_interception()
        await tab.on('Fetch.requestPaused', block_unwanted_requests)
        
        # Navigate to a page with many external resources
        await tab.go_to('https://example.com')
        await asyncio.sleep(10)  # Allow time to see blocked requests

asyncio.run(block_requests_example())
```

### 拦截修改API响应

使用 `fulfill_request` 可以做到不请求后端直接模拟请求返回:

```python
import asyncio
import json
from pydoll.browser.chromium import Chrome

async def mock_api_responses_example():
    async with Chrome() as browser:
        tab = await browser.start()
        
        async def mock_api_requests(event):
            request_id = event['params']['requestId']
            url = event['params']['request']['url']
            
            # Mock user API endpoint
            if '/api/user' in url:
                mock_user_data = {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "admin"
                }
                
                print(f"🎭 Mocking API response for: {url}")
                await tab.fulfill_request(
                    request_id=request_id,
                    response_code=200,
                    response_headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    body=json.dumps(mock_user_data)
                )
                return
            
            # Mock products API endpoint
            elif '/api/products' in url:
                mock_products = [
                    {"id": 1, "name": "Product A", "price": 29.99},
                    {"id": 2, "name": "Product B", "price": 39.99},
                    {"id": 3, "name": "Product C", "price": 19.99}
                ]
                
                print(f"🎭 Mocking products API response for: {url}")
                await tab.fulfill_request(
                    request_id=request_id,
                    response_code=200,
                    response_headers={'Content-Type': 'application/json'},
                    body=json.dumps(mock_products)
                )
                return
            
            # Simulate API error for specific endpoints
            elif '/api/error' in url:
                error_response = {"error": "Internal Server Error", "code": 500}
                
                print(f"🎭 Mocking error response for: {url}")
                await tab.fulfill_request(
                    request_id=request_id,
                    response_code=500,
                    response_headers={'Content-Type': 'application/json'},
                    body=json.dumps(error_response)
                )
                return
            
            # Continue with real requests for everything else
            await tab.continue_request(request_id=request_id)
        
        # Enable interception and register handler
        await tab.enable_request_interception()
        await tab.on('Fetch.requestPaused', mock_api_requests)
        
        # Navigate to a page that makes API calls
        await tab.go_to('https://example.com/dashboard')
        await asyncio.sleep(5)  # Allow time for API calls

asyncio.run(mock_api_responses_example())
```

### 高级请求操作

整合所有拦截方法，实现全面的请求控制：

```python
import asyncio
import json
from pydoll.browser.chromium import Chrome

async def advanced_request_control():
    async with Chrome() as browser:
        tab = await browser.start()
        
        async def advanced_interceptor(event):
            request_id = event['params']['requestId']
            url = event['params']['request']['url']
            method = event['params']['request']['method']
            headers = event['params']['request'].get('headers', {})
            
            print(f"📡 Intercepted {method} request to: {url}")
            
            # Block analytics and tracking
            if any(tracker in url for tracker in ['analytics', 'tracking', 'ads']):
                print(f"🚫 Blocked tracking request: {url}")
                await tab.fail_request(request_id=request_id, error_reason='BlockedByClient')
                return
            
            # Mock authentication endpoint
            if '/auth/login' in url and method == 'POST':
                mock_auth_response = {
                    "success": True,
                    "token": "mock-jwt-token-12345",
                    "user": {"id": 1, "username": "testuser"}
                }
                print(f"🎭 Mocking login response")
                await tab.fulfill_request(
                    request_id=request_id,
                    response_code=200,
                    response_headers={'Content-Type': 'application/json'},
                    body=json.dumps(mock_auth_response)
                )
                return
            
            # Add authentication to API requests
            if '/api/' in url and 'Authorization' not in headers:
                modified_headers = {
                    **headers,
                    'Authorization': 'Bearer mock-token-12345',
                    'X-Test-Mode': 'true'
                }
                print(f"🔧 Adding auth headers to: {url}")
                await tab.continue_request(
                    request_id=request_id,
                    headers=modified_headers
                )
                return
            
            # Continue with unmodified request
            await tab.continue_request(request_id=request_id)
        
        # Enable interception
        await tab.enable_request_interception()
        await tab.on('Fetch.requestPaused', advanced_interceptor)
        
        # Test the interception
        await tab.go_to('https://example.com/app')
        await asyncio.sleep(10)

asyncio.run(advanced_request_control())
```

这项强大的功能允许您：

- 为API请求**动态添加身份验证标头**
- **屏蔽不需要的资源**，例如广告、跟踪器和大图片，以加快加载速度
- **Mock API响应**，以便在没有后端依赖的情况下进行测试
- **模拟网络错误**，以测试错误处理
- **修改请求内容**
- **实时分析和调试网络流量**

这些功能充分展现了Pydoll作为新一代浏览器自动化工具的优势，它能直接控制浏览器与直观的异步原生API。