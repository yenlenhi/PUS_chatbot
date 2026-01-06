import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const decodeTokenPayload = (token: string) => {
  const parts = token.split('.');
  if (parts.length !== 3) {
    return null;
  }

  try {
    const payload = Buffer.from(parts[1], 'base64url').toString('utf8');
    return JSON.parse(payload);
  } catch {
    return null;
  }
};

export async function GET() {
  const token = cookies().get('admin_token')?.value;

  if (!token) {
    return NextResponse.json(
      { detail: 'Chưa đăng nhập.' },
      { status: 401 }
    );
  }

  const payload = decodeTokenPayload(token);

  if (!payload) {
    return NextResponse.json(
      { detail: 'Token không hợp lệ.' },
      { status: 401 }
    );
  }

  const nowSeconds = Math.floor(Date.now() / 1000);
  const exp = payload.exp ? Number(payload.exp) : 0;

  if (!exp || exp <= nowSeconds) {
    return NextResponse.json(
      { detail: 'Token đã hết hạn.' },
      { status: 401 }
    );
  }

  const scopes = Array.isArray(payload.scopes) ? payload.scopes : [];

  if (!scopes.includes('admin')) {
    return NextResponse.json(
      { detail: 'Không đủ quyền truy cập.' },
      { status: 403 }
    );
  }

  return NextResponse.json({
    username: payload.sub,
    scopes,
    exp,
  });
}
