import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { sql } from '$lib/server/db';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();
		const { user_id, dataset_id, score } = body;

		// Validate required fields
		if (!user_id || !dataset_id || score === undefined || score === null) {
			return json({ error: 'user_id, dataset_id, and score are required' }, { status: 400 });
		}

		// Validate score is a number
		if (typeof score !== 'number' || score < 0) {
			return json({ error: 'score must be a non-negative number' }, { status: 400 });
		}

		// Insert or update user score using PostgreSQL's ON CONFLICT
		const result = await sql`
			INSERT INTO user_scores (user_id, dataset_id, score_date, score)
			VALUES (${user_id}, ${dataset_id}, CURRENT_DATE, ${score})
			ON CONFLICT (user_id, dataset_id, score_date)
			DO UPDATE SET 
				score = GREATEST(user_scores.score, ${score}),
				created_at = CURRENT_TIMESTAMP
			RETURNING score_id, score
		`;

		return json(
			{
				success: true,
				message: 'Score saved successfully',
				score_id: result[0].score_id,
				score: result[0].score
			},
			{ status: 201 }
		);
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
