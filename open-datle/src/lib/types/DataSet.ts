interface DataSet {
    id: string;
    name: string;
    xAxisLabel: string;
    yAxisLabel: string;
    data: Array<{[key: string]: number}>;
}


export type { DataSet };