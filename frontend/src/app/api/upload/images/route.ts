import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

const USER_IMAGES_BUCKET = 'user-images';

export async function POST(request: NextRequest) {
  try {
    const data = await request.formData();
    const files: File[] = [];
    
    // Extract all files from formData
    for (const [key, value] of data.entries()) {
      if (key.startsWith('images') && value instanceof File) {
        files.push(value);
      }
    }

    if (files.length === 0) {
      return NextResponse.json({ 
        success: false, 
        error: 'Không có file nào được tải lên' 
      }, { status: 400 });
    }

    const uploadResults = [];

    for (const file of files) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        return NextResponse.json({ 
          success: false, 
          error: `File "${file.name}" không phải là ảnh hợp lệ` 
        }, { status: 400 });
      }

      // Validate file size (5MB = 5 * 1024 * 1024 bytes)
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        return NextResponse.json({ 
          success: false, 
          error: `Ảnh "${file.name}" vượt quá 5MB (hiện tại: ${sizeMB}MB)` 
        }, { status: 400 });
      }

      // Generate unique filename
      const timestamp = Date.now();
      const randomString = Math.random().toString(36).substring(2, 15);
      const fileExtension = file.name.split('.').pop() || 'jpg';
      const fileName = `img_${timestamp}_${randomString}.${fileExtension}`;
      
      // Convert file to array buffer
      const arrayBuffer = await file.arrayBuffer();
      
      try {
        // Upload to Supabase Storage (assuming bucket exists)
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from(USER_IMAGES_BUCKET)
          .upload(fileName, arrayBuffer, {
            contentType: file.type,
            cacheControl: '3600',
            upsert: false
          });

        if (uploadError) {
          console.error('Upload error details:', uploadError);
          // Fall back to local storage/base64 if Supabase fails
          const base64 = Buffer.from(arrayBuffer).toString('base64');
          uploadResults.push({
            id: `${timestamp}_${randomString}`,
            originalName: file.name,
            fileName: fileName,
            url: `data:${file.type};base64,${base64}`,
            size: file.size,
            mimeType: file.type,
            uploadedAt: new Date().toISOString(),
            supabaseError: uploadError.message,
            fallbackMode: true
          });
          continue;
        }

        // Get public URL
        const { data: urlData } = supabase.storage
          .from(USER_IMAGES_BUCKET)
          .getPublicUrl(fileName);
        
        uploadResults.push({
          id: `${timestamp}_${randomString}`,
          originalName: file.name,
          fileName: fileName,
          url: urlData.publicUrl,
          size: file.size,
          mimeType: file.type,
          uploadedAt: new Date().toISOString(),
          supabasePath: uploadData.path,
          uploaded: true
        });
      } catch (error) {
        console.error('Supabase upload failed:', error);
        // Fall back to base64 encoding
        const base64 = Buffer.from(arrayBuffer).toString('base64');
        uploadResults.push({
          id: `${timestamp}_${randomString}`,
          originalName: file.name,
          fileName: fileName,
          url: `data:${file.type};base64,${base64}`,
          size: file.size,
          mimeType: file.type,
          uploadedAt: new Date().toISOString(),
          fallbackMode: true
        });
      }
    }

    return NextResponse.json({
      success: true,
      message: `Đã xử lý ${uploadResults.length} ảnh thành công`,
      files: uploadResults
    });

  } catch (error) {
    console.error('Error processing images:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Lỗi khi tải lên ảnh. Vui lòng thử lại.' 
      },
      { status: 500 }
    );
  }
}

// API để lấy danh sách ảnh đã upload - simplified version
export async function GET(request: NextRequest) {
  try {
    // For now, return empty array since we don't have reliable Supabase access
    return NextResponse.json({
      success: true,
      files: [],
      total: 0,
      message: 'Gallery feature đang được phát triển'
    });

  } catch (error) {
    console.error('Error getting uploaded images:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Lỗi khi lấy danh sách ảnh' 
      },
      { status: 500 }
    );
  }
}