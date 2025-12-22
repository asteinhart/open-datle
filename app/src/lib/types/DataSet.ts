interface DataSet {
	dataset_id: number;
	title: string;
	xAxisLabel: string;
	yAxisLabel: string;
	data: Array<{
		x: number | string;
		y: number;
		sort_order: number;
	}>;
	type: string;
	source: string;
}

export type { DataSet };
