import { sql } from '$lib/server/db';

export async function load() {
	// Get today's date in YYYY-MM-DD format
	const today = new Date().toISOString().split('T')[0];

	// Query schedule table for today's dataset
	const result = await sql`
		SELECT dataset_id, day 
		FROM schedule 
		WHERE day = ${today}
	`;

	return {
		todayDatasetId: result.length > 0 ? result[0].dataset_id : null,
		today: today
	};
}
