# Cloud Media Platform - Backend API

A FastAPI-based REST API for cloud media storage and management, integrated with Azure Cosmos DB and Azure Blob Storage.

## Features

- User authentication with JWT tokens
- Image and video upload to Azure Blob Storage
- Metadata storage in Azure Cosmos DB for NoSQL
- Automatic thumbnail generation for images
- Media search and filtering
- Pagination support
- CORS enabled for frontend integration

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: Azure Cosmos DB for NoSQL
- **Storage**: Azure Blob Storage
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Image Processing**: Pillow

## Project Structure

```
bancked/
├── app.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── models.py              # Pydantic models for request/response
├── auth.py                # Authentication utilities (JWT, password hashing)
├── database.py            # Azure Cosmos DB integration
├── storage.py             # Azure Blob Storage integration
├── utils.py               # Utility functions (file validation, thumbnails)
├── routes_auth.py         # Authentication endpoints
├── routes_media.py        # Media management endpoints
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- Azure account with:
  - Azure Cosmos DB account
  - Azure Storage account
- pip package manager

### 2. Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Azure Configuration

#### Create Azure Cosmos DB

1. Create a Cosmos DB account in Azure Portal
2. Choose API: **Core (SQL) - NoSQL**
3. Create a database named `CloudMediaDB`
4. The containers will be created automatically on first run:
   - `users` (Partition Key: `/id`)
   - `media` (Partition Key: `/userId`)

#### Create Azure Blob Storage

1. Create a Storage account in Azure Portal
2. The container `media-files` will be created automatically on first run
3. Enable CORS for your frontend domain in Storage account settings

### 4. Environment Variables

Create a `.env` file in the `bancked` directory by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your Azure credentials:

```env
# Azure Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-cosmosdb-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-db-primary-key
COSMOS_DATABASE_NAME=CloudMediaDB

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-storage-account;AccountKey=your-storage-key;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=media-files

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:4200

# File Upload Configuration
MAX_FILE_SIZE_MB=100
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/gif,image/webp
ALLOWED_VIDEO_TYPES=video/mp4,video/mpeg,video/quicktime,video/webm
```

**Important**:
- Get your Cosmos DB endpoint and key from Azure Portal → Cosmos DB → Keys
- Get your Storage connection string from Azure Portal → Storage Account → Access keys

### 5. Running the Application

```bash
# Development mode with auto-reload
python app.py

# Or using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API Base: http://localhost:8000/api
- Documentation: http://localhost:8000/api/docs
- Alternative Docs: http://localhost:8000/api/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Media Management

- `POST /api/media` - Upload media file (requires auth)
- `GET /api/media` - Get user's media list (requires auth)
- `GET /api/media/{id}` - Get media details (requires auth)
- `PUT /api/media/{id}` - Update media metadata (requires auth)
- `DELETE /api/media/{id}` - Delete media (requires auth)
- `GET /api/media/search?query=...` - Search media (requires auth)

### Health Check

- `GET /api/health` - API health status

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

To get a token:
1. Register: `POST /api/auth/register`
2. Login: `POST /api/auth/login`
3. Use the returned token in subsequent requests

## Example Usage

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Upload Media

```bash
curl -X POST http://localhost:8000/api/media \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "description=My vacation photo" \
  -F 'tags=["vacation", "2025", "beach"]'
```

### Get Media List

```bash
curl -X GET "http://localhost:8000/api/media?page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Development

### Testing API with Swagger UI

1. Start the server
2. Open http://localhost:8000/api/docs
3. Click "Authorize" button
4. Enter your JWT token (get it from login/register)
5. Test endpoints interactively

### Logging

The application uses Python's built-in logging. Logs include:
- Request processing
- Azure service operations
- Errors and exceptions

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- File type validation (whitelist approach)
- File size limits (100MB default)
- User-specific data access control
- CORS protection

## File Upload Limits

- **Max file size**: 100MB (configurable)
- **Allowed image types**: JPEG, PNG, GIF, WebP
- **Allowed video types**: MP4, MPEG, QuickTime, WebM

## Troubleshooting

### Common Issues

1. **Connection to Cosmos DB fails**
   - Verify COSMOS_ENDPOINT and COSMOS_KEY in `.env`
   - Check network connectivity to Azure
   - Ensure Cosmos DB firewall allows your IP

2. **Blob upload fails**
   - Verify AZURE_STORAGE_CONNECTION_STRING in `.env`
   - Check Storage account firewall settings
   - Ensure container name is correct

3. **CORS errors from frontend**
   - Add your frontend URL to ALLOWED_ORIGINS in `.env`
   - Restart the server after changing `.env`

4. **JWT token errors**
   - Ensure JWT_SECRET_KEY is set and consistent
   - Check token expiration time
   - Verify token format in Authorization header

## Production Deployment

For production deployment:

1. **Set strong JWT secret**: Generate a secure random key
2. **Use environment variables**: Never commit `.env` to version control
3. **Enable HTTPS**: Use a reverse proxy (nginx, Azure App Service)
4. **Set up monitoring**: Use Azure Application Insights
5. **Configure firewall**: Restrict Cosmos DB and Storage access
6. **Scale settings**: Adjust Cosmos DB throughput based on usage
7. **Backup**: Enable point-in-time restore for Cosmos DB``