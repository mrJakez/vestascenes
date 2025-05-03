// app/frontend-api/config/route.js

export async function GET() {
  const apiUrl = process.env.API_URL || process.env.FALLBACK_BACKEND_URL;

  return Response.json({
    apiUrl,
  });
}