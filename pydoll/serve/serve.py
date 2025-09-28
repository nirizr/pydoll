# pydoll/serve.py
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Any, Dict, List
from .browser import Chrome
from .constants import Key  # for keyboard keys

app = FastAPI(title="Pydoll API")

async def execute_steps(tab, steps: List[Dict[str, Any]]):
    """
    Execute a list of steps on the given browser tab.
    Each step is a dict describing an action.
    """
    for step in steps:
        action = step.get("action")

        if action == "find":
            element = await tab.find(**step.get("by", {}))
            if "insert_text" in step:
                await element.insert_text(step["insert_text"])
            if step.get("click"):
                await element.click()

        elif action == "press_key":
            key_name = step.get("key")
            if not key_name:
                raise HTTPException(status_code=400, detail="press_key requires 'key'")
            key = getattr(Key, key_name, key_name)
            await tab.press_keyboard_key(key)

        elif action == "wait_for":
            await tab.find(**step.get("by", {}))

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

async def crawl_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle crawling: open Chrome, visit URL, execute steps, return HTML.
    """
    url = data.get("url")
    steps: List[Dict[str, Any]] = data.get("steps", [])
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' field")

    async with Chrome() as browser:
        tab = await browser.start()
        await tab.go_to(url)
        if steps:
            await execute_steps(tab, steps)
        html = await tab.content()
        return {"url": url, "html": html}

@app.post("/crawl")
async def crawl(data: Dict[str, Any] = Body(...)):
    """
    POST /crawl with JSON body:
    {
      "url": "https://example.com",
      "steps": [ ... ]
    }
    """
    try:
        result = await crawl_handler(data)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
