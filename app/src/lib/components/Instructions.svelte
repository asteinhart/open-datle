<script>
	// Instructions component for Open Datle game
	let isOpen = $state(false);
</script>

<div class="instructions-box">
	<button class="toggle-button" onclick={() => (isOpen = !isOpen)}>
		<span class="arrow" class:open={isOpen}>▶</span>
		<h2>How to Play</h2>
	</button>

	{#if isOpen}
		<ol>
			<li>Look at the data points provided on the chart</li>
			<li>Draw a line to predict the trend or pattern</li>
			<li>Submit your guess to see how close you were!</li>
		</ol>
	{/if}
</div>

<style>
	.instructions-box {
		border: 2px solid #ddd;
		border-radius: 8px;
		padding: 1rem;
		margin: 1rem auto;
		width: 600px;
		box-sizing: border-box;
	}

	.toggle-button {
		background: none;
		border: none;
		padding: 0;
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
		text-align: left;
	}

	.toggle-button:hover {
		opacity: 0.7;
	}

	.arrow {
		font-size: 1rem;
		transition: transform 0.2s ease;
		display: inline-block;
	}

	.arrow.open {
		transform: rotate(90deg);
	}

	h2 {
		margin: 0;
		color: #333;
		font-size: 1.1rem;
	}

	ol {
		margin: 1rem 0 0 0;
		padding-left: 1.5rem;
		color: #555;
	}

	li {
		margin-bottom: 0.75rem;
		line-height: 1.5;
		font-size: 0.9rem;
	}

	li:last-child {
		margin-bottom: 0;
	}

	@media (max-width: 768px) {
		.instructions-box {
			width: calc(100% - 2rem);
			margin: 0.5rem auto 0 auto;
			border-radius: 4px;
			padding: 0.5rem;
			max-width: 600px;
		}

		h2 {
			font-size: 1rem;
		}

		li {
			font-size: 0.85rem;
		}
	}
</style>
