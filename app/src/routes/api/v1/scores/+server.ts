import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { sql } from '$lib/server/db';

export const GET: RequestHandler = async ({ url }) => {
	try {
		const datasetId = url.searchParams.get('dataset_id');
		const userId = url.searchParams.get('user_id');

		if (!datasetId) {
			return json({ error: 'dataset_id parameter is required' }, { status: 400 });
		}

		// Get all scores for this dataset from today
		const scores = await sql`
			SELECT score, COUNT(*) as count
			FROM user_scores
			WHERE dataset_id = ${datasetId}
				AND score_date = CURRENT_DATE
			GROUP BY score
			ORDER BY score ASC
		`;

		let userScore = null;
		if (userId) {
			// Get user's score for this dataset
			const userScoreResult = await sql`
				SELECT score
				FROM user_scores
				WHERE user_id = ${userId}
					AND dataset_id = ${datasetId}
					AND score_date = CURRENT_DATE
				ORDER BY created_at DESC
				LIMIT 1
			`;
			if (userScoreResult.length > 0) {
				userScore = Number(userScoreResult[0].score);
			}
		}

		return json({
			scores: scores.map(row => ({
				score: Number(row.score),
				count: Number(row.count)
			})),
			userScore
		});
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};