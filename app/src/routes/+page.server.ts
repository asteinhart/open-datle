import { sql } from '$lib/server/db';
import type { RequestEvent } from '@sveltejs/kit';

function generateCookieId(): string {
	return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
}

export async function load({ cookies }: RequestEvent) {
	// Get or create user_id cookie
	let userId: string = cookies.get('user_id') || '';

	if (!userId) {
		// Generate a unique cookie identifier
		const cookieId = generateCookieId();

		// Create a new user in the database
		const result = await sql`
			INSERT INTO users (cookie, created_at)
			VALUES (${cookieId}, CURRENT_TIMESTAMP)
			RETURNING user_id
		`;

		userId = result[0].user_id.toString();

		// Set cookie for 1 year
		cookies.set('user_id', userId, {
			path: '/',
			maxAge: 60 * 60 * 24 * 365,
			httpOnly: true,
			sameSite: 'lax'
		});
	}

	// Get today's date in YYYY-MM-DD format
	const today = new Date().toISOString().split('T')[0];

	// Query schedule table for today's dataset
	const scheduleResult = await sql`
		SELECT dataset_id, day 
		FROM schedule 
		WHERE day = ${today}
	`;

	return {
		userId: parseInt(userId, 10),
		todayDatasetId: scheduleResult.length > 0 ? scheduleResult[0].dataset_id : null,
		today: today
	};
}
