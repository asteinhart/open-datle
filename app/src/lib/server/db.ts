import { neon } from '@neondatabase/serverless';
import { DATABASE_URL } from '$env/static/private';
import ws from 'ws';

// Configure WebSocket for Node.js environment (development)
if (typeof WebSocket === 'undefined') {
	(global as any).WebSocket = ws;
}

export const sql = neon(DATABASE_URL, {
	fetchOptions: {
		cache: 'no-store'
	}
});
