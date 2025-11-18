import type { DataSet } from './types/DataSet';

function findID(): Number {
	// Dummy implementation - replace with actual logic
	return 1;
}

const DATA = [
	{ x: 2017, y: 22522 },
	{ x: 2018, y: 21830 },
	{ x: 2019, y: 18715 },
	{ x: 2020, y: 3422 },
	{ x: 2021, y: 268 },
	{ x: 2022, y: 5067 },
	{ x: 2023, y: 13447 },
	{ x: 2024, y: 16812 },
	{ x: 2025, y: 16752 }
];

function returnFakeData(): DataSet {
	return {
		id: '1',
		name: 'Evictions',
		xAxisLabel: 'Year',
		yAxisLabel: 'Number of Evictions',
		data: DATA
	};
}

export { findID, returnFakeData };
