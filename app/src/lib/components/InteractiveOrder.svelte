<script lang="ts">
	let {
		title = 'Problem Title',
		data = [],
		reveal = false,
		slots = $bindable([null, null, null, null, null]),
		correctSlots = $bindable(new Set<number>())
	} = $props();

	const boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'The Bronx', 'Staten Island'];

	const boroughColors: Record<string, string> = {
		Manhattan: '#7DD5C080',
		Brooklyn: '#00000080',
		Queens: '#FF591080',
		'The Bronx': '#00308780',
		'Staten Island': '#A9B8C780'
	};

	let availableBoroughs: string[] = $state([...boroughs]);
	let draggedItem: string | null = $state(null);
	let draggedFromSlot: number | null = $state(null);
	let isAnimating = $state(false);
	let animationOffsets: Record<number, number> = $state({});

	$inspect('slots', slots);

	// Watch for reveal changes and auto-sort
	$effect(() => {
		if (reveal && data && data.length > 0) {
			isAnimating = true;

			// Sort data by sort_order to get correct positions
			const sorted = [...data].sort((a, b) => a.sort_order - b.sort_order);

			// Store current positions before updating
			const currentPositions = new Map<string, number>();
			slots.forEach((borough, index) => {
				if (borough) currentPositions.set(borough, index);
			});

			// Calculate offsets for items that are moving
			const newOffsets: Record<number, number> = {};
			const newSlots = sorted.map((item) => item.x);

			newSlots.forEach((borough, targetIndex) => {
				const currentIndex = currentPositions.get(borough);
				if (currentIndex !== undefined) {
					// This borough is moving - calculate offset
					const rowHeight = 76; // 60px + 16px gap
					newOffsets[targetIndex] = (currentIndex - targetIndex) * rowHeight;
				}
			});

			// Set offsets first
			animationOffsets = newOffsets;

			// Then update slots after a tiny delay to trigger animation
			setTimeout(() => {
				slots = newSlots;
				availableBoroughs = [];

				// Clear offsets after animation completes
				setTimeout(() => {
					animationOffsets = {};
					isAnimating = false;
				}, 1200);
			}, 50);
		} else if (!reveal) {
			// Reset when reveal is turned off
			isAnimating = false;
			animationOffsets = {};
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
	<h1>Rank the borouhgs in order of {title}</h1>
	<h2>Drag and drop the boroughs into the correct order from 1 (highest) to 5 (lowest).</h2>

	<div class="main-container">
		<div class="slots-container">
			{#each slots as slot, index}
				<div class="row">
					<div
						class="slot {slot !== null ? 'filled' : ''}"
						ondragover={handleDragOver}
						ondrop={() => handleDropOnSlot(index)}
					>
						<span class="slot-number">{index + 1}</span>
						{#if slot !== null}
							<div
								class="borough-box placed"
								class:animating={animationOffsets[index] !== undefined}
								class:correct={correctSlots.has(index)}
								draggable="true"
								ondragstart={() => handleDragStart(slot, index)}
								style="border-color: {boroughColors[slot]}; {animationOffsets[index] !== undefined
									? `--offset: ${animationOffsets[index]}px;`
									: ''}"
							>
								{slot}
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
	.order-container {
		max-width: 800px;
		margin: 2rem auto;
		padding: 1.5rem;
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
	.slot {
		border: 2px dashed #999;
		border-radius: 8px;
		height: 60px;
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #f9f9f9;
		transition: all 0.2s;
		position: relative;
	}

	.option-slot {
		flex: 1;
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #f9f9f9;
		transition: all 0.2s;
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

	.borough-box {
		width: 100%;
	}

	.available-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		flex: 1;
	}

	.borough-box {
		background-color: white;
		border: 2px solid #ddd;
		border-radius: 8px;
		padding: 0 1rem;
		text-align: center;
		font-size: 1.1rem;
		cursor: move;
		user-select: none;
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
		transition:
			transform 0.2s,
			box-shadow 0.2s;
	}

	.borough-box.placed {
		width: 100%;
		height: 100%;
		border: 2px solid;
		margin: 0;
		padding: 1rem;
	}

	.borough-box.placed.animating {
		animation: slideToPosition 5s ease-in-out;
	}

	.borough-box.placed.correct {
		background-color: #d4edda;
	}

	@keyframes slideToPosition {
		from {
			transform: translateY(var(--offset, 0));
		}
		to {
			transform: translateY(0);
		}
	}

	.borough-box:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.borough-box:active {
		cursor: grabbing;
	}
</style>
