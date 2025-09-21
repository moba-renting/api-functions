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
from api.rest.vehicle_controller import router as vehicleController
from api.rest.category_controller import router as categoryController
from api.rest.driver_controller import router as driverController

logger = logging.getLogger(__name__)

def createApp():
    # Initialize container
    container = Container()
    container.wire(modules=["api.rest.home_page_controller", "api.rest.vehicle_controller", "api.rest.category_controller", "api.rest.driver_controller"])
    
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
    app.include_router(vehicleController)
    app.include_router(categoryController)
    app.include_router(driverController)
    
    return app

app = createApp()

@app.get("/", include_in_schema=False, response_class=RedirectResponse)
async def redirectToSwagger():    
    logger.info("Redirect to swagger...")
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)