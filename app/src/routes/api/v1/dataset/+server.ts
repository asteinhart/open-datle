import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { sql } from '$lib/server/db';

export const GET: RequestHandler = async ({ url }) => {
	const id = url.searchParams.get('id');

	if (!id) {
		return json({ error: 'ID parameter is required' }, { status: 400 });
	}

	const datasetId = parseInt(id);
	if (isNaN(datasetId)) {
		return json({ error: 'ID must be a number' }, { status: 400 });
	}

	try {
		console.log('Requested dataset ID:', datasetId);

		// Get dataset metadata
		const metaResult = await sql`
			SELECT dataset_id, title, type, city, subtitle, y_min, y_max, source, note 
			FROM datasets_meta 
			WHERE dataset_id = ${datasetId}
		`;

		console.log('Meta result:', metaResult);

		if (!metaResult || metaResult.length === 0) {
			return json({ error: 'Dataset not found' }, { status: 404 });
		}

		const dataset = metaResult[0];

		// Get data points
		const dataResult = await sql`
			SELECT x, y, sort_order 
			FROM data 
			WHERE dataset_id = ${datasetId} 
			ORDER BY sort_order
		`;

		console.log('Data result:', dataResult);
		console.log('Data result length:', dataResult ? dataResult.length : 0);

		const data = dataResult || [];

		// Process data for borough mapping if type is "order"
		const processedData =
			dataset.type === 'order'
				? data.map((point: any) => ({
						x:
							Number(point.x) === 1
								? 'Manhattan'
								: Number(point.x) === 2
									? 'Brooklyn'
									: Number(point.x) === 3
										? 'Queens'
										: Number(point.x) === 4
											? 'The Bronx'
											: Number(point.x) === 5
												? 'Staten Island'
												: point.x,
						y: point.y,
						sort_order: point.sort_order
					}))
				: data;

		console.log('Final response data:', { dataset_id: dataset.dataset_id, data: processedData });

		return json({
			dataset_id: dataset.dataset_id,
			title: dataset.title,
			city: dataset.city,
			subtitle: dataset.subtitle,
			yMin: dataset.y_min,
			yMax: dataset.y_max,
			data: processedData,
			type: dataset.type,
			source: dataset.source,
			note: dataset.note
		});
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();

		if (!body.title || !body.type || !body.city || !body.data || !Array.isArray(body.data)) {
			return json({ error: 'Title, type, city, and data array are required' }, { status: 400 });
		}

		console.log('body:', body);

		// Check if dataset with same title exists
		const existing = await sql`
			SELECT dataset_id FROM datasets_meta WHERE title = ${body.title}
		`;

		if (existing && existing.length > 0) {
			return json({ error: 'A dataset with this title already exists' }, { status: 409 });
		}

		// Insert dataset metadata (SERIAL will auto-increment)
		const insertedDataset = await sql`
			INSERT INTO datasets_meta (title, type, city, subtitle, y_min, y_max, source, note)
			VALUES (
				${body.title},
				${body.type},
				${body.city},
				${body.subtitle || null},
				${body.y_min ?? null},
				${body.y_max ?? null},
				${body.source || null},
				${body.note || null}
			)
			RETURNING dataset_id
		`;

		const datasetId = insertedDataset[0].dataset_id;

		// Insert data points
		for (let i = 0; i < body.data.length; i++) {
			const point = body.data[i];
			await sql`
				INSERT INTO data (dataset_id, x, y, sort_order)
				VALUES (
					${datasetId},
					${point.x},
					${point.y},
					${point.sort_order || i + 1}
				)
			`;
		}

		return json({ success: true, dataset_id: datasetId }, { status: 201 });
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};

export const DELETE: RequestHandler = async ({ url }) => {
	const id = url.searchParams.get('id');

	if (!id) {
		return json({ error: 'ID parameter is required' }, { status: 400 });
	}

	const datasetId = parseInt(id);
	if (isNaN(datasetId)) {
		return json({ error: 'ID must be a number' }, { status: 400 });
	}

	try {
		// Check if dataset exists
		const dataset = await sql`
			SELECT dataset_id FROM datasets_meta WHERE dataset_id = ${datasetId}
		`;

		if (!dataset || dataset.length === 0) {
			return json({ error: 'Dataset not found' }, { status: 404 });
		}

		// Delete data points (CASCADE will handle this, but explicit is fine)
		await sql`DELETE FROM data WHERE dataset_id = ${datasetId}`;

		// Delete dataset metadata
		await sql`DELETE FROM datasets_meta WHERE dataset_id = ${datasetId}`;

		return json({ success: true, dataset_id: datasetId }, { status: 200 });
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
