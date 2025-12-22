<script lang="ts">
	import type { UserLine } from '$lib/types/UserLine';
	import type { DataSet } from '$lib/types/DataSet';
	import { currentGuess, guesses, revealAnswer } from '$lib/stores/utils';

	let { data, guess } = $props<{
		data: DataSet;
		guess: UserLine;
	}>();

	type GameStateType = 'playing' | 'won' | 'lost';

	let numGuesses = $state(1);
	let maxGuesses = 3;
	let feedback = $state('');
	let gameState = $state<GameStateType>('playing');

	function guessScore(guess: UserLine, data: DataSet): string {
		// attempt to calculate area between curve

		// loop though both list and take the next two points
		let totalAreaDifference = 0;
		let goodScore = 0;
		let okScore = 0;
		let dataPoints = data.data;

		// how to detemrine good score
		// take max min of y, break into 10, if within 2 then good, within 5 then ok, else bad
		let dataMaxY = Math.max(...dataPoints.map((d) => d.y));
		let dataMinY = Math.min(...dataPoints.map((d) => d.y));
		let unit = (dataMaxY - dataMinY) / 10;

		// I think i can just do data length will force guess to be same length
		for (let i = 0; i < dataPoints.length - 1; i++) {
			const userPoint1 = guess.points[i];
			const userPoint2 = guess.points[i + 1];

			const dataPoint1 = data.data[i];
			const dataPoint2 = data.data[i + 1];

			// calculate real score
			// which line is on top
			let a =
				userPoint2.y > dataPoint2.y ? userPoint2.y - dataPoint2.y : dataPoint2.y - userPoint2.y;
			let b =
				userPoint1.y > dataPoint1.y ? userPoint1.y - dataPoint1.y : dataPoint1.y - userPoint1.y;

			//always a constant so can just be 1
			let h = 1;

			// hmm trapezoid
			let areaDifference = ((a + b) / 2) * h;
			totalAreaDifference += areaDifference;

			// calculate good and ok score
			let goodArea = (1.5 * unit + 1.5 * unit) / 2; // this is dumb but for me
			goodScore += goodArea;

			let okArea = (2 * unit + 2 * unit) / 2;
			okScore += okArea;
		}

		// todo, only need to calculate good and ok score once

		if (totalAreaDifference <= goodScore) {
			return 'won';
		} else if (totalAreaDifference <= okScore) {
			return 'close';
		} else {
			return 'wrong';
		}
	}

	function updateGameState() {
		// check if guess accurate
		let guessStatus = guessScore(guess, data);

		$guesses = [...$guesses, guess];
		$currentGuess = { points: [] };

		if (guessStatus === 'won') {
			gameState = 'won';
			feedback = 'Congratulations! Your guess is very close to the actual line.';
			$revealAnswer = true;
			return;
		} else {
			if (numGuesses >= maxGuesses) {
				gameState = 'lost';
				feedback = 'Sorry, you have used all your guesses. The correct answer is now revealed.';

				$revealAnswer = true;
				numGuesses++;
				return;
			} else {
				feedback =
					guessStatus === 'close'
						? 'Not quite there, but you are close! Try again.'
						: 'That guess was off the mark. Give it another shot!';
				gameState = 'playing';
				numGuesses++;
			}
		}
	}

	function handleSubmit() {
		updateGameState();
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
				disabled={numGuesses > maxGuesses || guess.length < data.length}
			>
				{#if numGuesses <= maxGuesses}
					Submit Guess {numGuesses}/{maxGuesses}
				{:else}
					Lost
				{/if}
			</button>
			<button class="give-up-btn">Give Up</button>
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
