# Image Upload Service Documentation

## Overview

The Disfactory backend now supports multiple image upload backends with automatic fallback capabilities. This addresses the issue where Imgur's API is blocked in Taiwan by providing alternative upload services.

## Supported Backends

### 1. Imgur Backend
- **Service**: Imgur API v3
- **Configuration**: `DISFACTORY_IMGUR_CLIENT_ID`
- **Features**: High reliability, delete hash support
- **Limitations**: May be blocked in certain regions

### 2. ImageBB Backend
- **Service**: ImageBB API v1
- **Configuration**: `DISFACTORY_IMAGEBB_API_KEY`
- **Features**: Alternative to Imgur, good international availability
- **Limitations**: Requires API key registration

### 3. Local Storage Backend
- **Service**: Local file storage
- **Configuration**: Uses existing `MEDIA_ROOT` and `DOMAIN` settings
- **Features**: Always available, no external dependencies
- **Limitations**: Requires server storage space, no delete hash

## Configuration

Add to your environment variables:

```bash
# Existing Imgur configuration
DISFACTORY_IMGUR_CLIENT_ID=your_imgur_client_id

# New ImageBB configuration
DISFACTORY_IMAGEBB_API_KEY=your_imagebb_api_key
```

## API Endpoints

### 1. Direct File Upload (NEW)

**Endpoint**: `POST /api/factories/{factory_id}/images/upload`

**Content-Type**: `multipart/form-data`

**Parameters**:
- `image` (required): Image file
- `nickname` (optional): Reporter nickname
- `contact` (optional): Reporter contact
- `Latitude` (optional): GPS latitude
- `Longitude` (optional): GPS longitude  
- `DateTimeOriginal` (optional): Photo timestamp (format: `YYYY:mm:dd HH:MM:SS`)

**Example**:
```bash
curl -X POST \
  "https://api.disfactory.tw/api/factories/123/images/upload" \
  -F "image=@photo.jpg" \
  -F "nickname=Reporter" \
  -F "contact=reporter@example.com" \
  -F "Latitude=23.5" \
  -F "Longitude=120.5"
```

### 2. URL Upload (EXISTING)

**Endpoint**: `POST /api/factories/{factory_id}/images`

**Content-Type**: `application/json`

This endpoint remains unchanged for backward compatibility.

## How It Works

### Upload Process

1. **Service Initialization**: The `ImageUploadService` automatically detects configured backends based on environment variables.

2. **Backend Priority**: 
   - Imgur (if configured)
   - ImageBB (if configured) 
   - Local Storage (always available)

3. **Automatic Fallback**: If the first backend fails, the service automatically tries the next one until success or all backends are exhausted.

4. **Error Handling**: Comprehensive error logging and user-friendly error messages.

### Example Upload Flow

```
1. Client uploads image to /factories/123/images/upload
2. Service tries Imgur → Success ✓
3. Image saved to database with Imgur URL
4. Response returned to client

Alternative flow:
1. Client uploads image to /factories/123/images/upload  
2. Service tries Imgur → Fails (network error)
3. Service tries ImageBB → Success ✓
4. Image saved to database with ImageBB URL
5. Response returned to client
```

## Implementation Details

### Service Architecture

```python
ImageUploadService
├── ImgurBackend
├── ImageBBBackend  
└── LocalBackend
```

### Backend Interface

Each backend implements:
- `upload(image_buffer: bytes) -> Dict[str, Any]`
- `get_name() -> str`

### Error Handling

- Network timeouts (30 seconds)
- API rate limits and quota exceeded
- Invalid API keys/credentials
- Service unavailable errors
- Automatic fallback to next backend

## Backward Compatibility

- Existing URL-based upload endpoint unchanged
- Legacy `upload_image` task updated to use new service
- All existing functionality preserved
- Database schema unchanged

## Testing

Run the test suite:

```bash
# Test the image upload service
pytest api/tests/test_image_upload_service.py

# Test the new API endpoint
pytest api/tests/test_factory_image_file_upload.py

# Test legacy functionality
pytest api/tests/test_tasks.py
```

## Migration Guide

### For Frontend Developers

**New Direct Upload** (Recommended):
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('nickname', 'User');
formData.append('Latitude', '23.5');

fetch(`/api/factories/${factoryId}/images/upload`, {
  method: 'POST',
  body: formData
});
```

**Existing URL Upload** (Still Supported):
```javascript
// Upload to external service first, then send URL
const response = await uploadToImgur(imageFile);
fetch(`/api/factories/${factoryId}/images`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    url: response.data.link,
    deletehash: response.data.deletehash
  })
});
```

### For System Administrators

1. **Add ImageBB API Key** (optional but recommended):
   ```bash
   export DISFACTORY_IMAGEBB_API_KEY="your_key_here"
   ```

2. **Monitor Logs**: The service logs which backend was used for each upload and any failures.

3. **Storage Considerations**: If relying on local storage, ensure adequate disk space and backup procedures.

## Troubleshooting

### Common Issues

**All backends failing:**
- Check network connectivity
- Verify API keys are valid
- Ensure `MEDIA_ROOT` is writable for local fallback

**High error rates:**
- Monitor API quotas/rate limits
- Consider upgrading to paid plans for external services
- Check server resources for local storage

### Monitoring

Key metrics to monitor:
- Upload success rate by backend
- Average response time
- Storage usage (for local backend)
- API quota usage

## Future Enhancements

Potential improvements:
- Additional backends (Cloudinary, AWS S3, etc.)
- Image compression and optimization
- CDN integration
- Background processing for large images
- Image metadata extraction

## Security Considerations

- File type validation
- File size limits
- Virus scanning (recommended)
- Rate limiting per user/IP
- API key rotation procedures