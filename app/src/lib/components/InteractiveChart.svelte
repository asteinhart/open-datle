<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import type { UserLine } from '$lib/types/UserLine';
	import { guesses, currentGuess, score } from '$lib/stores/utils';

	// Props for the chart
	let {
		data = [],
		width = 600,
		height = 400,
		reveal = false,
		title = '',
		subtitle = null,
		yMin = null,
		yMax = null,
		lastScore = null
	} = $props();

	let svg: any;
	let containerWidth = $state(width);

	// Responsive height based on container width
	let chartHeight = $derived(
		containerWidth < 500 ? 250 : containerWidth < 768 ? 350 : containerWidth < 1024 ? 380 : 400
	);

	const margin = $derived(
		containerWidth < 600
			? { top: 20, right: 50, bottom: 20, left: 30 }
			: { top: 40, right: 80, bottom: 40, left: 50 }
	);

	const formatter = new Intl.NumberFormat('en', {
		notation: 'compact',
		compactDisplay: 'short' // ensures 'K' and 'M' instead of 'thousand' or 'million'
	});

	// Update width on mount and resize
	onMount(() => {
		const updateWidth = () => {
			if (svg) {
				const container = svg.parentElement;
				if (container) {
					containerWidth = container.clientWidth;
				}
			}
		};

		updateWidth();
		window.addEventListener('resize', updateWidth);

		return () => {
			window.removeEventListener('resize', updateWidth);
		};
	});

	// TODO parse x values correctly based on data type

	// Convert data x values to Date objects
	const processedData = $derived(
		data.map((d) => ({
			...d,
			x: typeof d.x === 'number' ? new Date(d.x, 0, 1) : d.x // Convert year number to Date
		}))
	);

	// User drawing state
	let isDrawing = $state(false);
	let lastX: Date | null = $state(null);
	let buffer = 365; // Distance along x-axis before adding new point
	let firstRelease = $state(false);
	let isPulsing = $state(false);
	let hasStartedDrawing = $state(false);

	// find data domains
	const xDomain = $derived(d3.extent(processedData, (d) => d.x) as [Date, Date]);
	const yDomain = $derived(
		yMin !== null && yMax !== null
			? [yMin, yMax]
			: (d3.extent(processedData, (d) => d.y) as [number, number])
	);

	// Handle mouse down - start drawing
	function handleMouseDown(event: MouseEvent) {
		if (reveal) return;
		d3.selectAll('.missing-line').interrupt();
		isPulsing = false;
		isDrawing = true;
		if (!hasStartedDrawing) hasStartedDrawing = true;
		addPoint(event);
	}

	// Handle mouse move - continue drawing
	function handleMouseMove(event: MouseEvent) {
		if (!isDrawing) return;
		addPoint(event);
	}

	// Handle mouse up - stop drawing
	function handleMouseUp() {
		isDrawing = false;
		lastX = null;
		if (!firstRelease && $currentGuess.points.length > 0) {
			firstRelease = true;
			isPulsing = true;
		}
	}

	// Handle touch start - start drawing
	function handleTouchStart(event: TouchEvent) {
		event.preventDefault();
		if (reveal) return;
		d3.selectAll('.missing-line').interrupt();
		isPulsing = false;
		isDrawing = true;
		if (!hasStartedDrawing) hasStartedDrawing = true;
		addPoint(event);
	}

	// Handle touch move - continue drawing
	function handleTouchMove(event: TouchEvent) {
		event.preventDefault();
		if (!isDrawing) return;
		addPoint(event);
	}

	// Handle touch end - stop drawing
	function handleTouchEnd(event: TouchEvent) {
		event.preventDefault();
		isDrawing = false;
		lastX = null;
		if (!firstRelease && $currentGuess.points.length > 0) {
			firstRelease = true;
			isPulsing = true;
		}
	}

	// Add a point based on mouse position
	function addPoint(event: MouseEvent | TouchEvent) {
		if (!svg) return;

		const chartWidth = containerWidth - margin.left - margin.right;
		const innerChartHeight = chartHeight - margin.top - margin.bottom;

		// Get position relative to SVG
		const rect = svg.getBoundingClientRect();
		let clientX: number, clientY: number;
		if (event instanceof TouchEvent) {
			const touch = event.touches[0];
			clientX = touch.clientX;
			clientY = touch.clientY;
		} else {
			clientX = event.clientX;
			clientY = event.clientY;
		}
		const mouseX = clientX - rect.left - margin.left;
		const mouseY = clientY - rect.top - margin.top;

		// Check if mouse is within chart bounds
		if (mouseX < 0 || mouseX > chartWidth || mouseY < 0 || mouseY > innerChartHeight) {
			return;
		}

		// Create scales
		const xScale = d3.scaleTime().domain(xDomain).range([0, chartWidth]);
		const yScale = d3.scaleLinear().domain(yDomain).range([innerChartHeight, 0]);

		// Convert mouse position to data coordinates
		const dataX = xScale.invert(mouseX);
		const dataY = yScale.invert(mouseY);

		// Find the closest x value in the processed data
		let closestDataPoint = processedData[0];
		let minDistance = Math.abs(dataX.getTime() - (closestDataPoint.x as Date).getTime());

		for (const point of processedData) {
			const distance = Math.abs(dataX.getTime() - (point.x as Date).getTime());
			if (distance < minDistance) {
				minDistance = distance;
				closestDataPoint = point;
			}
		}

		// Use the closest x from data, but keep user's y value
		const snappedX = closestDataPoint.x;

		// Check if we should add a new point based on buffer distance
		// For time scale, convert to milliseconds for comparison
		const snappedXTime = (snappedX as Date).getTime();
		const lastXTime = lastX ? lastX.getTime() : null;

		if (lastXTime === null || Math.abs(snappedXTime - lastXTime) >= buffer * 86400000) {
			// buffer converted to milliseconds (days * ms per day)

			// Prevent duplicate points at same x coordinate
			const existingPoint = $currentGuess.points.find((p) => {
				const pTime = typeof p.x === 'number' ? p.x : p.x.getTime();
				return Math.abs(pTime - snappedXTime) < buffer * 86400000;
			});
			if (!existingPoint) {
				$currentGuess.points.push({ x: snappedX, y: dataY });
				lastX = snappedX as Date;
			} else {
				// Update existing point's y value
				existingPoint.y = dataY;
			}
			$currentGuess = { ...$currentGuess }; // Trigger reactivity
		}
	}

	$effect(() => {
		if (!svg) return;

		// Clear pulsing if no current guess
		if ($currentGuess.points.length === 0) {
			isPulsing = false;
			firstRelease = false;
			d3.select(svg).select('.missing-g').remove();
		}

		// Clear previous content except missing lines
		d3.select(svg).selectAll(':not(.missing-g)').remove();

		const chartWidth = containerWidth - margin.left - margin.right;
		const innerChartHeight = chartHeight - margin.top - margin.bottom;

		// Create SVG container
		const g = d3
			.select(svg)
			.attr('width', containerWidth)
			.attr('height', chartHeight)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`)
			.attr('id', 'g-chart');

		// Create scales
		const xScale = d3.scaleTime().domain(xDomain).range([0, chartWidth]);

		const yScale = d3.scaleLinear().domain(yDomain).range([innerChartHeight, 0]);

		// Create line generator
		const line = d3
			.line()
			.x((d) => xScale(d.x))
			.y((d) => yScale(d.y));

		// Create line generator for user points (spline/curve)
		const userLineGenerator: d3.Line<any> = d3
			.line()
			.x((d) => xScale(d.x))
			.y((d) => yScale(d.y))
			.curve(d3.curveMonotoneX); // Smooth spline curve

		const yTickSpacing = containerWidth < 500 ? 100 : 125; // Pixels between ticks
		const xTickSpacing = containerWidth < 500 ? 80 : 70; // Pixels between ticks

		const yTickCount = Math.floor(width / yTickSpacing);
		// include Y min and max in ticks
		const yTicks = yScale.ticks(yTickCount);
		// if (!yTicks.includes(yDomain[1])) yTicks.push(yDomain[1]);

		let xtickCount = Math.floor(chartWidth / xTickSpacing);
		// include Y min and max in ticks
		const xTicks = xScale.ticks(xtickCount);
		// remove first tick to avoid overlap
		//xTicks.shift();

		// Add X axis
		const xAxis = g
			.append('g')
			.attr('transform', `translate(0,${innerChartHeight})`)
			.call(d3.axisBottom(xScale).tickValues(xTicks).tickSize(0).tickPadding(10));

		// Increase X axis font size
		xAxis
			.selectAll('text')
			.style('font-size', containerWidth < 500 ? '12px' : '14px')
			.style('font-family', "'Hanken Grotesk', sans-serif");

		// Add Y axis with labels only (no ticks, just domain line)
		const yAxis = g
			.append('g')
			.call(
				d3
					.axisLeft(yScale)
					.tickValues(yTicks)
					.tickSize(0)
					.tickPadding(5)
					.tickFormat(formatter.format)
			);

		// Increase Y axis font size
		yAxis
			.selectAll('text')
			.style('font-size', containerWidth < 500 ? '12px' : '14px')
			.style('font-family', "'Hanken Grotesk', sans-serif")
			.attr('text-anchor', 'start')
			.attr('x', -margin.left);

		// Add horizontal grid lines
		g.append('g')
			.attr('class', 'grid')
			.call(
				d3
					.axisLeft(yScale)
					.ticks(yTickCount)
					.tickSize(-chartWidth)
					.tickFormat(() => '')
			)
			.selectAll('line')
			.style('stroke', '#ddd')
			.style('stroke-opacity', 0.65)
			.style('stroke-width', 1);

		// Remove the grid domain line
		g.select('.grid .domain').remove();

		// Add vertical grid lines
		g.append('g')
			.attr('class', 'grid')
			.attr('transform', `translate(0,${innerChartHeight})`)
			.call(
				d3
					.axisBottom(xScale)
					.tickSize(-innerChartHeight)
					.tickFormat(() => '')
			)
			.selectAll('line')
			.style('stroke', '#ddd')
			.style('stroke-opacity', 0.65)
			.style('stroke-width', 1);

		// Remove the vertical grid domain line
		g.selectAll('.grid .domain').remove();

		// Add hint dot at center if not revealed
		if (!reveal) {
			const centerIndex = Math.floor(processedData.length / 2);
			const centerPoint = processedData[centerIndex];
			// add dot
			g.append('circle')
				.attr('cx', xScale(centerPoint.x))
				.attr('cy', yScale(centerPoint.y))
				.attr('r', 4)
				.attr('fill', 'steelblue');
		}

		// Add hint text at center if not started drawing and not revealed
		if (!hasStartedDrawing && !reveal) {
			const centerIndex = Math.floor(processedData.length / 2);
			const centerPoint = processedData[centerIndex];
			// add text below
			const textGroup = g
				.append('text')
				.attr('x', xScale(centerPoint.x))
				.attr('y', yScale(centerPoint.y) + 20)
				.attr('text-anchor', 'middle')
				.attr('font-size', '12px')
				.attr('fill', 'black')
				.attr('opacity', 0.5);
			textGroup
				.append('tspan')
				.attr('x', xScale(centerPoint.x))
				.attr('dy', '0')
				.text('Your line will go');
			textGroup
				.append('tspan')
				.attr('x', xScale(centerPoint.x))
				.attr('dy', '1.2em')
				.text('through this point');
		}

		// Add the line and data points only if reveal is true
		if (reveal) {
			// Add the line
			g.append('path')
				.datum(processedData)
				.attr('fill', 'none')
				.attr('stroke', 'steelblue')
				.attr('stroke-width', 3.5)
				.attr('d', line);

			// Add data points
			g.selectAll('.dot')
				.data(processedData)
				.enter()
				.append('circle')
				.attr('class', 'dot')
				.attr('cx', (d) => xScale(d.x))
				.attr('cy', (d) => yScale(d.y))
				.attr('r', 5)
				.attr('fill', 'steelblue');
		}

		// Add user-drawn line if there are user points
		if ($currentGuess.points && $currentGuess.points.length > 0) {
			// Create a set of user x values for quick lookup
			const userXSet = new Set(
				$currentGuess.points.map((p) => (typeof p.x === 'number' ? p.x : p.x.getTime()))
			);

			// Draw line segments between consecutive data points that both have user points
			for (let i = 0; i < processedData.length - 1; i++) {
				const point1 = processedData[i];
				const point2 = processedData[i + 1];
				const point1X = typeof point1.x === 'number' ? point1.x : point1.x.getTime();
				const point2X = typeof point2.x === 'number' ? point2.x : point2.x.getTime();

				const userPoint1 = $currentGuess.points.find(
					(p) => (typeof p.x === 'number' ? p.x : p.x.getTime()) === point1X
				);
				const userPoint2 = $currentGuess.points.find(
					(p) => (typeof p.x === 'number' ? p.x : p.x.getTime()) === point2X
				);

				if (userPoint1 && userPoint2) {
					const segment = [userPoint1, userPoint2];
					g.append('path')
						.datum(segment)
						.attr('fill', 'none')
						.attr('stroke', 'steelblue')
						.attr('stroke-width', 3)
						.attr('stroke-dasharray', '8,8')
						.attr('d', userLineGenerator);
				}
			}

			// Sort user points by x coordinate for dots
			const sortedUserPoints = [...$currentGuess.points].sort((a, b) => {
				const aTime = typeof a.x === 'number' ? a.x : a.x.getTime();
				const bTime = typeof b.x === 'number' ? b.x : b.x.getTime();
				return aTime - bTime;
			});

			// Add user points
			g.selectAll('.user-dot')
				.data(sortedUserPoints)
				.enter()
				.append('circle')
				.attr('class', 'user-dot')
				.attr('cx', (d) => xScale(d.x))
				.attr('cy', (d) => yScale(d.y))
				.attr('r', 4)
				.attr('fill', 'steelblue');
		}

		// Draw previous guesses from store with colored segments
		if ($guesses && $guesses.length > 0) {
			const yRange = yDomain[1] - yDomain[0];
			const threshold1 = 0.2 * yRange;
			const threshold2 = 0.4 * yRange;

			$guesses.forEach((guess, index) => {
				const isMostRecent = index === $guesses.length - 1;
				if (guess.points && guess.points.length > 0) {
					// Draw segments between consecutive data points that both have guess points
					for (let i = 0; i < processedData.length - 1; i++) {
						const point1 = processedData[i];
						const point2 = processedData[i + 1];
						const point1X = typeof point1.x === 'number' ? point1.x : point1.x.getTime();
						const point2X = typeof point2.x === 'number' ? point2.x : point2.x.getTime();

						const guessPoint1 = guess.points.find(
							(p) => (typeof p.x === 'number' ? p.x : p.x.getTime()) === point1X
						);
						const guessPoint2 = guess.points.find(
							(p) => (typeof p.x === 'number' ? p.x : p.x.getTime()) === point2X
						);

						if (guessPoint1 && guessPoint2) {
							const error = Math.abs(guessPoint1.y - point1.y) + Math.abs(guessPoint2.y - point2.y);
							const color =
								error < threshold1
									? '#3bb273' // green (saturated, bright)
									: error < threshold2
										? '#ffb347' // orange (saturated, bright)
										: '#e74c3c'; // red (saturated, bright)
							const opacity = reveal ? 0.2 : isMostRecent ? 0.8 : 0.2;

							const segment = [guessPoint1, guessPoint2];
							g.append('path')
								.datum(segment)
								.attr('fill', 'none')
								.attr('stroke', color)
								.attr('stroke-width', 3)
								.attr('stroke-opacity', opacity)
								.attr('d', userLineGenerator);
						}
					}
				}
			});
		}

		// Pulse missing points if first release happened
		if (firstRelease && $currentGuess.points.length > 0) {
			let missingG = d3.select(svg).select('.missing-g');
			if (missingG.empty()) {
				missingG = d3.select(svg).append('g').attr('class', 'missing-g');
			}

			const userXSet = new Set(
				$currentGuess.points.map((p) => (typeof p.x === 'number' ? p.x : p.x.getTime()))
			);
			const missingPoints = processedData.filter(
				(d) => !userXSet.has(typeof d.x === 'number' ? d.x : d.x.getTime())
			);

			// Update lines
			const lines = missingG.selectAll('.missing-line').data(missingPoints, (d) => d.x);

			lines
				.enter()
				.append('line')
				.attr('class', 'missing-line')
				.attr('x1', (d) => margin.left + xScale(d.x))
				.attr('x2', (d) => margin.left + xScale(d.x))
				.attr('y1', margin.top)
				.attr('y2', margin.top + innerChartHeight)
				.attr('stroke', 'black')
				.attr('stroke-width', 2)
				.attr('opacity', 0);

			lines.exit().remove();

			// Pulse function
			function pulseLines() {
				if (!isPulsing) return;
				missingG
					.selectAll('.missing-line')
					.transition()
					.duration(1000)
					.attr('opacity', 0.4)
					.transition()
					.duration(1000)
					.attr('opacity', 0)
					.on('end', pulseLines);
			}

			if (!missingG.selectAll('.missing-line').empty()) {
				pulseLines();
			}
		} else {
			// Remove missing lines if not first release
			d3.select(svg).select('.missing-g').remove();
		}
	});
</script>

<div class="chart-container">
	<div class="draw">DRAW THE LINE</div>
	<div class="header">
		<div class="title-section">
			{#if title}
				<h1 class="chart-title">{title}</h1>
			{/if}
			{#if subtitle}
				<p class="chart-subtitle">{subtitle}</p>
			{/if}
		</div>
	</div>
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<svg
		bind:this={svg}
		role="application"
		aria-label="Interactive chart - click and drag to draw"
		onmousedown={handleMouseDown}
		onmousemove={handleMouseMove}
		onmouseup={handleMouseUp}
		onmouseleave={handleMouseUp}
		ontouchstart={handleTouchStart}
		ontouchmove={handleTouchMove}
		ontouchend={handleTouchEnd}
	></svg>
</div>

<style>
	.draw {
		font-size: 1rem;
		font-weight: 500;
		margin: 0 0 0.5rem 0;
		text-decoration: underline wavy steelblue 2px;
		text-underline-offset: 3px;
	}
	.chart-title {
		font-size: 1.5rem;
		font-weight: bold;
		margin: 0 0 0.5rem 0;
		font-family: 'Hanken Grotesk', sans-serif;
	}

	.chart-subtitle {
		font-size: 1rem;
		color: #666;
		margin: 0 0 0.5rem 0;
		font-family: 'Hanken Grotesk', sans-serif;
	}

	.chart-container {
		width: 100%;
		padding: 1rem;
		margin: auto;
		border-radius: 4px;
		overflow: hidden;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		margin-bottom: 0.5rem;
	}

	.title-section {
		flex: 1;
	}

	.score-display {
		border: 2px solid steelblue;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-weight: bold;
		color: black;
		font-size: 1rem;
		background-color: white;
	}

	svg {
		user-select: none;
		display: block;
		cursor: pointer;
		touch-action: none;
	}

	@media (max-width: 768px) {
		.chart-container {
			padding: 0.5rem;
			width: 100%;
		}
		.chart-title {
			font-size: 1.2rem;
		}
		.chart-subtitle {
			font-size: 0.9rem;
		}
		.draw {
			font-size: 0.9rem;
		}
		.score-display {
			font-size: 0.9rem;
			padding: 0.2rem 0.4rem;
		}
	}
</style>
