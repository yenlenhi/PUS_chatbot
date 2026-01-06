import { NextRequest, NextResponse } from 'next/server';

const DEFAULT_TOKEN_TTL_SECONDS = 30 * 60; // 30 minutes

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

export async function POST(request: NextRequest) {
  try {
    const { username, password, rememberMe } = await request.json();

    if (!username || !password) {
      return NextResponse.json(
        { detail: 'Thiếu tên đăng nhập hoặc mật khẩu.' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const response = await fetch(`${backendUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      let detail = 'Đăng nhập thất bại.';
      try {
        const errorData = await response.json();
        detail = errorData.detail || detail;
      } catch {
        // Ignore JSON parse error
      }

      return NextResponse.json({ detail }, { status: response.status });
    }

    const data = await response.json();
    const token = data.access_token as string | undefined;

    if (!token) {
      return NextResponse.json(
        { detail: 'Không nhận được token từ server.' },
        { status: 500 }
      );
    }

    const payload = decodeTokenPayload(token);
    const nowSeconds = Math.floor(Date.now() / 1000);
    const exp = payload?.exp ? Number(payload.exp) : nowSeconds + DEFAULT_TOKEN_TTL_SECONDS;
    const maxAge = Math.max(exp - nowSeconds, 0);

    const responseBody = NextResponse.json({ ok: true });

    responseBody.cookies.set({
      name: 'admin_token',
      value: token,
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/',
      ...(rememberMe ? { maxAge } : {}),
    });

    return responseBody;
  } catch (error) {
    console.error('Login API error:', error);
    return NextResponse.json(
      { detail: 'Đã xảy ra lỗi khi đăng nhập.' },
      { status: 500 }
    );
  }
}
