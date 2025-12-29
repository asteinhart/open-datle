interface DataSet {
	dataset_id: number;
	title: string;
	subtitle: string | null;
	city: string;
	yMin: number | null;
	yMax: number | null;
	data: Array<{
		x: number | string;
		y: number;
		sort_order: number;
	}>;
	type: string;
	source: string;
}

export type { DataSet };
