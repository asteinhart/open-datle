<script>
	import Header from '$lib/components/Header.svelte';
</script>

<Header />
<main>
	<div class="article">
		<div class="title-block">
			<div class="title">Exploring New York City Open Data</div>
			<div class="subtitle">
				Building a daily guessing game using real NYC data to test your knowledge of the city.
			</div>
			<p class="byline">By <a href="austinsteinhart.com">Austin Steinhart</a> | Early 2026</p>
			<hr class="divider" />
		</div>
		<div class="body">
			<div class="prose">
				<p>
					TKTKT
				</p>
				</div>
		</div>
	</div>
</main>

<style>
	p {
		font-family: 'Hanken Grotesk', sans-serif;
		padding-block: 0.5rem;
	}

	.aside {
		font-style: italic;
		color: #555;
		margin-left: 1rem;
		font-size: small;
	}
	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1rem;
		border-bottom: 1px solid #ddd;
		font-weight: bold;
	}
	.author-link {
		font-size: 1.2rem;
		color: #333;
		text-decoration: none;
	}
	.article {
		padding: 2rem 1rem;
	}
	.title-block {
		width: 50%;
		margin: auto;
	}

	.link {
		color: #fba58b;
		text-decoration: none;
		font-weight: bold;
	}

	.link:hover {
		text-decoration: underline;
	}
	.title {
		font-size: 2.5rem;
		font-weight: bold;
		text-align: left;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		font-size: 1.3rem;
		text-align: left;
		margin-bottom: 0.5rem;
	}

	.byline {
		font-size: 0.9rem;
		margin: auto;
		color: #666;
	}

	.divider {
		margin-bottom: 0.5rem;
	}

	.byline a {
		color: #666;
		text-decoration: none;
	}
	.byline a:hover {
		text-decoration: underline;
	}

	
	.section {
		font-family: 'Hanken Grotesk', sans-serif;
		font-size: 1.5rem;
		font-weight: bold;
		margin: auto;
		margin-top: 1.5rem;
		margin-bottom: 0.5rem;
		width: 50%;
	}

	.subsection {
		font-family: 'Hanken Grotesk', sans-serif;
		font-size: 1.2rem;
		font-weight: bold;
		margin: auto;
		margin-top: 1rem;
		margin-bottom: 0.2rem;
		width: 50%;
	}

	
	.body {
		line-height: 1.6;
	}

	.prose {
		width: 50%;
		margin: auto;
	}


	/* Responsive adjustments for smaller screens */
	@media (max-width: 768px) {
		.title-block {
			width: 90%;
		}
		.title {
			font-size: 1.8em;
		}
		.subtitle {
			font-size: 1rem;
			width: 100%;
		}
		.section,
		.subsection,
		.prose {
			width: 95%;
		}
		
	}
</style>
