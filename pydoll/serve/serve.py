from typing import Any, Dict, List

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ..browser import Chrome
from ..browser.options import ChromiumOptions as Options
from ..constants import Key

from .schemas import CrawlRequest, Step

app = FastAPI(title="Pydoll API", docs_url="/docs", redoc_url="/redoc")  # explicitly define docs URLs

async def execute_steps(tab, steps: List[Step]) -> List[Any]:
    outputs = []
    for step in steps:
        action = step.action

        if action == "find":
            element = await tab.find(**(step.by.dict(exclude_none=True) if step.by else {}))
            if step.insert_text:
                await element.insert_text(step.insert_text)
            if step.click:
                await element.click()
            if step.key:
                key = getattr(Key, step.key, step.key)
                await element.press_keyboard_key(key)

        elif action == "wait_for":
            await tab.find(**(step.by.dict(exclude_none=True) if step.by else {}))

        elif action == "execute_script":
            if not step.script:
                raise HTTPException(status_code=400, detail="execute_script requires 'script'")
            result = await tab.execute_script(step.script, return_by_value=step.return_by_value or False)
            outputs.append({"action": "execute_script", "result": result})

        elif action == "request":
            if not step.method or not step.url:
                raise HTTPException(status_code=400, detail="request requires 'method' and 'url'")
            req = tab.request
            if step.method.upper() == "GET":
                resp = await req.get(step.url, headers=step.headers)
            else:
                resp = await req.post(step.url, headers=step.headers, json=step.json)
            outputs.append({"action": "request", "status": resp.status, "body": await resp.text()})

        elif action == "screenshot":
            ss = await tab.screenshot(full_page=step.full_page or False)
            outputs.append({"action": "screenshot", "screenshot": ss})

        elif action == "reload":
            await tab.reload()

        elif action == "go_back":
            await tab.go_back()

        elif action == "go_forward":
            await tab.go_forward()

        elif action == "stop_loading":
            await tab.stop_loading()

        elif action == "query":
            if not step.by or not step.by.selector:
                raise HTTPException(status_code=400, detail="query requires 'by.selector'")
            if step.find_all:
                elements = await tab.query_all(step.by.selector)
                outputs.append({"action": "query", "count": len(elements)})
            else:
                element = await tab.query(step.by.selector)
                outputs.append({"action": "query", "found": bool(element)})

        elif action == "get_attribute":
            if not step.by or not step.attribute:
                raise HTTPException(status_code=400, detail="get_attribute requires 'by' and 'attribute'")
            element = await tab.find(**step.by.dict(exclude_none=True))
            val = await element.get_attribute(step.attribute)
            outputs.append({"action": "get_attribute", "attribute": step.attribute, "value": val})

        elif action == "new_tab":
            new_tab = await tab.new_tab(step.url, browser_context_id=step.browser_context_id)
            outputs.append({"action": "new_tab", "message": "New tab opened"})

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    return outputs

async def crawl_handler(request: CrawlRequest) -> Dict[str, Any]:
    options = Options()
    options.headless = True
    options.start_timeout = 30
    options.binary_location = os.getenv('CHROME_BIN')
    options.add_argument('--no-sandbox')

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        await tab.go_to(request.url)
        outputs = []
        if request.steps:
            outputs = await execute_steps(tab, request.steps)
        html = await tab.page_source
        return {"url": request.url, "html": html, "outputs": outputs}

@app.post("/crawl")
async def crawl(req: CrawlRequest):
    try:
        result = await crawl_handler(req)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
async def schema():
    """
    Returns the OpenAPI schema for the API in JSON format.
    """
    return JSONResponse(content=app.openapi())
