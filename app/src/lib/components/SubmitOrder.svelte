<script lang="ts">
	import type { DataSet } from '$lib/types/DataSet';
	import { revealAnswer } from '$lib/stores/utils';

	let {
		data,
		slots = $bindable(),
		correctSlots = $bindable(new Set<number>())
	} = $props<{
		data: DataSet;
		slots?: (string | null)[];
		correctSlots?: Set<number>;
	}>();

	type GameStateType = 'playing' | 'won' | 'lost';

	let numGuesses = $state(1);
	let maxGuesses = 3;
	let feedback = $state('');
	let gameState = $state<GameStateType>('playing');

	function checkOrderScore(
		slots: (string | null)[],
		data: DataSet
	): { correct: number; status: string } {
		if (!data || data.length === 0) return { correct: 0, status: 'wrong' };

		// Sort data by sort_order to get correct positions
		const correctOrder = [...data.data]
			.sort((a, b) => a.sort_order - b.sort_order)
			.map((item) => item.x);

		// Count how many are correct
		let correctCount = 0;
		const newCorrectSlots = new Set<number>();

		slots.forEach((borough, index) => {
			if (borough === correctOrder[index]) {
				correctCount++;
				newCorrectSlots.add(index);
			}
		});

		correctSlots = newCorrectSlots;

		if (correctCount === slots.length) {
			return { correct: correctCount, status: 'won' };
		} else if (correctCount >= slots.length - 1) {
			return { correct: correctCount, status: 'close' };
		} else {
			return { correct: correctCount, status: 'wrong' };
		}
	}

	function updateGameState() {
		// Check if all slots are filled
		if (slots.some((slot) => slot === null)) {
			feedback = 'Please fill all slots before submitting.';
			return;
		}

		let result = checkOrderScore(slots, data);

		if (result.status === 'won') {
			gameState = 'won';
			feedback = `Congratulations! All ${result.correct} are in the correct order!`;
			$revealAnswer = true;
			return;
		} else {
			if (numGuesses >= maxGuesses) {
				gameState = 'lost';
				feedback = `Sorry, you have used all your guesses. You got ${result.correct} correct. The correct answer is now revealed.`;
				$revealAnswer = true;
				numGuesses++;
				return;
			} else {
				feedback =
					result.status === 'close'
						? `Close! You got ${result.correct} correct. Try again.`
						: `You got ${result.correct} correct. Keep trying!`;
				gameState = 'playing';
				numGuesses++;
			}
		}
	}

	function handleSubmit() {
		updateGameState();
	}

	function handleGiveUp() {
		gameState = 'lost';
		feedback = 'You gave up. The correct answer is now revealed.';
		$revealAnswer = true;
	}
</script>

<div class="submit-container">
	{#if gameState === 'playing'}
		<div class="guess-indicators">
			{#each Array(maxGuesses) as _, index}
				<div
					class="dot"
					class:active={index < numGuesses}
					class:current={index === numGuesses - 1}
				></div>
			{/each}
		</div>
	{/if}

	{#if feedback}
		<div class="feedback">{feedback}</div>
	{/if}

	{#if gameState === 'playing'}
		<div class="button-group">
			<button
				class="submit-btn"
				onclick={handleSubmit}
				disabled={numGuesses > maxGuesses || slots.some((slot) => slot === null)}
			>
				{#if numGuesses <= maxGuesses}
					Submit Guess {numGuesses}/{maxGuesses}
				{:else}
					Lost
				{/if}
			</button>
			<button class="give-up-btn" onclick={handleGiveUp}>Give Up</button>
		</div>
	{/if}
</div>

<style>
	.submit-container {
		max-width: 500px;
		margin: 2rem auto;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		align-items: center;
	}

	.guess-indicators {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.dot {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background-color: #ddd;
		transition: background-color 0.3s;
	}

	.dot.active {
		background-color: #4caf50;
	}

	.dot.current {
		background-color: #2196f3;
		animation: pulse 1s infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.2);
		}
	}

	.feedback {
		padding: 1rem;
		background-color: #f0f0f0;
		border-radius: 8px;
		text-align: center;
		font-size: 1rem;
		color: #333;
	}

	.button-group {
		display: flex;
		gap: 1rem;
	}

	button {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		cursor: pointer;
		transition:
			background-color 0.2s,
			transform 0.1s;
	}

	button:hover:not(:disabled) {
		transform: translateY(-2px);
	}

	button:active:not(:disabled) {
		transform: translateY(0);
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.submit-btn {
		background-color: #2196f3;
		color: white;
		font-weight: bold;
	}

	.submit-btn:hover:not(:disabled) {
		background-color: #1976d2;
	}

	.give-up-btn {
		background-color: #f44336;
		color: white;
	}

	.give-up-btn:hover {
		background-color: #d32f2f;
	}
</style>
