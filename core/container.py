from dependency_injector import containers, providers
from services.cloudinary_service import CloudinaryService
from services.home_page_service import HomePageService

class Container(containers.DeclarativeContainer):
    # Services
    cloudinaryService = providers.Factory(CloudinaryService)
    homePageService = providers.Factory(HomePageService, cloudinaryService=cloudinaryService)    