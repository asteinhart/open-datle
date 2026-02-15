<script lang="ts">
	import '../global.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
	<title>Open Datle - Daily Open Data Guessing Game</title>

	<!-- Meta Tags -->
	<meta
		name="description"
		content="Test your knowledge of New York City! Guess the trends in crime, housing, transportation, and more. A new challenge every day using real New York City data."
	/>
	<meta
		name="keywords"
		content="New York City data game, data visualization, guessing game, New York City, open data, statistics game, daily puzzle"
	/>
	<meta name="author" content="Austin Steinhart" />

	<!-- Open Graph / Facebook -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://open-datle.com/" />
	<meta property="og:title" content="Open Datle - Daily Open Data Guessing Game" />
	<meta
		property="og:description"
		content="Test your knowledge of New York City! Guess the trends in crime, housing, transportation, and more. A new challenge every day using real New York City data."
	/>
	<meta property="og:image" content="https://open-datle.com/favicon.svg" />

	<!-- Twitter -->
	<meta property="twitter:card" content="summary_large_image" />
	<meta property="twitter:url" content="https://open-datle.com/" />
	<meta property="twitter:title" content="Open Datle - Daily Open Data Guessing Game" />
	<meta
		property="twitter:description"
		content="Test your knowledge of New York City! Guess the trends in crime, housing, transportation, and more. A new challenge every day using real New York City data."
	/>
	<meta property="twitter:image" content="https://open-datle.com/favicon.svg" />

	<!-- Viewport -->
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />

	<!-- Robots -->
	<meta name="robots" content="index, follow" />
</svelte:head>

{@render children()}
