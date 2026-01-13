import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { createHmac, timingSafeEqual } from 'crypto';

// Supabase configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://thessjemstjljfbkvzih.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const jwtSecret = process.env.JWT_SECRET_KEY || 'your-secret-key-change-this-in-production';
const jwtAlgorithm = process.env.JWT_ALGORITHM || 'HS256';

const USER_IMAGES_BUCKET = 'user-images';

type JwtPayload = {
  sub?: string;
  user_id?: string;
  scopes?: string[];
  exp?: number;
};

function base64UrlDecode(input: string): Buffer {
  const normalized = input.replace(/-/g, '+').replace(/_/g, '/');
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
  return Buffer.from(padded, 'base64');
}

function parseJwt(token: string): JwtPayload {
  const [headerPart, payloadPart, signaturePart] = token.split('.');
  if (!headerPart || !payloadPart || !signaturePart) {
    throw new Error('Invalid token format');
  }

  const header = JSON.parse(base64UrlDecode(headerPart).toString('utf-8')) as { alg?: string };
  if (header.alg !== jwtAlgorithm) {
    throw new Error('Unsupported JWT algorithm');
  }

  if (jwtAlgorithm !== 'HS256') {
    throw new Error('Only HS256 is supported');
  }

  const data = `${headerPart}.${payloadPart}`;
  const expectedSignature = createHmac('sha256', jwtSecret).update(data).digest();
  const actualSignature = base64UrlDecode(signaturePart);

  if (expectedSignature.length !== actualSignature.length || !timingSafeEqual(expectedSignature, actualSignature)) {
    throw new Error('Invalid token signature');
  }

  const payload = JSON.parse(base64UrlDecode(payloadPart).toString('utf-8')) as JwtPayload;
  if (payload.exp && Date.now() >= payload.exp * 1000) {
    throw new Error('Token expired');
  }

  return payload;
}

function isSafeStoragePath(path: string): boolean {
  return !path.startsWith('/') && !path.includes('..') && !path.includes('\\');
}

export async function DELETE(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader?.toLowerCase().startsWith('bearer ')) {
      return NextResponse.json(
        { success: false, error: 'Authentication required' },
        { status: 401 }
      );
    }

    let payload: JwtPayload;
    try {
      payload = parseJwt(authHeader.slice(7).trim());
    } catch (error) {
      console.error('Invalid token:', error);
      return NextResponse.json(
        { success: false, error: 'Invalid token' },
        { status: 401 }
      );
    }

    if (!payload.scopes?.includes('admin')) {
      return NextResponse.json(
        { success: false, error: 'Admin access required' },
        { status: 403 }
      );
    }

    const ownerId = payload.user_id || payload.sub;
    const { searchParams } = new URL(request.url);
    const fileName = searchParams.get('fileName');
    const filePath = searchParams.get('filePath');

    if (!fileName && !filePath) {
      return NextResponse.json({
        success: false,
        error: 'Thiếu thông tin fileName hoặc filePath'
      }, { status: 400 });
    }

    const targetPath = filePath || (ownerId ? `${ownerId}/${fileName}` : fileName!);

    if (!isSafeStoragePath(targetPath)) {
      return NextResponse.json({
        success: false,
        error: 'Đường dẫn file không hợp lệ'
      }, { status: 400 });
    }

    if (ownerId && !targetPath.startsWith(`${ownerId}/`)) {
      return NextResponse.json({
        success: false,
        error: 'Không có quyền xóa ngoài phạm vi owner'
      }, { status: 403 });
    }

    const supabaseKey = supabaseServiceKey || supabaseAnonKey;
    const supabase = createClient(supabaseUrl, supabaseKey);

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
