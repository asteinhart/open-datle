import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import db from '$lib/db';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();
		const { user_id, dataset_id, user_order } = body;

		// Validate required fields
		if (!user_id || !dataset_id || !user_order) {
			return json({ error: 'user_id, dataset_id, and user_order are required' }, { status: 400 });
		}

		// Validate user_order is an array
		if (!Array.isArray(user_order)) {
			return json({ error: 'user_order must be an array' }, { status: 400 });
		}

		// Note: You may want to create a separate table for order type guesses
		// For now, using the same user_data_line table with user_line field
		const [result] = await db.query(
			`INSERT INTO user_data_line (user_id, dataset_id, user_line) 
			 VALUES (?, ?, ?) 
			 ON DUPLICATE KEY UPDATE user_line = ?, submitted_at = CURRENT_TIMESTAMP`,
			[user_id, dataset_id, JSON.stringify(user_order), JSON.stringify(user_order)]
		);

		return json(
			{
				success: true,
				message: 'Order guess submitted successfully',
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
