import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Test Supabase connection
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

export async function GET(request: NextRequest) {
  try {
    console.log('Testing Supabase connection...');
    console.log('URL:', supabaseUrl);
    console.log('Anon Key (first 20 chars):', supabaseAnonKey?.substring(0, 20));
    console.log('Service Key (first 20 chars):', supabaseServiceKey?.substring(0, 20));

    // Test with anon key
    const supabaseAnon = createClient(supabaseUrl, supabaseAnonKey);
    
    try {
      const { data: buckets, error } = await supabaseAnon.storage.listBuckets();
      console.log('Anon key test - Buckets:', buckets);
      console.log('Anon key test - Error:', error);
    } catch (e) {
      console.log('Anon key test failed:', e);
    }

    // Test with service key
    const supabaseService = createClient(supabaseUrl, supabaseServiceKey);
    
    try {
      const { data: buckets, error } = await supabaseService.storage.listBuckets();
      console.log('Service key test - Buckets:', buckets);
      console.log('Service key test - Error:', error);
      
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
      console.log('Service key test failed:', e);
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