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
	<a href="/" class="logo-link">
		<svg class="logo" width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
			<!-- Outer O circle -->
			<ellipse cx="20" cy="20" rx="11" ry="12" fill="none" stroke="#000" stroke-width="3.5" />

			<!-- 8 evenly spaced spokes around the ellipse -->
			<line x1="20" y1="20" x2="20" y2="8" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="28.78" y2="10.56" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="31" y2="20" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="28.78" y2="29.44" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="20" y2="32" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="11.22" y2="29.44" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="9" y2="20" stroke="#000" stroke-width="2" />
			<line x1="20" y1="20" x2="11.22" y2="10.56" stroke="#000" stroke-width="2" />
		</svg>
		<h1 class="title">pen Datle</h1>
	</a>
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

	.logo-link {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;

		text-decoration: none;
	}

	.logo {
		flex-shrink: 0;
		margin-right: -0.3rem;
		margin-bottom: 0.35rem;
	}

	.title {
		text-align: center;
		margin: 0;
		font-size: 1.8rem;
		font-weight: bold;
		color: #000;
	}

	a {
		text-decoration: none;
	}

	nav {
		flex: 1;
		text-align: right;
	}

	nav a {
		color: #000;
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
			padding: 0.5rem 0.5rem;
		}

		.date {
			order: 3;
			text-align: center;
			margin-top: 0.2rem;
		}

		.logo-link {
			order: 1;
			margin: 0.2rem 0;
		}

		.logo {
			width: 32px;
			height: 32px;
		}

		.title {
			font-size: 1.5rem;
		}

		nav {
			order: 2;
			text-align: center;
			margin: 0.1rem 0;
		}
	}
</style>
