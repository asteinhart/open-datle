import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { DuckDBInstance, INTEGER, VARCHAR, DOUBLE } from '@duckdb/node-api';
import { join } from 'path';

// Path to the DuckDB database file
const DB_PATH = join(process.cwd(), '..', 'database', 'open_datle.db');

export const GET: RequestHandler = async ({ url }) => {
	const id = url.searchParams.get('id');

	if (!id) {
		return json({ error: 'ID parameter is required' }, { status: 400 });
	}

	const datasetId = parseInt(id);
	if (isNaN(datasetId)) {
		return json({ error: 'ID must be a number' }, { status: 400 });
	}

	let instance;
	let connection;

	try {
		console.log('DB_PATH:', DB_PATH);
		console.log('Requested dataset ID:', datasetId);

		instance = await DuckDBInstance.create(DB_PATH);
		connection = await instance.connect();

		// Get dataset metadata
		const metaStmt = await connection.prepare(
			'SELECT dataset_id, title, type, city, subtitle, y_min, y_max, source, note FROM datasets_meta WHERE dataset_id = $datasetId'
		);
		metaStmt.bind({ datasetId }, { datasetId: INTEGER });
		const metaResult = await metaStmt.run();
		const metaRows = await metaResult.getRowObjectsJson();

		console.log('Meta result:', metaRows);

		if (!metaRows || metaRows.length === 0) {
			return json({ error: 'Dataset not found' }, { status: 404 });
		}

		const dataset = metaRows[0] as {
			dataset_id: number;
			title: string;
			type: string;
			city: string;
			subtitle: string | null;
			y_min: number | null;
			y_max: number | null;
			source: string;
			note: string | null;
		};

		// Get data points
		const dataStmt = await connection.prepare(
			'SELECT x, y, sort_order FROM data WHERE dataset_id = $datasetId ORDER BY sort_order'
		);
		dataStmt.bind({ datasetId }, { datasetId: INTEGER });
		const dataResult = await dataStmt.run();
		const dataRows = await dataResult.getRowObjectsJson();

		console.log('Data result:', dataRows);
		console.log('Data result length:', dataRows ? dataRows.length : 0);

		const data = dataRows
			? dataRows
					.map((row) => row as { x: number; y: number; sort_order: number })
					.sort((a, b) => a.sort_order - b.sort_order)
			: [];

		// Process data for borough mapping if type is "order"
		const processedData =
			dataset.type === 'order'
				? data.map((point) => ({
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
	} finally {
		if (connection) connection.closeSync();
		if (instance) instance.closeSync();
	}
};

export const POST: RequestHandler = async ({ request }) => {
	let instance;
	let connection;

	try {
		const body = await request.json();

		if (!body.title || !body.type || !body.city || !body.data || !Array.isArray(body.data)) {
			return json({ error: 'Title, type, city, and data array are required' }, { status: 400 });
		}

		console.log('body:', body);
		console.log('body.title', body.title);

		instance = await DuckDBInstance.create(DB_PATH);
		connection = await instance.connect();

		// Check if dataset with same title exists
		const existingStmt = await connection.prepare(
			'SELECT dataset_id FROM datasets_meta WHERE title = $title'
		);
		existingStmt.bind({ title: body.title }, { title: VARCHAR });
		const existingResult = await existingStmt.run();
		const existingRows = await existingResult.getRows();

		if (existingRows && existingRows.length > 0) {
			return json({ error: 'A dataset with this title already exists' }, { status: 409 });
		}

		// Get the next dataset_id
		const maxIdStmt = await connection.prepare(
			'SELECT MAX(dataset_id) as max_id FROM datasets_meta'
		);
		const maxIdResult = await maxIdStmt.run();
		const maxIdRows = await maxIdResult.getRowObjectsJson();

		const nextId =
			maxIdRows && maxIdRows.length > 0 && maxIdRows[0].max_id
				? Number(maxIdRows[0].max_id) + 1
				: 1;

		// Insert dataset metadata
		const insertMetaStmt = await connection.prepare(
			'INSERT INTO datasets_meta (dataset_id, title, type, city, subtitle, y_min, y_max, source, note) VALUES ($datasetId, $title, $type, $city, $subtitle, $yMin, $yMax, $source, $note)'
		);
		insertMetaStmt.bind(
			{
				datasetId: nextId,
				title: body.title,
				type: body.type,
				city: body.city,
				subtitle: body.subtitle || null,
				yMin: body.y_min || null,
				yMax: body.y_max || null,
				source: body.source || null,
				note: body.note || null
			},
			{
				datasetId: INTEGER,
				title: VARCHAR,
				type: VARCHAR,
				city: VARCHAR,
				subtitle: VARCHAR,
				yMin: DOUBLE,
				yMax: DOUBLE,
				source: VARCHAR,
				note: VARCHAR
			}
		);
		await insertMetaStmt.run();

		// Get the next data_id
		const maxDataIdStmt = await connection.prepare('SELECT MAX(data_id) as max_id FROM data');
		const maxDataIdResult = await maxDataIdStmt.run();
		const maxDataIdRows = await maxDataIdResult.getRowObjectsJson();

		let nextDataId =
			maxDataIdRows && maxDataIdRows.length > 0 && maxDataIdRows[0].max_id
				? Number(maxDataIdRows[0].max_id) + 1
				: 1;

		// Insert data points
		const insertDataStmt = await connection.prepare(
			'INSERT INTO data (data_id, dataset_id, x, y, sort_order) VALUES ($dataId, $datasetId, $x, $y, $sortOrder)'
		);

		for (let i = 0; i < body.data.length; i++) {
			const point = body.data[i];
			insertDataStmt.bind(
				{
					dataId: nextDataId++,
					datasetId: nextId,
					x: point.x,
					y: point.y,
					sortOrder: point.sort_order || i + 1
				},
				{
					dataId: INTEGER,
					datasetId: INTEGER,
					x: DOUBLE,
					y: DOUBLE,
					sortOrder: INTEGER
				}
			);
			await insertDataStmt.run();
		}

		return json({ success: true, dataset_id: nextId }, { status: 201 });
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	} finally {
		if (connection) connection.closeSync();
		if (instance) instance.closeSync();
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

	let instance;
	let connection;

	try {
		instance = await DuckDBInstance.create(DB_PATH);
		connection = await instance.connect();

		// Check if dataset exists
		const checkStmt = await connection.prepare(
			'SELECT dataset_id FROM datasets_meta WHERE dataset_id = $datasetId'
		);
		checkStmt.bind({ datasetId }, { datasetId: INTEGER });
		const checkResult = await checkStmt.run();
		const checkRows = await checkResult.getRows();

		if (!checkRows || checkRows.length === 0) {
			return json({ error: 'Dataset not found' }, { status: 404 });
		}

		// Delete data points
		const deleteDataStmt = await connection.prepare(
			'DELETE FROM data WHERE dataset_id = $datasetId'
		);
		deleteDataStmt.bind({ datasetId }, { datasetId: INTEGER });
		await deleteDataStmt.run();

		// Delete dataset metadata
		const deleteMetaStmt = await connection.prepare(
			'DELETE FROM datasets_meta WHERE dataset_id = $datasetId'
		);
		deleteMetaStmt.bind({ datasetId }, { datasetId: INTEGER });
		await deleteMetaStmt.run();

		return json({ success: true, dataset_id: datasetId }, { status: 200 });
	} catch (error) {
		console.error('Database error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	} finally {
		if (connection) connection.closeSync();
		if (instance) instance.closeSync();
	}
};
