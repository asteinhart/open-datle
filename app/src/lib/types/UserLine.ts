export interface UserPoint {
	x: number | Date;
	y: number;
}

export interface UserLine {
	points: UserPoint[];
}
