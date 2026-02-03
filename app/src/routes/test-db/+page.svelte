<script lang="ts">
	export let data;
</script>

<main>
	<h1>SvelteKit + Neon</h1>
	<p>Successfully connected to Postgres. Version: {data.version}</p>
	<br />
	<a href="/">← Back to Open Datle</a>
</main>

<style>
	main {
		max-width: 800px;
		margin: 2rem auto;
		padding: 2rem;
		text-align: center;
	}
	h1 {
		font-size: 2rem;
		margin-bottom: 1rem;
	}
	a {
		color: steelblue;
		text-decoration: none;
	}
	a:hover {
		text-decoration: underline;
	}
</style>
