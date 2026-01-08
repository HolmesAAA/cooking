from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.cosmos.container import ContainerProxy
from typing import Optional, List, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class CosmosDBClient:
    def __init__(self):
        self.client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
        self.database = None
        self.users_container = None
        self.media_container = None

    def initialize(self):
        """Initialize database and containers"""
        try:
            # Create database if it doesn't exist
            self.database = self.client.create_database_if_not_exists(
                id=settings.cosmos_database_name
            )
            logger.info(f"Database '{settings.cosmos_database_name}' is ready")

            # Create users container if it doesn't exist
            self.users_container = self.database.create_container_if_not_exists(
                id="users",
                partition_key=PartitionKey(path="/id"),
                offer_throughput=400,
            )
            logger.info("Users container is ready")

            # Create media container if it doesn't exist
            self.media_container = self.database.create_container_if_not_exists(
                id="media",
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400,
            )
            logger.info("Media container is ready")

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            raise

    # User operations
    def create_user(self, user_data: dict) -> dict:
        """Create a new user"""
        try:
            return self.users_container.create_item(body=user_data)
        except exceptions.CosmosResourceExistsError:
            raise ValueError("User already exists")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            query = "SELECT * FROM users u WHERE u.email = @email"
            parameters = [{"name": "@email", "value": email}]
            items = list(
                self.users_container.query_items(
                    query=query, parameters=parameters, enable_cross_partition_query=True
                )
            )
            return items[0] if items else None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user by email: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            return self.users_container.read_item(item=user_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise

    # Media operations
    def create_media(self, media_data: dict) -> dict:
        """Create a new media item"""
        try:
            return self.media_container.create_item(body=media_data)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create media: {e}")
            raise

    def get_media_by_id(self, media_id: str, user_id: str) -> Optional[dict]:
        """Get media by ID"""
        try:
            return self.media_container.read_item(item=media_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get media by ID: {e}")
            raise

    def get_user_media(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        media_type: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """Get paginated list of user's media"""
        try:
            # Build query
            query = "SELECT * FROM media m WHERE m.userId = @userId"
            parameters = [{"name": "@userId", "value": user_id}]

            if media_type:
                query += " AND m.mediaType = @mediaType"
                parameters.append({"name": "@mediaType", "value": media_type})

            query += " ORDER BY m.uploadedAt DESC"

            # Get total count
            count_query = query.replace("SELECT *", "SELECT VALUE COUNT(1)")
            count_result = list(
                self.media_container.query_items(
                    query=count_query, parameters=parameters
                )
            )
            total = count_result[0] if count_result else 0

            # Apply pagination
            offset = (page - 1) * page_size
            query += f" OFFSET {offset} LIMIT {page_size}"

            items = list(
                self.media_container.query_items(query=query, parameters=parameters)
            )

            return items, total

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user media: {e}")
            raise

    def update_media(self, media_id: str, user_id: str, updates: dict) -> dict:
        """Update media metadata"""
        try:
            # Get existing item
            existing = self.get_media_by_id(media_id, user_id)
            if not existing:
                raise ValueError("Media not found")

            # Update fields
            existing.update(updates)

            # Save updated item
            return self.media_container.replace_item(
                item=media_id, body=existing
            )
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update media: {e}")
            raise

    def delete_media(self, media_id: str, user_id: str) -> bool:
        """Delete media item"""
        try:
            self.media_container.delete_item(item=media_id, partition_key=user_id)
            return True
        except exceptions.CosmosResourceNotFoundError:
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete media: {e}")
            raise

    def search_media(
        self, user_id: str, query: str, page: int = 1, page_size: int = 20
    ) -> tuple[List[dict], int]:
        """Search media by filename, description, or tags"""
        try:
            # Build search query
            search_query = """
                SELECT * FROM media m
                WHERE m.userId = @userId
                AND (
                    CONTAINS(LOWER(m.originalFileName), LOWER(@query))
                    OR CONTAINS(LOWER(m.description), LOWER(@query))
                    OR ARRAY_CONTAINS(m.tags, @query, true)
                )
                ORDER BY m.uploadedAt DESC
            """
            parameters = [
                {"name": "@userId", "value": user_id},
                {"name": "@query", "value": query},
            ]

            # Get total count
            count_query = search_query.replace("SELECT *", "SELECT VALUE COUNT(1)")
            count_result = list(
                self.media_container.query_items(
                    query=count_query, parameters=parameters
                )
            )
            total = count_result[0] if count_result else 0

            # Apply pagination
            offset = (page - 1) * page_size
            search_query += f" OFFSET {offset} LIMIT {page_size}"

            items = list(
                self.media_container.query_items(
                    query=search_query, parameters=parameters
                )
            )

            return items, total

        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to search media: {e}")
            raise


# Global instance
cosmos_db = CosmosDBClient()
