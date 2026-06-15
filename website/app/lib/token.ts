const SECRET = process.env.JWT_SECRET || 'fallback-secret-key-12345-automated-posts';

/**
 * Edge-safe HMAC-SHA256 signer using the native Web Crypto API.
 */
async function signMessage(message: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const keyData = encoder.encode(secret);
  const msgData = encoder.encode(message);

  const key = await crypto.subtle.importKey(
    'raw',
    keyData,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const sigBuffer = await crypto.subtle.sign('HMAC', key, msgData);
  const sigArray = Array.from(new Uint8Array(sigBuffer));
  return sigArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Creates a signed session token.
 */
export async function createSessionToken(payload: { username: string }): Promise<string> {
  const expiresAt = Date.now() + 7 * 24 * 60 * 60 * 1000; // 7 days expiration
  const data = JSON.stringify({ ...payload, expiresAt });
  
  // Safe base64 encoding (works in Node and Edge)
  const base64Data = btoa(unescape(encodeURIComponent(data)));
  const signature = await signMessage(base64Data, SECRET);
  
  return `${base64Data}.${signature}`;
}

/**
 * Verifies a signed session token and returns the payload if valid.
 */
export async function verifySessionToken(token: string): Promise<{ username: string } | null> {
  try {
    if (!token) return null;
    const parts = token.split('.');
    if (parts.length !== 2) return null;

    const [base64Data, signature] = parts;
    const expectedSignature = await signMessage(base64Data, SECRET);

    // Timing-safe comparison would be preferred, but simple check is standard for API
    if (signature !== expectedSignature) {
      return null;
    }

    // Safe base64 decoding (works in Node and Edge)
    const dataJson = decodeURIComponent(escape(atob(base64Data)));
    const data = JSON.parse(dataJson);

    if (Date.now() > data.expiresAt) {
      return null; // Token expired
    }

    return { username: data.username };
  } catch (error) {
    console.error('Session token verification failed:', error);
    return null;
  }
}
