# Local Image Upload Service

## Overview

This implementation replaces the Imgur API with a local filesystem-based image upload service that maintains API compatibility with minimal frontend/backend changes.

## Files Added

### `api/services/image_upload.py`
Core service for handling image uploads with:
- EXIF data extraction (GPS coordinates and datetime) before stripping
- Image format validation and size limits
- UUID-based filename generation
- Local filesystem storage
- Imgur-compatible response format

### `api/views/upload_image.py`
Django view providing the `/api/upload-image` endpoint:
- Accepts `multipart/form-data` with `image` field
- Returns Imgur-compatible JSON responses
- Comprehensive error handling
- Swagger documentation

### `api/views/tests/test_upload_image.py`
Test suite covering:
- Image upload service functionality
- EXIF data extraction
- Error handling scenarios
- API endpoint behavior

## API Specification

### Endpoint
- **URL**: `POST /api/upload-image`
- **Content-Type**: `multipart/form-data`

### Request Format
```
FormData:
  image: <file> (image binary data)
```

### Response Format (Success)
```json
{
  "data": {
    "link": "https://api.disfactory.tw/media/550e8400-e29b-41d4-a716-446655440000.jpg",
    "deletehash": "delete_550e8400e29b41d4a716446655440000",
    "Latitude": 23.8103,
    "Longitude": 121.5598,
    "DateTimeOriginal": "2023:08:27 15:30:45"
  },
  "success": true,
  "status": 200
}
```

### Response Format (Error)
```json
{
  "data": {
    "error": "Invalid image format"
  },
  "success": false,
  "status": 400
}
```

## Configuration

### Environment Variables
- `DISFACTORY_BACKEND_DOMAIN`: Base domain for constructing image URLs
- `DISFACTORY_BACKEND_MEDIA_ROOT`: Local storage path for uploaded images
- `MEDIA_URL`: URL path for media files (configured in Django settings)

### Example Configuration
```bash
DISFACTORY_BACKEND_DOMAIN="https://api.disfactory.tw/"
DISFACTORY_BACKEND_MEDIA_ROOT="/app/media"
```

## Features

### Image Processing
1. **File Validation**: Checks file size (max 10MB) and format (JPEG, PNG, WEBP)
2. **EXIF Extraction**: Preserves GPS coordinates and datetime before stripping
3. **EXIF Stripping**: Removes all metadata for privacy using PIL
4. **Format Conversion**: Converts all images to JPEG for consistency
5. **UUID Naming**: Generates secure filenames using UUID4

### Security Features
- File type validation (only image formats allowed)
- File size limits (10MB max)
- UUID-based filenames prevent directory traversal
- EXIF data stripping for privacy
- No executable file uploads

### Error Handling
- `400 Bad Request`: Invalid file format, file too large, missing file
- `413 Request Entity Too Large`: File exceeds size limit
- `500 Internal Server Error`: Storage or processing errors

## Integration

### Minimal Changes Required
1. **Frontend**: Change upload endpoint from Imgur to `/api/upload-image`
2. **Backend**: No changes to existing image handling code required
3. **Database**: Uses existing `Image` model with current fields

### Compatibility
- Response format identical to Imgur API
- EXIF data extraction provides same metadata fields
- Existing image views (`post_image_url`, `post_factory_image_url`) work unchanged

## Testing

### Unit Tests
Run comprehensive tests covering:
```bash
cd backend
python /tmp/test_image_upload.py      # Core service tests
python /tmp/test_full_workflow.py     # Integration tests
python /tmp/verify_specification.py   # Specification compliance
```

### Manual Testing
```bash
# Create test image and test with cURL
python /tmp/create_test_files.py
/tmp/test_curl_upload.sh
```

## Production Deployment

### Docker Configuration
```yaml
services:
  web:
    volumes:
      - ${DISFACTORY_BACKEND_MEDIA_ROOT}:/app/media
    environment:
      - DISFACTORY_BACKEND_MEDIA_ROOT=/app/media
      - DISFACTORY_BACKEND_DOMAIN=${DISFACTORY_BACKEND_DOMAIN}
```

### Reverse Proxy
Configure Nginx/Caddy to serve media files:
```nginx
location /media/ {
    alias /app/media/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Migration Strategy

1. Deploy new service alongside existing Imgur integration
2. Test with sample uploads to verify functionality
3. Update frontend to use local endpoint
4. Monitor for any issues with existing image URLs
5. Remove Imgur client ID configuration when ready

## Dependencies

- **Python Standard Library**: `os`, `uuid`, `logging`, `urllib.parse`, `datetime`
- **Django**: Core framework and file handling
- **Pillow**: Image processing and EXIF handling

No additional third-party dependencies required.