from fastapi import APIRouter, Depends, UploadFile, File, Query
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
    return {"message": homePageService.addHeroBannerImage(image)}

@router.delete("/hero-banner/remove")
@inject
async def removeHeroBannerImage( 
    imageUrl: str = Query(...),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    return {"message": homePageService.removeHeroBannerImage(imageUrl)}

@router.put("/b2b-benefits")
@inject
async def upsertB2bBenefitsImage( 
    image: UploadFile = File(...),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    return {"message": homePageService.upsertB2bBenefitsImage(image)}

@router.put("/b2c-benefits")
@inject
async def upsertB2cBenefitsImage( 
    image: UploadFile = File(...),
    homePageService: HomePageService = Depends(Provide[Container.homePageService])
):
    return {"message": homePageService.upsertB2cBenefitsImage(image)}
