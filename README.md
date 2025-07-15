# PriceX - Intelligent Price Comparison Platform

## Overview

PriceX is a price comparison platform that scrapes product information from Amazon and Flipkart. The system now includes a sophisticated, self-hosted proxy management system that provides a free alternative to paid proxy services.

## Features

- **Product Search**: Compare prices across Amazon and Flipkart
- **Intelligent Proxy Management**: Self-hosted proxy rotation system
- **Resilient Scraping**: Automatic retry logic with exponential backoff
- **User Agent Rotation**: Randomized headers to avoid detection
- **Concurrent Processing**: High-performance parallel proxy validation
- **Smart Caching**: Persistent proxy pool with automatic refresh

## Architecture

### Backend Components

1. **Proxy Sourcing (`proxy_sourcing.py`)**
   - Fetches free proxies from multiple public sources
   - Handles source failures gracefully
   - Deduplicates and formats proxy lists

2. **Proxy Validation (`proxy_validator.py`)**
   - Concurrent validation of proxy health
   - Configurable timeout and worker limits
   - Multiple test endpoints for reliability

3. **Proxy Pool Manager (`proxy_pool_manager.py`)**
   - Thread-safe singleton proxy management
   - Automatic pool replenishment
   - Persistent caching with timestamp validation
   - Performance statistics tracking

4. **Utilities (`utils.py`)**
   - Random user agent generation
   - Common header construction
   - Proxy format validation

5. **Enhanced Scraper (`scrapers/scraper.py`)**
   - Integrated proxy management
   - Retry logic with exponential backoff
   - Comprehensive error handling

### Database Schema

- **Products Table**: Stores product information (ASIN, title, URL)
- **Price History Table**: Tracks price changes over time with images

## Installation

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create `backend/.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost/pricecompare
   UPSTASH_REDIS_URL=redis://localhost:6379
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Initialize Database**
   ```bash
   cd backend
   python database.py
   ```

## Usage

### Starting the Services

1. **Start Backend**
   ```bash
   cd backend
   python main.py
   ```

2. **Start Celery Worker**
   ```bash
   cd backend
   celery -A worker.celery_app worker --loglevel=info
   ```

3. **Start Frontend**
   ```bash
   yarn dev
   ```

### API Endpoints

- `GET /search?q=<query>` - Initiate product search
- `GET /results?q=<query>` - Get search results

## Proxy Management System

### How It Works

1. **Sourcing**: Fetches proxies from multiple free proxy websites
2. **Validation**: Tests each proxy concurrently for health and speed
3. **Pool Management**: Maintains a queue of healthy proxies
4. **Rotation**: Automatically rotates through proxies for requests
5. **Failure Handling**: Removes failed proxies and replenishes pool

### Key Features

- **No API Keys Required**: Completely self-hosted solution
- **High Concurrency**: Validates up to 50 proxies simultaneously
- **Smart Caching**: Caches validated proxies for 30 minutes
- **Automatic Recovery**: Replenishes proxy pool when running low
- **Performance Monitoring**: Real-time statistics and health metrics

### Configuration

The proxy system is highly configurable:

```python
# In proxy_validator.py
validator = ProxyValidator(
    max_workers=50,    # Concurrent validation threads
    timeout=8          # Request timeout in seconds
)

# In proxy_pool_manager.py
cache_max_age = 30 * 60      # Cache lifetime (30 minutes)
min_pool_size = 10           # Minimum proxies in pool
max_pool_size = 100          # Maximum proxies in pool
```

## Important Notes

### Free Proxy Limitations

- **Success Rate**: Free proxies typically have a 5-15% success rate
- **First Run**: Initial proxy validation may take 2-5 minutes
- **Performance**: Free proxies are generally slower than paid alternatives
- **Reliability**: Some requests may fail even with healthy proxies

### Recommendations

1. **Be Patient**: First run requires time for proxy validation
2. **Monitor Logs**: Check application logs for proxy health status
3. **Adjust Timeouts**: Increase timeouts if experiencing frequent failures
4. **Scale Workers**: Increase validation workers for faster proxy processing

## Development

### Testing Components

1. **Test Proxy Sourcing**
   ```bash
   cd backend
   python proxy_sourcing.py
   ```

2. **Test Proxy Validation**
   ```bash
   cd backend
   python proxy_validator.py
   ```

3. **Test Proxy Pool Manager**
   ```bash
   cd backend
   python proxy_pool_manager.py
   ```

### Monitoring

The system provides comprehensive statistics:

```python
from proxy_pool_manager import get_proxy_manager

manager = get_proxy_manager()
stats = manager.get_stats()
print(f"Pool size: {stats['pool_size']}")
print(f"Success rate: {stats['total_validated'] / stats['total_sourced'] * 100:.1f}%")
```

## Troubleshooting

### Common Issues

1. **No Proxies Found**
   - Check internet connection
   - Verify proxy sources are accessible
   - Try forcing a refresh: `manager.force_refresh()`

2. **Slow Performance**
   - Increase timeout values
   - Reduce concurrent workers
   - Clear failed proxy cache

3. **High Failure Rate**
   - Normal for free proxies
   - Consider adjusting retry counts
   - Monitor proxy source quality

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- Free proxies may log or monitor traffic
- Avoid sensitive operations through free proxies
- Consider implementing IP whitelisting for production
- Monitor proxy usage patterns

## Future Enhancements

- Integration with Google Gemini for review analysis
- Product URL analysis (ASIN/PID extraction)
- Cross-platform product matching
- Advanced review sentiment analysis
- Machine learning-based proxy quality scoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details