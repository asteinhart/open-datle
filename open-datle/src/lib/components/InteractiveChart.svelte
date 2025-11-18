<script lang="ts">
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import type { UserPoint } from '$lib/types/UserPoints';

	// Props for the chart
	let {
		data = [],
		xAxisLabel = 'X Axis',
		yAxisLabel = 'Y Axis',
		width = 600,
		height = 400,
		reveal = false
	} = $props();

	let svg;
	const margin = { top: 20, right: 30, bottom: 50, left: 60 };

	// Convert data x values to Date objects
	const processedData = $derived(
		data.map((d) => ({
			...d,
			x: typeof d.x === 'number' ? new Date(d.x, 0, 1) : d.x // Convert year number to Date
		}))
	);

	// User drawing state
	let userPoints: UserPoint[] = $state([]);
	let isDrawing = $state(false);
	let lastX: Date | null = $state(null);
	let buffer = 365; // Distance along x-axis before adding new point

	// find data domains
	const xDomain = $derived(d3.extent(processedData, (d) => d.x) as [Date, Date]);
	const yDomain = $derived(d3.extent(processedData, (d) => d.y) as [number, number]);

	$inspect(processedData, xDomain, yDomain);

	// Handle mouse down - start drawing
	function handleMouseDown(event) {
		isDrawing = true;
		addPoint(event);
	}

	// Handle mouse move - continue drawing
	function handleMouseMove(event) {
		if (!isDrawing) return;
		addPoint(event);
	}

	// Handle mouse up - stop drawing
	function handleMouseUp() {
		isDrawing = false;
		lastX = null;
	}

	// Add a point based on mouse position
	function addPoint(event) {
		if (!svg) return;

		const chartWidth = width - margin.left - margin.right;
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
			const existingPoint = userPoints.find((p) => {
				const pTime = typeof p.x === 'number' ? p.x : p.x.getTime();
				return Math.abs(pTime - snappedXTime) < buffer * 86400000;
			});
			if (!existingPoint) {
				userPoints.push({ x: snappedX, y: dataY });
				userPoints = userPoints; // Trigger reactivity
				lastX = snappedX as Date;
			}
		}
	}

	$effect(() => {
		if (!svg) return;

		// Clear previous content
		d3.select(svg).selectAll('*').remove();

		const chartWidth = width - margin.left - margin.right;
		const chartHeight = height - margin.top - margin.bottom;

		// Create SVG container
		const svgElement = d3.select(svg).attr('width', width).attr('height', height);

		const g = svgElement.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

		// Create scales
		const xScale = d3.scaleTime().domain(xDomain).range([0, chartWidth]);

		const yScale = d3.scaleLinear().domain(yDomain).range([chartHeight, 0]);

		// Create line generator
		const line = d3
			.line()
			.x((d) => xScale(d.x))
			.y((d) => yScale(d.y));

		// Create line generator for user points
		const userLine = d3
			.line<UserPoint>()
			.x((d) => xScale(d.x))
			.y((d) => yScale(d.y));

		// Add X axis
		g.append('g')
			.attr('transform', `translate(0,${chartHeight})`)
			.call(d3.axisBottom(xScale))
			.append('text')
			.attr('x', chartWidth / 2)
			.attr('y', 40)
			.attr('fill', 'black')
			.attr('text-anchor', 'middle')
			.style('font-size', '12px')
			.text(xAxisLabel);

		// Add Y axis
		g.append('g')
			.call(d3.axisLeft(yScale))
			.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('x', -chartHeight / 2)
			.attr('y', -45)
			.attr('fill', 'black')
			.attr('text-anchor', 'middle')
			.style('font-size', '12px')
			.text(yAxisLabel);

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
		if (userPoints.length > 0) {
			// Sort user points by x coordinate
			const sortedUserPoints = [...userPoints].sort((a, b) => {
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
				.attr('d', userLine);

			// Add user points (skip the first point which is the last data point)
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
	});
</script>

<div class="chart-container">
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
	.chart-container {
		display: flex;
		justify-content: center;
		margin: 2rem 0;
	}

	svg {
		border: 1px solid #ddd;
		border-radius: 4px;
		background-color: white;
		cursor: crosshair;
		user-select: none;
	}
</style>
