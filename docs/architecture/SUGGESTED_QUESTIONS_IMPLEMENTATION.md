# Topic Trending Suggested Questions - Implementation Complete ✅

## Overview
Implemented smart suggested questions based on **Topic Trending** (Phương án C) that analyzes trending topics from the last 24 hours and suggests popular questions from those topics.

## Architecture

### Backend Implementation

#### 1. Analytics Service (`src/services/analytics_service.py`)

**New Method: `get_trending_topics(hours_lookback=24)`**
- Analyzes topic growth rate by comparing two time periods
- Recent period: last 12 hours
- Previous period: 12-24 hours ago
- Calculates growth rate: `((recent - previous) / previous) * 100`
- Trending score formula: `(growth_rate * 0.4) + (recent_volume * 0.6)`
- Returns sorted list of trending topics with scores

**New Method: `get_suggested_questions(limit=5)`**
- Gets top 3 trending topics from `get_trending_topics()`
- Queries `conversations` and `topic_classifications` tables via JOIN
- Filters questions from last 7 days
- Removes duplicate/similar questions
- Falls back to sample questions if insufficient data
- Returns `PopularQuestion` models with count and last_asked timestamp

#### 2. API Endpoint (`src/api/routes.py`)

**New Endpoint: `GET /api/analytics/suggested-questions`**

Query Parameters:
- `limit`: Number of questions (1-10, default: 5)
- `force_refresh`: Force cache refresh (default: false)

Response Format:
```json
{
  "success": true,
  "questions": [
    {
      "question": "Điều kiện tuyển sinh năm 2025 như thế nào?",
      "count": 156,
      "last_asked": "2025-12-07 10:30:00"
    }
  ],
  "count": 5,
  "cached": true,
  "cache_age_seconds": 1800
}
```

**Caching Strategy:**
- In-memory cache with 1-hour TTL (3600 seconds)
- Cache stores up to 10 questions
- Returns limited subset based on `limit` parameter
- Includes cache metadata in response
- `force_refresh=true` bypasses cache

### Frontend Implementation

#### Updated: `frontend/src/app/chat-bot/page.tsx`

**State Management:**
```typescript
const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
const [loadingSuggestions, setLoadingSuggestions] = useState(false);
```

**API Integration:**
- Fetches questions on component mount via `useEffect`
- Endpoint: `/api/analytics/suggested-questions?limit=5`
- Falls back to hardcoded questions on error
- Updates fallback when language toggles

**UI Enhancements:**
- Loading skeleton (5 gray animated bars)
- Loading indicator text in heading
- Clickable question buttons populate input field
- Hover effects (red border, shadow)

## Database Schema

### Required Tables

**`topic_classifications`** (Already exists)
```sql
CREATE TABLE topic_classifications (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255),
    session_id VARCHAR(255),
    query TEXT NOT NULL,
    topic VARCHAR(100) NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_topic_class_topic ON topic_classifications(topic);
CREATE INDEX idx_topic_class_created ON topic_classifications(created_at);
```

**`conversations`** (Already exists)
```sql
CREATE TABLE conversations (
    conversation_id VARCHAR(255) PRIMARY KEY,
    user_message TEXT,
    bot_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ...
);
```

## Algorithm Details

### Trending Score Calculation

```
growth_rate = ((recent_count - previous_count) / previous_count) * 100
trending_score = (growth_rate × 0.4) + (recent_count × 0.6)
```

**Weight Distribution:**
- 40% growth rate (viral/emerging topics)
- 60% absolute volume (sustained popularity)

**Special Cases:**
- New topics (no previous count): `growth_rate = 200%`
- Ensures emerging topics get visibility

### Question Selection Process

1. Get top 3 trending topics
2. Query popular questions from those topics (last 7 days)
3. Join `conversations` with `topic_classifications`
4. Order by: count DESC, avg_confidence DESC
5. Deduplicate similar questions
6. Truncate long questions to 100 chars
7. Fill remaining slots with fallback questions

## Performance Optimizations

### Caching
- **Cache Duration:** 1 hour (3600 seconds)
- **Cache Storage:** In-memory (process-level)
- **Cache Key:** Global `_suggested_questions_cache`
- **Cache Size:** 10 questions (serves various limits)
- **Cache Metrics:** Returns age in response

### Database Indexes
- `topic_classifications.topic` - Fast topic filtering
- `topic_classifications.created_at` - Time-based queries
- `conversations.created_at` - Time-based queries

### Query Optimizations
- Time-windowed queries (24h trending, 7d questions)
- LIMIT clauses on all queries
- JOIN only on indexed columns

## Testing

### API Testing
```bash
# Test endpoint
curl http://localhost:8000/api/analytics/suggested-questions?limit=5

# Force cache refresh
curl http://localhost:8000/api/analytics/suggested-questions?limit=5&force_refresh=true

# Test with different limits
curl http://localhost:8000/api/analytics/suggested-questions?limit=3
```

### Frontend Testing
1. Open http://localhost:3000/chat-bot
2. Wait for suggestions to load (loading skeleton → questions)
3. Click a suggested question → should populate input
4. Check browser console for API call logs
5. Refresh page → should use cached data (fast load)

### Backend Testing
```python
# In Python console
from src.services.analytics_service import AnalyticsService

svc = AnalyticsService()

# Test trending topics
topics = svc.get_trending_topics(hours_lookback=24)
print(topics)

# Test suggested questions
questions = svc.get_suggested_questions(limit=5)
for q in questions:
    print(f"- {q.question} ({q.count} times)")
```

## Fallback Behavior

### No Trending Data
- Falls back to `_generate_sample_popular_questions()`
- Returns hardcoded Vietnamese questions
- Ensures system always returns suggestions

### Insufficient Questions
- Fills remaining slots with fallback questions
- Prevents empty suggestion lists
- Maintains 5-question minimum

### API Errors
- Frontend catches errors gracefully
- Uses language-specific fallback questions
- No UI disruption

## Configuration

### Adjustable Parameters

**Backend (`analytics_service.py`):**
```python
hours_lookback = 24      # Trending analysis window
limit = 5                # Default questions count
min_question_length = 10 # Filter short queries
```

**API (`routes.py`):**
```python
cache_ttl = 3600         # Cache duration (1 hour)
max_cached = 10          # Max cached questions
```

**Frontend (`page.tsx`):**
```typescript
limit = 5                // Questions to fetch
// Fallback questions array
```

## Monitoring & Logs

### Log Messages

**Trending Analysis:**
```
📈 Analyzed {N} trending topics
```

**Question Generation:**
```
✅ Generated {N} suggested questions from trending topics: [topics]
⚠️ Only found {N} questions, adding fallback
⚠️ No trending topics found, using fallback questions
```

**API Cache:**
```
📦 Returning cached suggested questions
🔄 Fetching fresh suggested questions (cache miss or expired)
```

## Future Enhancements

### Potential Improvements
1. **Multi-language Support**: Separate suggestions for VI/EN
2. **User Segmentation**: Different suggestions by user type
3. **Time-of-Day Weighting**: Morning vs evening topics
4. **Redis Cache**: Replace in-memory with Redis for multi-worker
5. **A/B Testing**: Compare suggestion algorithms
6. **Click Tracking**: Monitor which suggestions are used
7. **Personalization**: Use session history for recommendations

### Analytics Dashboard
- Add "Trending Topics" chart
- Show suggestion click-through rate
- Display cache hit/miss ratio
- Monitor question freshness

## Dependencies

### Python Packages
- `sqlalchemy` - Database queries
- `fastapi` - API endpoint
- `pydantic` - Data models

### Database
- PostgreSQL with `topic_classifications` table
- Requires active topic tracking

### Frontend
- React hooks (`useState`, `useEffect`)
- Fetch API

## Deployment Notes

1. **Database Migration**: No schema changes required (tables exist)
2. **API Compatibility**: Backward compatible (new endpoint)
3. **Frontend Build**: Rebuild Next.js after deployment
4. **Cache Warmup**: First request will be slow (cache miss)
5. **Monitoring**: Watch for trending topic data availability

## Summary

✅ **Backend:** 2 new methods, 1 API endpoint with caching
✅ **Frontend:** Dynamic question loading with skeleton UI
✅ **Performance:** 1-hour cache, optimized queries
✅ **Reliability:** Multiple fallback layers
✅ **User Experience:** Smooth loading, instant suggestions

The system intelligently suggests questions based on what's trending right now, updating every hour to stay relevant!
