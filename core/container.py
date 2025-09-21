from dependency_injector import containers, providers
from services.cloudinary_service import CloudinaryService
from services.home_page_service import HomePageService
from services.vehicle_service import VehicleService
from services.category_service import CategoryService
from services.driver_service import DriverService

class Container(containers.DeclarativeContainer):
    # Services
    cloudinaryService = providers.Factory(CloudinaryService)
    homePageService = providers.Factory(HomePageService, cloudinaryService=cloudinaryService)
    vehicleService = providers.Factory(VehicleService, cloudinaryService=cloudinaryService)
    categoryService = providers.Factory(CategoryService, cloudinaryService=cloudinaryService)
    driverService = providers.Factory(DriverService, cloudinaryService=cloudinaryService)    