from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Azure Cosmos DB Configuration
    cosmos_endpoint: str
    cosmos_key: str
    cosmos_database_name: str = "CloudMediaDB"

    # Azure Blob Storage Configuration
    azure_storage_connection_string: str
    blob_container_name: str = "media-files"

    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:4200"

    # File Upload Configuration
    max_file_size_mb: int = 100
    allowed_image_types: str = "image/jpeg,image/png,image/gif,image/webp"
    allowed_video_types: str = "video/mp4,video/mpeg,video/quicktime,video/webm"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip() for t in self.allowed_image_types.split(",")]

    @property
    def allowed_video_types_list(self) -> List[str]:
        return [t.strip() for t in self.allowed_video_types.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
