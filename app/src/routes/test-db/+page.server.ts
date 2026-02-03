import { sql } from '$lib/server/db';

export async function load() {
	const response = await sql`SELECT version()`;
	return {
		version: response[0].version as string
	};
}
