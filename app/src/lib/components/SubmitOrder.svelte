<script lang="ts">
	import type { DataSet } from '$lib/types/DataSet';
	import { revealAnswer } from '$lib/stores/utils';

	let {
		data,
		slots = $bindable(),
		correctSlots = $bindable(new Set<number>()),
		incorrectSlots = $bindable(new Set<number>()),
		userId,
		onFeedbackShown,
		onFeedbackHidden
	} = $props<{
		data: DataSet;
		slots?: (string | null)[];
		correctSlots?: Set<number>;
		incorrectSlots?: Set<number>;
		userId: number;
		onFeedbackShown?: () => void;
		onFeedbackHidden?: () => void;
	}>();

	$inspect('correctSlots', correctSlots);
	$inspect('incorrectSlots', incorrectSlots);

	type GameStateType = 'playing' | 'won' | 'lost';

	let numGuesses = $state(1);
	let maxGuesses = 3;
	let feedback = $state('');
	let gameState = $state<GameStateType>('playing');
	let datasetLink = $derived(data.source);
	let nycOpenDataLink = 'https://opendata.cityofnewyork.us/';

	function checkOrderScore(
		slots: (string | null)[],
		data: DataSet
	): { correct: number; status: string } {
		if (!data || !data.data || data.data.length === 0) return { correct: 0, status: 'wrong' };

		// Sort data by sort_order to get correct positions
		const correctOrder = [...data.data]
			.sort((a, b) => a.sort_order - b.sort_order)
			.map((item) => item.x);

		// Count how many are correct
		let correctCount = 0;
		const newCorrectSlots = new Set<number>();
		const newIncorrectSlots = new Set<number>();

		slots.forEach((borough, index) => {
			if (borough === correctOrder[index]) {
				correctCount++;
				newCorrectSlots.add(index);
			} else {
				newIncorrectSlots.add(index);
			}
		});

		correctSlots = newCorrectSlots;
		incorrectSlots = newIncorrectSlots;

		if (correctCount === slots.length) {
			return { correct: correctCount, status: 'won' };
		} else if (correctCount >= slots.length - 1) {
			return { correct: correctCount, status: 'close' };
		} else {
			return { correct: correctCount, status: 'wrong' };
		}
	}

	async function saveScore(numCorrect: number) {
		try {
			const response = await fetch('/api/v1/score', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					user_id: userId,
					dataset_id: data.dataset_id,
					score: numCorrect
				})
			});

			if (!response.ok) {
				console.error('Failed to save score:', await response.text());
			}
		} catch (error) {
			console.error('Error saving score:', error);
		}
	}

	async function updateGameState() {
		// Check if all slots are filled
		if (slots.some((slot: string | null) => slot === null)) {
			feedback = 'Please fill all slots before submitting.';
			return;
		}

		let result = checkOrderScore(slots, data);

		// Save score to database
		await saveScore(result.correct);

		if (result.status === 'won') {
			gameState = 'won';
			feedback = `Congratulations! All ${result.correct} are in the correct order!`;
			onFeedbackShown?.();
			$revealAnswer = true;
			return;
		} else {
			if (numGuesses >= maxGuesses) {
				gameState = 'lost';
				feedback = `Sorry, you have used all your guesses. You got ${result.correct} correct. The correct answer is now revealed.`;
				onFeedbackShown?.();
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
		onFeedbackShown?.();
		$revealAnswer = true;
	}

	function handleTryAgain() {
		gameState = 'playing';
		numGuesses = 1;
		feedback = '';
		onFeedbackHidden?.();
		$revealAnswer = false;
		correctSlots.clear();
		incorrectSlots.clear();
		slots = slots.map(() => null);
	}
</script>

{#snippet datasetInfo()}
	<br /> <br />
	This data is from the dataset from NYC Open Data.
	<a class="link" href={datasetLink} target="_blank">Access the data</a> or learn more about
	<a class="link" href={nycOpenDataLink} target="_blank">NYC Open Data</a>.
{/snippet}

<div class="submit-container">
	{#if gameState === 'playing'}
		<div class="guesses">
			<div class="boxes">
				{#each Array(maxGuesses) as _, index}
					<div class="box" class:filled={index < numGuesses}>
						{index + 1}
					</div>
				{/each}
			</div>
		</div>
	{/if}

	{#if feedback}
		<div class="feedback">
			{feedback}

			{#if gameState !== 'playing'}
				{@render datasetInfo()}
				<button class="try-again-btn" onclick={handleTryAgain}>Try Again</button>
			{/if}
		</div>
	{/if}

	{#if gameState === 'playing'}
		<div class="button-group">
			<button
				class="submit-btn"
				onclick={handleSubmit}
				disabled={numGuesses > maxGuesses || slots.some((slot: string | null) => slot === null)}
			>
				{#if numGuesses <= maxGuesses}
					Submit Guess
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
		margin: 0rem auto 1rem auto;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		align-items: center;
	}

	.guesses {
		display: flex;
		gap: 0.5rem;
		align-items: center;
		flex-direction: column;
	}

	.boxes {
		display: flex;
		gap: 0.5rem;
	}

	.box {
		width: 30px;
		height: 30px;
		border: 2px solid #ddd;
		border-radius: 4px;
		background-color: white;
		transition: all 0.3s;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: bold;
		font-size: 1rem;
		color: #000;
	}

	.box.filled {
		background-color: steelblue;
		border-color: steelblue;
		color: white;
	}

	.feedback {
		padding: 1rem;
		border-radius: 8px;
		font-size: 1rem;
		color: #333;
	}

	.link {
		color: steelblue;
		text-decoration: none;
		font-weight: bold;
	}

	.link:hover {
		text-decoration: underline;
	}

	.button-group {
		display: flex;
		gap: 1rem;
	}

	button {
		-webkit-appearance: none; /* Remove Safari's default button styling */
		-moz-appearance: none; /* Remove Firefox's default button styling */
		appearance: none; /* Remove default button styling for other browsers */
		padding: 0.5rem 1.5rem;
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
		border: solid 3px steelblue;
		background-color: white;
		font-weight: bold;
	}

	.submit-btn:hover:not(:disabled) {
		background-color: steelblue;
		color: white;
	}

	.give-up-btn {
		border: rgb(0, 0, 0,0.8)  solid 3px;
		background-color: white;
		font-weight: bold;
	}

	.give-up-btn:hover {
		background-color: black;
		color: white;
	}

	.try-again-btn {
		margin-top: 1rem;
		border: solid 3px steelblue;
		background-color: white;
		font-weight: bold;
		color: steelblue;
		margin-inline: auto;
		display: block;
		padding: 0.3rem 1rem;
	}

	.try-again-btn:hover {
		background-color: steelblue;
		color: white;
	}

	@media (max-width: 768px) {
		.feedback {
			padding: 0.75rem;
			font-size: 0.9rem;
		}

		.box {
			width: 25px;
			height: 25px;
			font-size: 0.9rem;
		}

		button {
			padding: 0.4rem 1rem;
			font-size: 0.9rem;
		}

		.try-again-btn {
			padding: 0.25rem 0.8rem;
			font-size: 0.9rem;
		}
	}

	@media (max-width: 400px) {
		button {
			padding: 0.3rem 0.8rem;
			font-size: 0.85rem;
		}

		.try-again-btn {
			padding: 0.2rem 0.6rem;
			font-size: 0.85rem;
		}

		.button-group {
			gap: 0.5rem;
		}
	}
</style>
