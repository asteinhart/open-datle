<script>
	import Header from '$lib/components/Header.svelte';
</script>

<Header />
<main>
	<div class="article">
		<div class="title-block">
			<div class="title">Exploring New York City Open Data</div>
			<div class="subtitle">
				Building a daily guessing game using real NYC data to learn more about the city.
			</div>
			<p class="byline">By <a href="austinsteinhart.com">Austin Steinhart</a> | March 2026</p>
			<hr class="divider" />
		</div>
		<div class="body">
			<p class="prose">
				From rat sightings, to park benches, to public restrooms, cities produce and publish troves of data that help quantify an urban environment. This data is used by activists to advocate for change, by entrepreneurs to develop products, by teachers to build analytics skills in the classroom, by government agencies to make data more accessible, and much more. 
			</p>
			<p class="prose">
				I recently moved back to NYC and I wanted to explore New York's city data as a way to reconnect and better understand the city I call home. Inspired by an old New York Times article format called <a href="https://www.nytimes.com/interactive/2015/05/28/upshot/you-draw-it-how-family-income-affects-childrens-college-chances.html" target="_blank" rel="noopener noreferrer">"You Draw It"</a>, I wanted to turn my exploration into a daily game to turn complicated, hard to access data into an entry point to be curious about New York City.
			</p>
		
			<div class="section">What is open data?</div>
			<p class="prose">
				Open data refers to data that is freely available for anyone to use, modify, and share. In
				the context of New York City, this means that various datasets collected by the city
				government are made accessible to the public.
			</p>
			<div class="section">NYC open data is both incredible and pretty bad</div>
			<p class="prose">
				TKTK - talk about the variety of datasets available, but also the challenges of working with
				them
			</p>

			<div class="section">Add your city's open data to Open Datle!</div>
			<p class="prose">
				TKTK - encourage people to submit datasets from their city, and talk about how I built the
				backend to be flexible and adaptable to different types of data
			</p>
			<div class="section">How does Open Datle work?</div>
			<p class="prose">TKTK</p>
			<div class="section">Play today's game!</div>
			<p class="prose">
				Or check out the sunset from my apartment last night with another app I built last summer: <a
					href="https://thesunset.austinsteinhart.com"
					class="link">Last Night's Sunset</a
				>
			</p>
		</div>
	</div>
</main>

<style>
	.article {
		width: clamp(300px, 60%, 800px);
		margin: auto;
	}
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
	.author-link {
		font-size: 1.2rem;
		color: #333;
		text-decoration: none;
	}
	.article {
		padding: 2rem 1rem;
	}

	a, .link {
		color: steelblue;
		text-decoration: none;
		font-weight: bold;
	}

	a:hover, .link:hover {
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
		font-size: 1rem;
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
		font-weight: 550;
		margin: auto;
		margin-block: 0.5rem;
	}

	.body {
		line-height: 1.6;
	}

	.prose {
		margin: auto;
		font-size: 1.15rem;
	}

	/* Responsive adjustments for smaller screens */
	@media (max-width: 768px) {
		.article {
			width: 90%;
			padding: 1rem;
		}
		.title {
			font-size: 1.8em;
		}
		.subtitle {
			font-size: 1rem;
		}
		.prose {
			font-size: 1rem;
		}
	}
</style>
