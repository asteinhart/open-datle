# open-datle

[open-datle](open-datle.com) is a daily data game focused on city open data.
Players explore charts, compare trends, and make guesses based on real NYC datasets.

The repository includes two main parts:
- A web app for gameplay and visualization.
- A data pipeline for collecting, transforming, and publishing datasets.

## Why this project

- Make public data easier and more fun to understand.
- Turn raw city datasets into simple, interactive challenges.
- Keep the project easy to extend with new datasets.

## Tech used

### Frontend and app

- SvelteKit
- Svelte
- TypeScript
- Vite
- D3

### Data and backend tooling

- Python
- Polars
- SODA API via sodapy
- DuckDB
- Neon/Postgres tooling

## Project structure

- app/: SvelteKit app, API routes, UI components, and charts.
- data/: dataset creation scripts and prepared output JSON.
- database/: migration, import/export, and seed scripts.

## Contributing

Contributions are welcome.

- Open an issue for bugs, ideas, or dataset suggestions.
- Keep changes focused and include clear commit messages.
- For new datasets, follow the existing script style in data/create_data.

## License

This project is licensed under the terms in the LICENSE file.
