<script>
	let isMobile = false;
	let currentDate = $state('');
	if (typeof window !== 'undefined') {
		isMobile = window.innerWidth <= 768;
	}
	if (isMobile) {
		currentDate = new Date().toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	} else {
		currentDate = new Date().toLocaleDateString('en-US', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}



</script>

<header>
	<div class="date">{currentDate}</div>
	<a href="/" class="logo-link">
		<div class="title-container">
			<div class="title-box">
				<svg
					class="logo"
					width="40"
					height="40"
					viewBox="0 0 40 40"
					xmlns="http://www.w3.org/2000/svg"
				>
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
			</div>
		</div>
	</a>
	<div class="spacer"></div>
	<a href="/about" class="about-link">About</a>
</header>

<style>
	header {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: .7rem 1rem;
		background-color: #f5f5f5;
		border-bottom: 2px solid #ddd;
	}

	.date {
		flex: 1;
		text-align: left;
		font-size: 0.9rem;
		color: #666;
	}

	.spacer {
		display: none;
	}

	.about-link {
		flex: 1;
		text-align: right;
		font-size: 1rem;
		color: #666;
		text-decoration: none;
		border-radius: 4px;
		transition: background-color 0.2s;
	}

	

	.logo-link {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		text-decoration: none;
	}

	.title-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
	}

	.title-box {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}
	.logo {
		width: 40px;
		height: 40px;
		flex-shrink: 0;
		margin-right: -0.6rem;
		margin-bottom: 0.2rem;
	}

	.title {
		margin: 0;
		font-size: 1.8rem;
		font-weight: bold;
		color: #000;
		white-space: nowrap;
	}


	@media (max-width: 500px) {
		header {
			gap: 0.5rem;
			padding: 0.5rem;
		}

		.spacer {
			display: none;
		}

		.logo {
			width: 30px;
			height: 30px;
			margin-right: -0.5rem;
		}

		.title {
			font-size: 1.2rem;
		}

		.about-link {
			
			font-size: 0.8rem;
		}
	}
</style>
