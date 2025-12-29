<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Instructions from '$lib/components/Instructions.svelte';
	import InteractiveChart from '$lib/components/InteractiveChart.svelte';
	import InteractiveOrder from '$lib/components/InteractiveOrder.svelte';
	import SubmitChart from '$lib/components/SubmitChart.svelte';
	import SubmitOrder from '$lib/components/SubmitOrder.svelte';

	import type { UserData } from '$lib/types/UserData';
	import type { DataSet } from '$lib/types/DataSet';

	import { currentGuess, revealAnswer, orderSlots, correctSlots } from '$lib/stores/utils';

	import { onMount } from 'svelte';
	import { page } from '$app/state';

	let data = $state(null as DataSet | null);
	let reveal: boolean = $state(false);
	let loading: boolean = $state(true);

	// Get dataset ID from URL parameter or default to 1
	// Access query parameters (e.g., /search?q=svelte)
	let dataset_id: number = $derived(parseInt(page.url.searchParams.get('id') || '1'));

	onMount(() => {
		// find data for chart using api
		fetch(`/api/v1/dataset?id=${dataset_id}`)
			.then((res) => res.json())
			.then((fetchedData) => {
				console.log('Fetched data:', fetchedData);
				data = fetchedData;
				loading = false;
			})
			.catch((error) => {
				console.error('Error fetching data:', error);
				loading = false;
			});
	});

	let chart: any;

	function handleSubmit() {
		const userDrawing = chart.getUserPoints();
		console.log('User drew:', userDrawing);
	}

	function handleClear() {
		chart.clearDrawing();
	}
</script>

<Header />
<Instructions />

{#if loading}
	<div class="loading">Loading chart data...</div>
{:else if data}
	{#if data.type == 'line'}
		<div class="chart-wrapper">
			<InteractiveChart
				bind:this={chart}
				title={data.title}
				subtitle={data.subtitle}
				data={data.data}
				yMin={data.yMin}
				yMax={data.yMax}
				reveal={$revealAnswer}
			/>
		</div>
		<SubmitChart guess={$currentGuess} {data} />
	{:else if data.type == 'order'}
		<div class="chart-wrapper">
			<InteractiveOrder
				title={data.title}
				data={data.data}
				reveal={$revealAnswer}
				bind:slots={$orderSlots}
				bind:correctSlots={$correctSlots}
			/>
		</div>
		<SubmitOrder {data} bind:slots={$orderSlots} bind:correctSlots={$correctSlots} />
	{/if}
{:else}
	<div class="error">Failed to load chart data</div>
{/if}

<style>
	.chart-wrapper {
		max-width: 600px;
		margin: 1rem auto;
	}

	.button-group {
		max-width: 500px;
		margin: 1rem auto;
		display: flex;
		gap: 1rem;
		justify-content: center;
	}

	.loading,
	.error {
		text-align: center;
		padding: 2rem;
		font-size: 1.2rem;
	}

	.error {
		color: red;
	}
</style>
