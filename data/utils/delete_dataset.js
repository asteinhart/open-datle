import { readdir } from 'fs/promises';
import { join } from 'path';

const API_URL = 'http://localhost:5173/api/v1/dataset';

async function deleteDataset(datasetId) {
	try {
		console.log(`\nDeleting dataset with ID: ${datasetId}...`);

		const response = await fetch(`${API_URL}?id=${datasetId}`, {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		const result = await response.json();

		if (response.ok) {
			console.log('✅ Dataset deleted successfully');
			console.log(`Dataset ID: ${result.dataset_id}`);
			return true;
		} else {
			console.error('❌ Failed to delete dataset');
			console.error('Error:', result.error);
			return false;
		}
	} catch (error) {
		console.error('❌ Error deleting dataset:', error.message);
		return false;
	}
}

// Get dataset ID from command line argument
const datasetId = process.argv[2];

if (!datasetId) {
	console.error('Usage: node delete_dataset.js <dataset_id>');
	console.error('Example: node delete_dataset.js 3');
	process.exit(1);
}

if (isNaN(parseInt(datasetId))) {
	console.error('Error: Dataset ID must be a number');
	process.exit(1);
}

// Execute deletion
deleteDataset(parseInt(datasetId)).then((success) => {
	process.exit(success ? 0 : 1);
});
