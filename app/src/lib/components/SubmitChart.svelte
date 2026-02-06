<script lang="ts">
	import type { UserLine } from '$lib/types/UserLine';
	import type { DataSet } from '$lib/types/DataSet';
	import {
		currentGuess,
		guesses,
		revealAnswer,
		score,
		lastScorePercentage
	} from '$lib/stores/utils';

	let { data, guess } = $props<{
		data: DataSet;
		guess: UserLine;
	}>();

	type GameStateType = 'playing' | 'won' | 'lost' | 'gave-up';

	let numGuesses = $state(1);
	let maxGuesses = 3;
	let feedback = $state('');
	let gameState = $state<GameStateType>('playing');
	let accuracyText = $state('');
	let accuracyClass = $state('');

	let datasetLink = $derived(data.source);
	let nycOpenDataLink = 'https://opendata.cityofnewyork.us/';

	function guessScore(guess: UserLine, data: DataSet): { status: string; percentage: number } {
		// Check if 75% of segments are good and no segment is under ok
		console.log('Calculating guess score...');
		console.log('User guess points:', guess.points);
		console.log('Actual data points:', data.data);

		let dataPoints = data.data;
		let dataMaxY = Math.max(...dataPoints.map((d) => d.y));
		let dataMinY = Math.min(...dataPoints.map((d) => d.y));
		let unit = (dataMaxY - dataMinY) / 10;

		let totalSegments = dataPoints.length - 1;
		let goodCount = 0;
		let okCount = 0;
		let totalAreaDiff = 0;

		for (let i = 0; i < totalSegments; i++) {
			const userPoint1 = guess.points[i];
			const userPoint2 = guess.points[i + 1];

			const dataPoint1 = data.data[i];
			const dataPoint2 = data.data[i + 1];

			// calculate area difference for this segment
			let a =
				userPoint2.y > dataPoint2.y ? userPoint2.y - dataPoint2.y : dataPoint2.y - userPoint2.y;
			let b =
				userPoint1.y > dataPoint1.y ? userPoint1.y - dataPoint1.y : dataPoint1.y - userPoint1.y;
			let h = 1; // constant
			let areaDifference = ((a + b) / 2) * h;

			totalAreaDiff += areaDifference;

			let goodArea = (1.5 * unit + 1.5 * unit) / 2;
			let okArea = (2 * unit + 2 * unit) / 2;

			if (areaDifference <= goodArea) goodCount++;
			if (areaDifference <= okArea) okCount++;
		}

		// Calculate the worst possible guess: each user point is at the furthest bound (max or min y)
		let worstTotalDiff = 0;
		for (let i = 0; i < dataPoints.length; i++) {
			const dataY = dataPoints[i].y;
			const furthestY =
				Math.abs(dataY - dataMaxY) > Math.abs(dataY - dataMinY) ? dataMaxY : dataMinY;
			worstTotalDiff += Math.abs(dataY - furthestY);
		}

		// Calculate user's total difference
		let userTotalDiff = 0;
		for (let i = 0; i < dataPoints.length; i++) {
			userTotalDiff += Math.abs(dataPoints[i].y - guess.points[i].y);
		}

		let percentage =
			worstTotalDiff === 0
				? 100
				: Math.round(Math.max(0, (1 - userTotalDiff / worstTotalDiff) * 100));

		let status: string;
		if (goodCount >= 0.75 * totalSegments && okCount === totalSegments) {
			status = 'won';
		} else if (okCount === totalSegments) {
			status = 'close';
		} else {
			status = 'wrong';
		}

		return { status, percentage };
	}

	function updateGameState() {
		// check if guess accurate
		let result = guessScore(guess, data);
		let guessStatus = result.status;
		let percentage = result.percentage;

		score.set(guessStatus);
		lastScorePercentage.set(percentage);

		$guesses = [...$guesses, guess];
		$currentGuess = { points: [] };

		accuracyText = `${percentage}%`;
		accuracyClass = result.status === 'won' ? 'correct' : percentage >= 50 ? 'close' : 'far-off';

		if (guessStatus === 'won') {
			gameState = 'won';
			feedback = 'Congratulations! Your guess is';
			$revealAnswer = true;
			return;
		} else {
			if (numGuesses >= maxGuesses) {
				gameState = 'lost';
				feedback = 'Sorry, you have used all your guesses. Your last guess was';
				$revealAnswer = true;
				numGuesses++;
				return;
			} else {
				feedback = 'Not quite there, your guess is';
				gameState = 'playing';
				numGuesses++;
			}
		}
	}

	function handleSubmit() {
		updateGameState();
	}

	function handleGiveUp() {
		gameState = 'gave-up';
		feedback = 'You gave up.';
		$revealAnswer = true;
		$currentGuess = { points: [] };
	}

	function handleTryAgain() {
		gameState = 'playing';
		numGuesses = 1;
		feedback = '';
		$revealAnswer = false;
		$currentGuess = { points: [] };
		$guesses = [];
		score.set('');
		lastScorePercentage.set(0);
	}
</script>

{#snippet datasetInfo()}
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
			{#if gameState === 'won'}
				{feedback} <span class="accuracy {accuracyClass}">{accuracyText} correct</span> and very
				close to the actual line.
				<br /><br />
				<div class="dataset-info">
					{@render datasetInfo()}
				</div>
				<button class="try-again-btn" onclick={handleTryAgain}>Try Again</button>
			{:else if gameState === 'lost'}
				{feedback} <span class="accuracy {accuracyClass}">{accuracyText} correct</span>. The correct
				answer is now revealed.

				<br /><br />
				<div class="dataset-info">
					{@render datasetInfo()}
				</div>
				<button class="try-again-btn" onclick={handleTryAgain}>Try Again</button>
			{:else if gameState === 'gave-up'}
				{feedback} The correct answer is now revealed.
				<br /><br />
				<div class="dataset-info">
					{@render datasetInfo()}
				</div>
				<button class="try-again-btn" onclick={handleTryAgain}>Try Again</button>
			{:else}
				{feedback} <span class="accuracy {accuracyClass}">{accuracyText} correct</span>. Try again.
			{/if}
		</div>
	{/if}

	{#if gameState === 'playing'}
		<div class="button-group">
			<button
				class="submit-btn"
				onclick={handleSubmit}
				disabled={numGuesses > maxGuesses || guess.points.length < data.data.length}
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
		margin: 0 auto 1rem auto;
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
		width: 80%;
		padding: 1rem;
		background-color: #f0f0f0;
		border-radius: 8px;
		text-align: left;
		font-size: 1rem;
		color: #333;
		border: 2px solid #333;
	}

	.link {
		color: steelblue;
		text-decoration: none;
		font-weight: bold;
	}

	.link:hover {
		text-decoration: underline;
	}

	.accuracy {
		font-weight: bold;
	}

	.accuracy.correct {
		text-decoration: underline;
		text-decoration-color: steelblue;
		text-decoration-thickness: 2px;
	}

	.accuracy.close {
		text-decoration: underline;
		text-decoration-color: #ffb347;
		text-decoration-thickness: 2px;
	}

	.accuracy.far-off {
		text-decoration: underline;
		text-decoration-color: #e74c3c;
		text-decoration-thickness: 2px;
	}

	.button-group {
		display: flex;
		gap: 1rem;
	}

	button {
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
		border: #b32303 solid 3px;
		background-color: white;
		font-weight: bold;
	}

	.give-up-btn:hover {
		background-color: #b32303;
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
</style>
