<script lang="ts">
	let {
		title = 'Problem Title',
		data = [],
		reveal = false,
		submitted = false,
		slots = $bindable([null, null, null, null, null]),
		correctSlots = $bindable(new Set<number>()),
		incorrectSlots = $bindable(new Set<number>())
	} = $props();

	const boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'The Bronx', 'Staten Island'];

	const boroughColors: Record<string, string> = {
		Manhattan: '#004B8D90',
		Brooklyn: '#00000090',
		Queens: '#B933AD90',
		'The Bronx': '#14244890',
		'Staten Island': '#A9B8C790'
	};

	const formatter = new Intl.NumberFormat('en', {
		notation: 'compact',
		compactDisplay: 'short' // ensures 'K' and 'M' instead of 'thousand' or 'million'
	});

	let availableBoroughs: string[] = $state([...boroughs]);
	let draggedItem: string | null = $state(null);
	let draggedFromSlot: number | null = $state(null);

	$inspect('slots', slots);

	// Watch for reveal or submitted changes and auto-sort
	$effect(() => {
		if ((reveal || (submitted && correctSlots.size < 5)) && data && data.length > 0) {
			// Sort data by sort_order to get correct positions
			const sorted = [...data].sort((a, b) => a.sort_order - b.sort_order);
			slots = sorted.map((item) => item.x);
			availableBoroughs = [];
		} else if (!reveal) {
			// Reset when reveal is turned off
			slots = [null, null, null, null, null];
			availableBoroughs = [...boroughs];
		}
	});

	function handleDragStart(borough: string, fromSlot: number | null = null) {
		draggedItem = borough;
		draggedFromSlot = fromSlot;
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
	}

	function handleDropOnSlot(slotIndex: number) {
		if (draggedItem === null) return;

		// If dragging from available boroughs
		if (draggedFromSlot === null) {
			// if slot already has an item move that one down to available in slote
			if (slots[slotIndex] !== null) {
				const temp = slots[slotIndex];

				// Find the next available (null) slot to move temp into
				if (temp !== null) {
					const nextNull = slots.findIndex((s, i) => s === null && i !== slotIndex);
					if (nextNull !== -1) {
						slots[nextNull] = temp;
					} else {
						// If no empty slot, put temp back to availableBoroughs
						availableBoroughs = [...availableBoroughs, temp];
					}
				}
			}
			slots[slotIndex] = draggedItem;
			availableBoroughs = availableBoroughs.filter((b) => b !== draggedItem);
		}
		// If dragging from another slot
		else {
			// Swap or shift items
			const temp = slots[slotIndex];
			slots[slotIndex] = draggedItem;

			// If target slot had an item, put it in the old slot
			if (temp !== null) {
				slots[draggedFromSlot] = temp;
			} else {
				slots[draggedFromSlot] = null;
			}
		}

		draggedItem = null;
		draggedFromSlot = null;
	}

	function handleDropOnAvailable() {
		if (draggedItem === null || draggedFromSlot === null) return;

		// Remove from slot and add back to available
		slots[draggedFromSlot] = null;
		availableBoroughs = [...availableBoroughs, draggedItem];

		draggedItem = null;
		draggedFromSlot = null;
	}
</script>

<div class="order-container">
	<div class="rank">RANK THE BOROUGHS</div>
	<h1 class="title">{title}</h1>
	<h2 class="subtitle">
		Drag and drop the boroughs into the correct order from 1 (highest) to 5 (lowest).
	</h2>

	<div class="main-container">
		<div class="slots-container">
			{#each slots as slot, index}
				<div class="row" class:centered={reveal}>
					<div
						class="slot {slot !== null ? 'filled' : ''}"
						ondragover={handleDragOver}
						ondrop={() => handleDropOnSlot(index)}
					>
						{#if slot === null}
							<span class="slot-number">{index + 1}</span>
						{/if}
						{#if slot !== null}
							<div
								class="borough-box placed"
								class:revealed={reveal}
								class:dark-text={['Brooklyn', 'The Bronx'].includes(slot)}
								class:light-bg={['Staten Island', 'Manhattan', 'Queens'].includes(slot)}
								class:incorrect-bg={incorrectSlots.has(index) && !reveal}
								class:correct-bg={correctSlots.has(index) && !reveal}
								draggable={!correctSlots.has(index)}
								ondragstart={() => handleDragStart(slot, index)}
								style="{!(incorrectSlots.has(index) && !reveal) &&
								!(correctSlots.has(index) && !reveal)
									? `border-color: ${boroughColors[slot]};`
									: ''} {reveal ? `background-color: ${boroughColors[slot]};` : ''}"
							>
								<div class="left-content">
									<span class="slot-number">{index + 1}</span>
									<span class="borough-name">{slot}</span>
								</div>
								{#if correctSlots.has(index) || reveal}
									<div class="right-content">
										{formatter.format(data.find((item) => item.x === slot)?.y)}
									</div>
								{/if}
							</div>
						{/if}
					</div>

					<div class="option-slot">
						{#if availableBoroughs[index]}
							<div
								class="borough-box"
								draggable="true"
								ondragstart={() => handleDragStart(availableBoroughs[index])}
								style="border-color: {boroughColors[availableBoroughs[index]]};"
							>
								{availableBoroughs[index]}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>

<style>
	.rank {
		font-size: 1rem;
		margin: 0 0 0.3rem 0;
		border: #999 2px dashed;
		border-radius: 6px;
		padding-inline: 4px;
		padding-block: 1.5px;
		width: fit-content;
		font-weight: 500;
	}
	.title {
		font-size: 1.5rem;
		font-weight: bold;
		margin: 0 0 0.5rem 0;
		font-family: 'Hanken Grotesk', sans-serif;
	}

	.subtitle {
		font-size: 1rem;
		color: #666;
		margin: 0 0 2rem 0;
		font-family: 'Hanken Grotesk', sans-serif;
	}
	.order-container {
		max-width: 800px;
		margin: 0 auto 1rem;
		padding: 1rem;
		border-radius: 4px;
	}

	h1 {
		font-size: 1.8rem;
		margin: 0 0 0.5rem 0;
		color: #333;
	}

	h2 {
		font-size: 1.2rem;
		margin: 0 0 2rem 0;
		color: #666;
		font-weight: normal;
	}

	.main-container {
		width: 100%;
	}

	.slots-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.row {
		display: flex;
		gap: 2rem;
	}

	.row.centered {
		justify-content: center;
	}

	.row.centered .slot {
		flex: none;
		width: 400px;
	}

	.row.centered .option-slot {
		display: none;
	}

	.slot {
		border: 2px dashed #999;
		border-radius: 8px;
		height: 60px;
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #f9f9f9;
		position: relative;
	}

	.option-slot {
		flex: 1;
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #f9f9f9;
		position: relative;
	}

	.slot.filled {
		border: none;
		background-color: transparent;
	}

	.slot-number {
		position: absolute;
		left: 1rem;
		font-size: 1.2rem;
		font-weight: bold;
		color: #999;
		z-index: 1;
	}

	.slot.filled:hover {
		background-color: transparent;
	}

	.available-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		flex: 1;
	}

	.borough-box {
		background-color: white;
		border: 3.5px solid #ddd;
		border-radius: 8px;
		padding: 0 1rem;
		text-align: center;
		font-size: 1.1rem;
		width: 100%;
		cursor: move;
		user-select: none;
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
		font-weight: 550;
	}

	.borough-box.placed {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 2rem;
		width: 100%;
		height: 100%;
		margin: 0;
		font-size: 1.1rem;
		font-weight: 550;
		box-sizing: border-box;
	}

	.borough-box.placed .left-content {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.borough-box.placed .right-content {
		margin-left: auto;
		font-size: 1.2rem;
		color: #666;
		font-weight: 550;
	}

	.borough-box.placed .slot-number {
		font-size: 1.2rem;
		font-weight: bold;
		color: #333;
	}

	.borough-box.placed .borough-name {
		padding-left: 0.5rem;
		color: black;
	}

	.animation-wrapper {
		position: relative;
		width: 100%;
		height: 100%;
	}

	.animation-wrapper.animating {
		animation: slideToPosition 2s ease-in-out;
	}

	.borough-box.placed.incorrect-bg {
		background-color: #fdd;
		border-color: rgb(130, 0, 0);
	}

	.borough-box.placed.correct-bg {
		background-color: #d4edda;
		border-color: #28a745;
	}

	.borough-box.placed.revealed .slot-number {
		color: white !important;
	}

	.borough-box.placed.revealed .borough-name {
		color: white !important;
	}

	.borough-box.placed.revealed.light-bg .borough-name {
		color: black !important;
	}

	.borough-box.placed.revealed.light-bg .slot-number {
		color: black !important;
	}

	.borough-box.placed.revealed.light-bg .right-content {
		color: black !important;
	}

	.borough-box.placed.revealed .right-content {
		color: white !important;
	}

	@keyframes slideToPosition {
		from {
			transform: translateY(var(--offset, 0));
		}
		to {
			transform: translateY(0);
		}
	}

	.borough-box:active {
		cursor: grabbing;
	}

	@media (max-width: 400px) {
		.rank {
			font-size: 0.9rem;
			padding-block: 0.5px;
		}

		.title {
			font-size: 1.3rem;
			margin-bottom: 0.3rem;
		}

		.subtitle {
			font-size: 0.9rem;
			margin-bottom: 1rem;
		}

		.order-container {
			padding: 0.5rem;
		}

		.slots-container {
			gap: 0.5rem;
		}

		.borough-box {
			border-width: 2px;
			font-size: 1rem;
			padding: 0 0.5rem;
			height: 50px;
		}

		.borough-box.placed {
			padding: 0 0.8rem;
			font-size: 1rem;
		}

		.borough-box.placed .slot-number {
			font-size: 1rem;
		}

		.borough-box.placed .right-content {
			font-size: 1rem;
		}

		.slot-number {
			font-size: 1rem;
		}

		.slot {
			height: 50px;
		}

		.option-slot {
			height: 50px;
		}
	}
</style>
