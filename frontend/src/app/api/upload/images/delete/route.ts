import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://thessjemstjljfbkvzih.supabase.co';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

const USER_IMAGES_BUCKET = 'user-images';

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const fileName = searchParams.get('fileName');
    const filePath = searchParams.get('filePath');

    if (!fileName && !filePath) {
      return NextResponse.json({
        success: false,
        error: 'Thiếu thông tin fileName hoặc filePath'
      }, { status: 400 });
    }

    const targetPath = filePath || fileName!;

    // Delete file from Supabase Storage
    const { error } = await supabase.storage
      .from(USER_IMAGES_BUCKET)
      .remove([targetPath]);

    if (error) {
      console.error('Error deleting file from Supabase:', error);
      return NextResponse.json({
        success: false,
        error: `Lỗi xóa ảnh: ${error.message}`
      }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      message: 'Đã xóa ảnh thành công'
    });

  } catch (error) {
    console.error('Error deleting image:', error);
    return NextResponse.json({
      success: false,
      error: 'Lỗi khi xóa ảnh'
    }, { status: 500 });
  }
}