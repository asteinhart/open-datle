<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	let {
		datasetId,
		userId,
		gameType
	} = $props<{
		datasetId: number;
		userId: number;
		gameType: 'line' | 'order';
	}>();

	let svg = $state<any>();
	let scores: Array<{ score: number; count: number }> = $state([]);
	let userScore: number | null = $state(null);
	let loading = $state(true);
	let error = $state('');

	// Responsive container
	let containerWidth = $state(600);
	const margin = { top: 20, right: 20, bottom: 50, left: 50 };
	const height = 300;

	// Update width on mount and resize
	onMount(() => {
		const updateWidth = () => {
			if (svg) {
				const container = svg.parentElement;
				if (container) {
					containerWidth = container.clientWidth;
				}
			}
		};

		updateWidth();
		window.addEventListener('resize', updateWidth);

		// Fetch scores
		fetchScores();

		return () => {
			window.removeEventListener('resize', updateWidth);
		};
	});

	async function fetchScores() {
		try {
			const response = await fetch(`/api/v1/scores?dataset_id=${datasetId}&user_id=${userId}`);
			if (!response.ok) {
				throw new Error('Failed to fetch scores');
			}
			const data = await response.json();
			scores = data.scores;
			userScore = data.userScore;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load scores';
		} finally {
			loading = false;
		}
	}

	// Create histogram data
	let histogramData: Array<{ bucket: number; min: number; max: number; count: number; label: string }> = $state([]);

	let totalPlayers = $derived(scores.reduce((sum, s) => sum + s.count, 0));

	// Update histogram when scores change
	$effect(() => {
		if (scores.length === 0) {
			histogramData = [];
			return;
		}

		const maxScore = gameType === 'line' ? 100 : 5;
		const numBuckets = 5; // Always 5 buckets now

		// Create buckets
		const buckets = Array.from({ length: numBuckets }, (_, i) => ({
			bucket: i,
			min: (i * maxScore) / numBuckets,
			max: ((i + 1) * maxScore) / numBuckets,
			count: 0,
			label: gameType === 'line'
				? `${Math.round((i + 0.5) * 20)}%`
				: `${Math.round((i + 0.5) * maxScore / numBuckets)}`
		}));

		// Count scores in each bucket
		scores.forEach(({ score, count }) => {
			const bucketIndex = Math.min(
				Math.floor((score / maxScore) * numBuckets),
				numBuckets - 1
			);
			buckets[bucketIndex].count += count;
		});

		histogramData = buckets;
	});

	// Chart dimensions
	const chartWidth = $derived(containerWidth - margin.left - margin.right);
	const chartHeight = $derived(height - margin.top - margin.bottom);

	// Responsive font sizes
	const axisFontSize = '12px';
	const labelFontSize = '13px';
	const youFontSize = '13px';

	$effect(() => {
		if (!svg || loading || error || histogramData.length === 0) return;

		// Clear previous content
		d3.select(svg).selectAll('*').remove();

		const g = d3.select(svg)
			.attr('width', containerWidth)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Scales
		const xScale = d3.scaleBand()
			.domain(histogramData.map((d: any) => d.label))
			.range([0, chartWidth])
			.padding(0.1);

		const yScale = d3.scaleLinear()
			.domain([0, d3.max(histogramData, (d: any) => d.count) || 1])
			.range([chartHeight, 0]);

		// Bars
		g.selectAll('.bar')
			.data(histogramData)
			.enter()
			.append('rect')
			.attr('class', 'bar')
			.attr('x', (d: any) => xScale(d.label) || 0)
			.attr('y', (d: any) => yScale(d.count))
			.attr('width', xScale.bandwidth())
			.attr('height', (d: any) => chartHeight - yScale(d.count))
			.attr('fill', 'steelblue')
			.attr('rx', 2);

		// X axis
		g.append('g')
			.attr('transform', `translate(0,${chartHeight})`)
			.call(d3.axisBottom(xScale).tickSize(0).tickPadding(8))
			.selectAll('text')
			.style('font-size', axisFontSize)
			.style('font-family', "'Hanken Grotesk', sans-serif")
			.style('text-anchor', 'middle');

		// Y axis
		// g.append('g')
		// 	.call(d3.axisLeft(yScale).ticks(4).tickSize(0).tickPadding(8))
		// 	.selectAll('text')
		// 	.style('font-size', '12px')
		// 	.style('font-family', "'Hanken Grotesk', sans-serif");

		// Remove axis lines
		//g.selectAll('.domain').remove();

		// Add user score line
		if (userScore !== undefined && userScore !== null) {
			const maxScore = gameType === 'line' ? 100 : 5;
			const numBuckets = 5; // Always 5 buckets now
			const bucketIndex = Math.min(
				Math.floor((userScore / maxScore) * numBuckets),
				numBuckets - 1
			);

			const xPosition = (xScale(histogramData[bucketIndex]?.label) || 0) + xScale.bandwidth() / 2;

			g.append('line')
				.attr('x1', xPosition)
				.attr('x2', xPosition)
				.attr('y1', 0)
				.attr('y2', chartHeight)
				.attr('stroke', 'black')
				.attr('stroke-width', 3)
				.attr('stroke-dasharray', '8,6')
				.attr('opacity', 0.8);

			// Add label for user score
			g.append('text')
				.attr('x', xPosition)
				.attr('y', -5)
				.attr('text-anchor', 'middle')
				.style('font-size', youFontSize)
				.style('font-family', "'Hanken Grotesk', sans-serif")
				.style('fill', 'black')
				.style('font-weight', 'bold')
				.text('You');
		}

		// Add axis labels
		g.append('text')
			.attr('x', chartWidth / 2)
			.attr('y', chartHeight + 30)
			.attr('text-anchor', 'middle')
			.style('font-size', labelFontSize)
			.style('font-family', "'Hanken Grotesk', sans-serif")
			.style('fill', '#666')
			.text(gameType === 'line' ? 'Accuracy' : 'Correct Answers');

		g.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('x', -chartHeight / 2)
			.attr('y', -35)
			.attr('text-anchor', 'middle')
			.style('font-size', labelFontSize)
			.style('font-family', "'Hanken Grotesk', sans-serif")
			.style('fill', '#666')
			.text('Number of Players');
	});
</script>

{#if totalPlayers >= 5}
<div class="compare-container">
	<h3 class="title">Compare Your Score</h3>

	{#if loading}
		<div class="loading">Loading comparison data...</div>
	{:else if error}
		<div class="error">Failed to load comparison data</div>
	{:else if scores.length === 0}
		<div class="no-data">No scores available yet</div>
	{:else}
		<div class="chart-wrapper">
			<svg bind:this={svg}></svg>
		</div>
		
	{/if}
</div>
{/if}

<style>
	.compare-container {
		margin: 1rem auto;
		padding: 1rem;
		border-radius: 8px;
	}

	.title {
		text-align: center;
		margin: 0 0 1rem 0;
		font-size: 1.2rem;
		font-weight: bold;
		font-family: 'Hanken Grotesk', sans-serif;
		color: #333;
	}

	.chart-wrapper {
		width: 100%;
		display: flex;
		justify-content: center;
		margin-bottom: 0.5rem;
	}

	svg {
		display: block;
		max-width: 100%;
		height: auto;
	}

	.loading,
	.error,
	.no-data {
		text-align: center;
		padding: 2rem;
		font-size: 1rem;
		color: #666;
		font-family: 'Hanken Grotesk', sans-serif;
	}

	.error {
		color: #e74c3c;
	}

	@media (max-width: 768px) {
		.compare-container {
			margin: 0.5rem auto;
			padding: 0.75rem;
		}

		.title {
			font-size: 1.1rem;
		}
	}

	@media (max-width: 400px) {
		.compare-container {
			margin: 0.25rem auto;
			padding: 0.5rem;
		}

		.title {
			font-size: 1rem;
		}
	}
</style>