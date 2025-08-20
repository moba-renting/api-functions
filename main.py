# main.py
import os
import time
import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from core.container import Container
from api.rest.home_page_controller import router as homePageController

logger = logging.getLogger(__name__)

def createApp():
    # Initialize container
    container = Container()
    container.wire(modules=["api.rest.home_page_controller"])
    
    app = FastAPI()
    app.container = container

    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(homePageController)
    
    return app

app = createApp()

@app.get("/", include_in_schema=False, response_class=RedirectResponse)
async def redirectToSwagger():    
    logger.info("Redirect to swagger...")
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)