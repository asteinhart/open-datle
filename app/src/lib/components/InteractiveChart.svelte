<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import type { UserLine } from '$lib/types/UserLine';
	import { guesses, currentGuess } from '$lib/stores/utils';

	// Props for the chart
	let {
		data = [],
		width = 600,
		height = 400,
		reveal = false,
		title = '',
		subtitle = null,
		yMin = null,
		yMax = null
	} = $props();

	let svg: any;
	let containerWidth = $state(width);
	const margin = { top: 40, right: 30, bottom: 50, left: 60 };

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

	// find data domains
	const xDomain = $derived(d3.extent(processedData, (d) => d.x) as [Date, Date]);
	const yDomain = $derived(
		yMin !== null && yMax !== null
			? [yMin, yMax]
			: (d3.extent(processedData, (d) => d.y) as [number, number])
	);

	// Handle mouse down - start drawing
	function handleMouseDown(event: MouseEvent) {
		isDrawing = true;
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
	}

	// Add a point based on mouse position
	function addPoint(event: MouseEvent) {
		if (!svg) return;

		const chartWidth = containerWidth - margin.left - margin.right;
		const chartHeight = height - margin.top - margin.bottom;

		// Get mouse position relative to SVG
		const rect = svg.getBoundingClientRect();
		const mouseX = event.clientX - rect.left - margin.left;
		const mouseY = event.clientY - rect.top - margin.top;

		// Check if mouse is within chart bounds
		if (mouseX < 0 || mouseX > chartWidth || mouseY < 0 || mouseY > chartHeight) {
			return;
		}

		// Create scales
		const xScale = d3.scaleTime().domain(xDomain).range([0, chartWidth]);
		const yScale = d3.scaleLinear().domain(yDomain).range([chartHeight, 0]);

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

		// Clear previous content
		d3.select(svg).selectAll('*').remove();

		const chartWidth = containerWidth - margin.left - margin.right;
		const chartHeight = height - margin.top - margin.bottom;

		// Create SVG container
		const g = d3
			.select(svg)
			.attr('width', containerWidth)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Create scales
		const xScale = d3.scaleTime().domain(xDomain).range([0, chartWidth]);

		const yScale = d3.scaleLinear().domain(yDomain).range([chartHeight, 0]);

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

		// Add X axis
		const xAxis = g
			.append('g')
			.attr('transform', `translate(0,${chartHeight})`)
			.call(d3.axisBottom(xScale).tickSize(0).tickSizeOuter(0).tickPadding(10));
		// Increase X axis font size
		xAxis.selectAll('text').style('font-size', '14px');

		// Add Y axis with labels only (no ticks, just domain line)
		const yAxis = g.append('g').call(d3.axisLeft(yScale).ticks(6).tickSize(0).tickPadding(10));

		// Increase Y axis font size
		yAxis.selectAll('text').style('font-size', '14px');

		// Add horizontal grid lines
		g.append('g')
			.attr('class', 'grid')
			.call(
				d3
					.axisLeft(yScale)
					.ticks(6)
					.tickSize(-chartWidth)
					.tickFormat(() => '')
			)
			.selectAll('line')
			.style('stroke', '#ddd')
			.style('stroke-opacity', 0.5);

		// Remove the grid domain line
		g.select('.grid .domain').remove();

		// Add vertical grid lines
		g.append('g')
			.attr('class', 'grid')
			.attr('transform', `translate(0,${chartHeight})`)
			.call(
				d3
					.axisBottom(xScale)
					.tickSize(-chartHeight)
					.tickFormat(() => '')
			)
			.selectAll('line')
			.style('stroke', '#ddd')
			.style('stroke-opacity', 0.5);

		// Remove the vertical grid domain line
		g.selectAll('.grid .domain').remove();

		// Add the line and data points only if reveal is true
		if (reveal) {
			// Add the line
			g.append('path')
				.datum(processedData)
				.attr('fill', 'none')
				.attr('stroke', '#0066cc')
				.attr('stroke-width', 2)
				.attr('d', line);

			// Add data points
			g.selectAll('.dot')
				.data(processedData)
				.enter()
				.append('circle')
				.attr('class', 'dot')
				.attr('cx', (d) => xScale(d.x))
				.attr('cy', (d) => yScale(d.y))
				.attr('r', 4)
				.attr('fill', '#0066cc');
		}

		// Add user-drawn line if there are user points
		if ($currentGuess.points && $currentGuess.points.length > 0) {
			// Sort user points by x coordinate
			const sortedUserPoints = [...$currentGuess.points].sort((a, b) => {
				const aTime = typeof a.x === 'number' ? a.x : a.x.getTime();
				const bTime = typeof b.x === 'number' ? b.x : b.x.getTime();
				return aTime - bTime;
			});

			g.append('path')
				.datum(sortedUserPoints)
				.attr('fill', 'none')
				.attr('stroke', '#ff6b6b')
				.attr('stroke-width', 2)
				.attr('stroke-dasharray', '5,5')
				.attr('d', userLineGenerator);

			// Add user points
			g.selectAll('.user-dot')
				.data(sortedUserPoints)
				.enter()
				.append('circle')
				.attr('class', 'user-dot')
				.attr('cx', (d) => xScale(d.x))
				.attr('cy', (d) => yScale(d.y))
				.attr('r', 4)
				.attr('fill', '#ff6b6b');
		}

		// Draw previous guesses from store as gray lines
		if ($guesses && $guesses.length > 0) {
			$guesses.forEach((guess) => {
				if (guess.points && guess.points.length > 0) {
					// Sort guess points by x coordinate
					const sortedGuessPoints = [...guess.points].sort((a, b) => {
						const aTime = typeof a.x === 'number' ? a.x : a.x.getTime();
						const bTime = typeof b.x === 'number' ? b.x : b.x.getTime();
						return aTime - bTime;
					});

					g.append('path')
						.datum(sortedGuessPoints)
						.attr('fill', 'none')
						.attr('stroke', '#999')
						.attr('stroke-width', 2)
						.attr('stroke-opacity', 0.2)
						.attr('d', userLineGenerator);
				}
			});
		}
	});
</script>

{#if title}
	<h1 class="chart-title">{title}</h1>
{/if}
{#if subtitle}
	<p class="chart-subtitle">{subtitle}</p>
{/if}

<div class="chart-container">
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<svg
		bind:this={svg}
		role="application"
		aria-label="Interactive chart - click and drag to draw"
		onmousedown={handleMouseDown}
		onmousemove={handleMouseMove}
		onmouseup={handleMouseUp}
		onmouseleave={handleMouseUp}
	></svg>
</div>

<style>
	.chart-title {
		font-size: 1.5rem;
		font-weight: bold;
		margin: 0 0 0.5rem 0;
		font-family: 'Hanken Grotesk', sans-serif;
	}

	.chart-subtitle {
		font-size: 1rem;
		color: #666;
		margin: 0 0 1rem 0;
		font-family: 'Hanken Grotesk', sans-serif;
	}

	.chart-container {
		width: 100%;
		margin: 0;
	}

	svg {
		border: 1px solid #ddd;
		border-radius: 4px;
		cursor: crosshair;
		user-select: none;
		display: block;
	}
</style>
