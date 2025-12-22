import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import duckdb from 'duckdb';
import { join } from 'path';
import { sort } from 'd3';

// Path to the DuckDB database file
const DB_PATH = join(process.cwd(), '..', 'backend', 'open_datle.db');

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
		console.log('DB_PATH:', DB_PATH);
		console.log('Requested dataset ID:', datasetId);

		const db = new duckdb.Database(DB_PATH);
		const connection = db.connect();

		// Get dataset metadata
		const metaResult = await new Promise((resolve, reject) => {
			connection.all(
				'SELECT dataset_id, title, x_axis_label, y_axis_label, type, source FROM datasets_meta WHERE dataset_id = ?',
				[datasetId],
				(err, rows) => {
					if (err) reject(err);
					else resolve(rows);
				}
			);
		});

		console.log('Meta result:', metaResult);

		if (!Array.isArray(metaResult) || metaResult.length === 0) {
			connection.close();
			db.close();
			return json({ error: 'Dataset not found' }, { status: 404 });
		}

		const dataset = metaResult[0] as {
			dataset_id: number;
			title: string;
			x_axis_label: string;
			y_axis_label: string;
			type: string;
			source: string;
		};

		// Get data points
		const dataResult = await new Promise((resolve, reject) => {
			connection.all(
				'SELECT x, y, sort_order FROM data WHERE dataset_id = ? ORDER BY sort_order',
				[datasetId],
				(err, rows) => {
					if (err) reject(err);
					else resolve(rows);
				}
			);
		});

		console.log('Data result:', dataResult);
		console.log('Data result length:', Array.isArray(dataResult) ? dataResult.length : 0);

		connection.close();
		db.close();

		const data = Array.isArray(dataResult)
			? (dataResult as Array<{ x: number; y: number; sort_order: number }>)
					.sort((a, b) => a.sort_order - b.sort_order)
					.map((point) => ({
						x: point.x,
						y: point.y,
						sort_order: point.sort_order
					}))
			: [];

		// Convert x values to borough names if type is "order"
		const processedData =
			dataset.type === 'order'
				? data.map((point) => ({
						x:
							point.x === 1
								? 'Brooklyn'
								: point.x === 2
									? 'The Bronx'
									: point.x === 3
										? 'Manhattan'
										: point.x === 4
											? 'Queens'
											: point.x === 5
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
			xAxisLabel: dataset.x_axis_label,
			yAxisLabel: dataset.y_axis_label,
			data: processedData,
			type: dataset.type,
			source: dataset.source
		});
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
