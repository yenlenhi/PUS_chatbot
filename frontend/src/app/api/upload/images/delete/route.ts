import { NextResponse } from 'next/server';

export async function DELETE() {
  return NextResponse.json(
    {
      success: false,
      error: 'Tinh nang xoa anh da tam khoa tren moi truong nay.',
    },
    { status: 403 }
  );
}
