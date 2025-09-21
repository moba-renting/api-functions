from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import List
from dependency_injector.wiring import inject, Provide
from core.container import Container
from services.home_page_service import HomePageService

# Definir el router con prefijo y etiqueta
router = APIRouter(
    prefix="/api/v1/home-page",
    tags=["home-page"]
)

@router.post("/hero-banner/add")
@inject
async def addHeroBannerImage( 
    image: UploadFile = File(...),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    url = homePageService.addHeroBannerImage(image)
    return {"url": url}

@router.delete("/hero-banner/remove")
@inject
async def removeHeroBannerImage( 
    imageUrls: List[str] = Query(..., description="URLs of the images to delete"),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    homePageService.removeHeroBannerImage(imageUrls)
    return

@router.put("/b2b-benefits")
@inject
async def upsertB2bBenefitsImage( 
    image: UploadFile = File(...),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    url = homePageService.upsertB2bBenefitsImage(image)
    return {"url": url}

@router.put("/b2c-benefits")
@inject
async def upsertB2cBenefitsImage( 
    image: UploadFile = File(...),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    url = homePageService.upsertB2cBenefitsImage(image)
    return {"url": url}
