import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const isDev = process.env.NODE_ENV === 'development';
const isRouteEnabled = process.env.ENABLE_SUPABASE_TEST_ROUTE === 'true';

export async function GET() {
  if (!isDev || !isRouteEnabled) {
    return new NextResponse(null, { status: 404 });
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
  const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

  try {
    // Test with anon key
    const supabaseAnon = createClient(supabaseUrl, supabaseAnonKey);
    
    try {
      await supabaseAnon.storage.listBuckets();
    } catch (e) {
      // ignore anon failures to proceed with service key test
    }

    // Test with service key
    const supabaseService = createClient(supabaseUrl, supabaseServiceKey);
    
    try {
      const { data: buckets, error } = await supabaseService.storage.listBuckets();
      
      if (buckets) {
        return NextResponse.json({
          success: true,
          buckets: buckets,
          message: 'Supabase connection successful'
        });
      } else {
        return NextResponse.json({
          success: false,
          error: error?.message || 'Unknown error',
          message: 'Failed to list buckets'
        }, { status: 500 });
      }
    } catch (e) {
      return NextResponse.json({
        success: false,
        error: e instanceof Error ? e.message : 'Unknown error',
        message: 'Service key test failed'
      }, { status: 500 });
    }

  } catch (error) {
    console.error('Supabase test error:', error);
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'Supabase connection failed'
    }, { status: 500 });
  }
}
