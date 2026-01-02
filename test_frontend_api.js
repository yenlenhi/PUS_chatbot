// Test frontend analytics API call
// This simulates what the React dashboard does

const API_BASE_URL = 'http://localhost:8000';

// Test the analytics API
async function testAnalyticsAPI() {
    console.log('🧪 Testing Frontend Analytics API...\n');
    
    try {
        // Test overview
        console.log('📊 Testing overview...');
        const overviewResponse = await fetch(`${API_BASE_URL}/api/v1/analytics/overview`);
        if (overviewResponse.ok) {
            const overview = await overviewResponse.json();
            console.log('✅ Overview:', overview.total_conversations, 'conversations');
        }
        
        // Test user insights
        console.log('👥 Testing user insights...');
        const userResponse = await fetch(`${API_BASE_URL}/api/v1/analytics/users?time_range=L7D`);
        if (userResponse.ok) {
            const userInsights = await userResponse.json();
            console.log('✅ User insights popular questions count:', userInsights.popular_questions?.length || 0);
            if (userInsights.popular_questions?.length > 0) {
                console.log('  Sample question:', userInsights.popular_questions[0].question);
            }
        }
        
        // Test new popular questions endpoint
        console.log('❓ Testing new popular questions endpoint...');
        const popularResponse = await fetch(`${API_BASE_URL}/api/v1/analytics/popular-questions?time_range=L7D&limit=5`);
        if (popularResponse.ok) {
            const popularData = await popularResponse.json();
            console.log('✅ Popular questions response:');
            console.log('  Data source:', popularData.data_source);
            console.log('  Total count:', popularData.total_count);
            console.log('  Time range:', popularData.time_range);
            
            if (popularData.popular_questions?.length > 0) {
                console.log('  Questions:');
                popularData.popular_questions.forEach((q, i) => {
                    console.log(`    ${i+1}. ${q.question} (${q.count} times)`);
                });
            }
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log('💡 Make sure the backend server is running on localhost:8000');
    }
}

// Check if running in Node.js environment
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment - use fetch polyfill
    const fetch = require('node-fetch');
    testAnalyticsAPI();
} else {
    // Browser environment
    testAnalyticsAPI();
}