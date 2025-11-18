<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Instructions from '$lib/components/Instructions.svelte';
	import InteractiveChart from '$lib/components/InteractiveChart.svelte';
	import ResultChart from '$lib/components/ResultsChart.svelte';

	import type { UserData } from '$lib/types/UserData.ts';

	import { returnFakeData } from '$lib/utils.ts';

	import { findID } from '$lib/utils.ts';
	import { onMount } from 'svelte';

	let id: Number = $state(1);

	let userData: UserData = $state({ id: 0, name: '', email: '', isAdmin: false });
	let filled: boolean = $state(false);
	let reveal: boolean = $state(false);

	let data = $state(returnFakeData());

	onMount(() => {
		id = findID();
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

<InteractiveChart
	bind:this={chart}
	data={data.data}
	xAxisLabel={data.xAxisLabel}
	yAxisLabel={data.yAxisLabel}
	{reveal}
/>

<button onclick={handleSubmit}>Submit</button>
<button onclick={handleClear}>Clear</button>
<button onclick={() => (reveal = !reveal)}>
	{#if reveal}
		Hide Results
	{:else}
		Reveal Results
	{/if}
</button>

<style>
</style>
