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
	<a href="/"><h1 class="title">Open Datle</h1></a>
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

	a {
		text-decoration: none;
	}

	nav {
		flex: 1;
		text-align: right;
	}

	nav a {
		color: black;
		text-decoration: none;
		font-weight: 500;
		transition: color 0.2s;
	}

	nav a:hover {
		text-decoration: underline;
	}

	@media (max-width: 768px) {
		header {
			flex-direction: column;
			padding: 0.5rem 1rem;
		}

		.date {
			text-align: center;
			margin-bottom: 0.5rem;
		}

		.title {
			margin: 0.5rem 0;
			font-size: 1.5rem;
		}

		nav {
			text-align: center;
			margin-top: 0.5rem;
		}
	}
</style>
