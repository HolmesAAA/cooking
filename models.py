from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: str
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True


class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime


# Auth Models
class Token(BaseModel):
    token: str
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Media Models
class MediaBase(BaseModel):
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None


class MediaCreate(MediaBase):
    pass


class MediaUpdate(MediaBase):
    pass


class MediaResponse(MediaBase):
    id: str
    user_id: str = Field(alias="userId")
    file_name: str = Field(alias="fileName")
    original_file_name: str = Field(alias="originalFileName")
    media_type: str = Field(alias="mediaType")
    file_size: int = Field(alias="fileSize")
    mime_type: str = Field(alias="mimeType")
    blob_url: str = Field(alias="blobUrl")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    uploaded_at: datetime = Field(alias="uploadedAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class MediaInDB(BaseModel):
    id: str
    user_id: str
    file_name: str
    original_file_name: str
    media_type: str
    file_size: int
    mime_type: str
    blob_url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    uploaded_at: datetime
    updated_at: datetime


class MediaListResponse(BaseModel):
    items: List[MediaResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# Error Models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
