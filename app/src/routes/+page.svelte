<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Instructions from '$lib/components/Instructions.svelte';
	import InteractiveChart from '$lib/components/InteractiveChart.svelte';
	import InteractiveOrder from '$lib/components/InteractiveOrder.svelte';
	import SubmitChart from '$lib/components/SubmitChart.svelte';
	import SubmitOrder from '$lib/components/SubmitOrder.svelte';

	import type { UserData } from '$lib/types/UserData';
	import type { DataSet } from '$lib/types/DataSet';

	import {
		currentGuess,
		revealAnswer,
		orderSlots,
		correctSlots,
		incorrectSlots,
		lastScorePercentage
	} from '$lib/stores/utils';

	import { onMount } from 'svelte';
	import { page } from '$app/state';

	// Get server data (today's dataset)
	let { data: serverData } = $props();

	let data = $state(null as DataSet | null);
	let reveal: boolean = $state(false);
	let loading: boolean = $state(true);

	// Get dataset ID from URL parameter, or use today's dataset from server, or default to 6
	let dataset_id: number = $derived(
		parseInt(page.url.searchParams.get('id') || '') || serverData?.todayDatasetId || 6
	);

	// admin mode
	let isAdmin: boolean = $derived(page.url.searchParams.get('admin') === 'true');

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
</script>

<Header />
{#if isAdmin}
	<div class="button-group">
		<button
			onclick={() => {
				const newId = dataset_id - 1 > 0 ? dataset_id - 1 : 1;
				window.location.search = `?id=${newId}${isAdmin ? '&admin=true' : ''}`;
			}}
		>
			Previous Dataset
		</button>
		<span>Dataset ID: {dataset_id}</span>
		<button
			onclick={() => {
				const newId = dataset_id + 1;
				window.location.search = `?id=${newId}${isAdmin ? '&admin=true' : ''}`;
			}}
		>
			Next Dataset
		</button>
	</div>
{/if}
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
				lastScore={$lastScorePercentage}
			/>
			<SubmitChart {data} guess={$currentGuess} />
		</div>
	{:else if data.type == 'order'}
		<div class="chart-wrapper">
			<InteractiveOrder
				title={data.title}
				data={data.data}
				reveal={$revealAnswer}
				bind:slots={$orderSlots}
				bind:correctSlots={$correctSlots}
				bind:incorrectSlots={$incorrectSlots}
			/>

			<SubmitOrder
				{data}
				bind:slots={$orderSlots}
				bind:correctSlots={$correctSlots}
				bind:incorrectSlots={$incorrectSlots}
			/>
		</div>
	{/if}
{:else}
	<div class="error">Failed to load chart data</div>
{/if}

<style>
	.chart-wrapper {
		max-width: 600px;
		width: 100%;
		margin: 1rem auto;
		border: 2px solid #ddd;
		margin-bottom: 4rem;
		border-radius: 8px;
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

	@media (max-width: 768px) {
		.chart-wrapper {
			margin: 0.5rem auto;
			margin-bottom: 2rem;
			border-radius: 4px;
		}
	}
</style>
