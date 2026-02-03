import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { sql } from '$lib/server/db';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();
		const { user_id, dataset_id, user_line } = body;

		// Validate required fields
		if (!user_id || !dataset_id || !user_line) {
			return json({ error: 'user_id, dataset_id, and user_line are required' }, { status: 400 });
		}

		// Validate user_line is an array
		if (!Array.isArray(user_line)) {
			return json({ error: 'user_line must be an array' }, { status: 400 });
		}

		// Insert or update user guess using PostgreSQL's ON CONFLICT
		await sql`
			INSERT INTO user_guesses (user_id, dataset_id, guess_data, guess_type)
			VALUES (${user_id}, ${dataset_id}, ${JSON.stringify(user_line)}, 'line')
			ON CONFLICT (user_id, dataset_id)
			DO UPDATE SET 
				guess_data = ${JSON.stringify(user_line)},
				submitted_at = CURRENT_TIMESTAMP
		`;

		return json(
			{
				success: true,
				message: 'Guess submitted successfully',
				user_id,
				dataset_id
			},
			{ status: 201 }
		);
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
