<script>
	let currentDate = $state(
		new Date().toLocaleDateString('en-US', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		})
	);
</script>

<header>
	<div class="date">{currentDate}</div>
	<h1 class="title">Open Datle</h1>
	<nav>
		<a href="/about">About</a>
	</nav>
</header>

<style>
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem 2rem;
		background-color: #f5f5f5;
		border-bottom: 2px solid #ddd;
	}

	.date {
		flex: 1;
		font-size: 0.9rem;
		color: #666;
	}

	.title {
		flex: 1;
		text-align: center;
		margin: 0;
		font-size: 1.8rem;
		font-weight: bold;
		color: #333;
	}

	nav {
		flex: 1;
		text-align: right;
	}

	nav a {
		text-decoration: none;
		color: #0066cc;
		font-weight: 500;
		transition: color 0.2s;
	}

	nav a:hover {
		color: #004499;
		text-decoration: underline;
	}
</style>
