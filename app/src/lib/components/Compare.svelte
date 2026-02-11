<script lang="ts">
    import { onMount } from 'svelte';
    import * as d3 from 'd3';

    let {
        datasetId,
        userId,
        gameType
    } = $props<{
        datasetId: number;
        userId: number;
        gameType: 'line' | 'order';
    }>();

    let svg = $state<any>();
    let scores: Array<{ score: number; count: number }> = $state([]);
    let userScore: number | null = $state(null);
    let loading = $state(true);
    let error = $state('');

    // Responsive container
    let containerWidth = $state(600);
    let margin = $derived(containerWidth < 768 ? { top: 20, right: 30, bottom: 40, left: 30 } : { top: 20, right: 30, bottom: 40, left: 50 });
    const height = $derived(containerWidth < 768 ? 250 : 300);

    // Update width function
    const updateWidth = () => {
        if (svg) {
            const container = svg.parentElement;
            if (container) {
                containerWidth = container.clientWidth;
            }
        }
    };

    // Update width on mount and resize
    onMount(() => {
        window.addEventListener('resize', updateWidth);

        // Fetch scores
        fetchScores();

        return () => {
            window.removeEventListener('resize', updateWidth);
        };
    });

    async function fetchScores() {
        try {
            const response = await fetch(`/api/v1/scores?dataset_id=${datasetId}&user_id=${userId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch scores');
            }
            const data = await response.json();
            scores = data.scores;
            userScore = data.userScore;
        } catch (err) {
            error = err instanceof Error ? err.message : 'Failed to load scores';
        } finally {
            loading = false;
        }
    }

    // Create histogram data
    let histogramData: Array<{ bucket: number; min: number; max: number; count: number; label: string }> = $state([]);

    $inspect(scores)
    let totalPlayers = $derived(scores.reduce((sum, s) => sum + s.count, 0));

    // Update histogram when scores change
    $effect(() => {
        if (scores.length === 0) {
            histogramData = [];
            return;
        }

        const maxScore = gameType === 'line' ? 100 : 5;
        const numBuckets = 5; // Always 5 buckets now

        // Create buckets
        const buckets = Array.from({ length: numBuckets }, (_, i) => ({
            bucket: i,
            min: (i * maxScore) / numBuckets,
            max: ((i + 1) * maxScore) / numBuckets,
            count: 0,
            label: gameType === 'line'
                ? `${Math.round((i + 0.5) * 20)}%`
                : `${Math.round((i + 0.5) * maxScore / numBuckets)}`
        }));

        // Count scores in each bucket
        scores.forEach(({ score, count }) => {
            const bucketIndex = Math.min(
                Math.floor((score / maxScore) * numBuckets),
                numBuckets - 1
            );
            buckets[bucketIndex].count += count;
        });

        histogramData = buckets;
    });

    // Chart dimensions
    const chartWidth = $derived(containerWidth - margin.left - margin.right);
    const chartHeight = $derived(height - margin.top - margin.bottom);

    // Responsive font sizes
    const axisFontSize = $derived(containerWidth < 768 ? '13px' : '13px');
    const labelFontSize = $derived(containerWidth < 768 ? '14px' : '14px');
    const youFontSize = $derived(containerWidth < 768 ? '13px' : '13px');
    const percentageFontSize = $derived(containerWidth < 768 ? '9px' : '11px'); // Font size for percentage labels

    $effect(() => {
        if (svg) {
            updateWidth();
        }
        if (!svg || loading || error || histogramData.length === 0) return;

        // Clear previous content
        d3.select(svg).selectAll('*').remove();

        const g = d3.select(svg)
            .attr('width', containerWidth)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3.scaleBand()
            .domain(histogramData.map((d: any) => d.label))
            .range([0, chartWidth])
            .padding(0.1);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(histogramData, (d: any) => d.count) || 1])
            .range([chartHeight, 0]);

        // Bars
        g.selectAll('.bar')
            .data(histogramData)
            .enter()
            .append('rect')
            .attr('class', 'bar')
            .attr('x', (d: any) => xScale(d.label) || 0)
            .attr('y', (d: any) => yScale(d.count))
            .attr('width', xScale.bandwidth())
            .attr('height', (d: any) => chartHeight - yScale(d.count))
            .attr('fill', 'steelblue')
            .attr('rx', 2);

        // Count labels inside bars at bottom
        g.selectAll('.bar-label')
            .data(histogramData)
            .enter()
            .append('text')
            .attr('class', 'bar-label')
            .attr('x', (d: any) => (xScale(d.label) || 0) + xScale.bandwidth() / 2)
            .attr('y', (d: any) => yScale(d.count) + 15) // Top of bar plus 15px
            .attr('text-anchor', 'middle')
            .style('font-size', axisFontSize)
            .style('font-family', "'Hanken Grotesk', sans-serif")
            .style('fill', 'white')
            .style('font-weight', 'bold')
            .text((d: any) => {
                const percentage = totalPlayers > 0 ? Math.round((d.count / totalPlayers) * 100) : 0;
                return d.count > 0 ? `${percentage}%` : '';
            });
        

        // X axis - custom ticks
        const tickLabels = ['0%', '20%', '40%', '60%', '80%', '100%'];
        const tickPositions = [
            0,
            ...histogramData.map((d: any) => (xScale(d.label) || 0) + xScale.bandwidth()),
            chartWidth
        ];

        g.selectAll('.x-tick')
            .data(tickLabels)
            .enter()
            .append('text')
            .attr('class', 'x-tick')
            .attr('x', (d: any, i: number) => tickPositions[i])
            .attr('y', chartHeight+15)
            .attr('text-anchor', 'middle')
            .style('font-size', labelFontSize)
            .style('font-family', "'Hanken Grotesk', sans-serif")
            .style('fill', '#333')
            .text((d: any) => d);

        // Add x-axis line
        g.append('line')
            .attr('x1', 0)
            .attr('x2', chartWidth)
            .attr('y1', chartHeight)
            .attr('y2', chartHeight)
            .style('stroke', '#000')
            .style('stroke-width', 1.2);

        // Y axis
        // g.append('g')
        // 	.call(d3.axisLeft(yScale).ticks(4).tickSize(0).tickPadding(8))
        // 	.selectAll('text')
        // 	.style('font-size', '12px')
        // 	.style('font-family', "'Hanken Grotesk', sans-serif");

        // Remove axis lines
        //g.selectAll('.domain').remove();

        // Add user score line
        if (userScore !== undefined && userScore !== null) {
            const maxScore = gameType === 'line' ? 100 : 5;
            const numBuckets = 5; // Always 5 buckets now
            const bucketIndex = Math.min(
                Math.floor((userScore / maxScore) * numBuckets),
                numBuckets - 1
            );

            const xPosition = (xScale(histogramData[bucketIndex]?.label) || 0) + xScale.bandwidth() / 2;

        

            // Add label for user score
            g.append('text')
                .attr('x', xPosition)
                .attr('y', -5)
                .attr('text-anchor', 'middle')
                .style('font-size', youFontSize)
                .style('font-family', "'Hanken Grotesk', sans-serif")
                .style('fill', 'black')
                .style('font-weight', 'bold')
                .text('You');
        }

        // Add axis labels
        g.append('text')
            .attr('x', chartWidth / 2)
            .attr('y', chartHeight + 35) // Adjusted position
            .attr('text-anchor', 'middle')
            .style('font-size', labelFontSize)
            .style('font-family', "'Hanken Grotesk', sans-serif")
            .style('fill', '#000')
            .text(gameType === 'line' ? 'Accuracy' : 'Correct Answers');

        g.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -chartHeight / 2)
            .attr('y', -20)
            .attr('text-anchor', 'middle')
            .style('font-size', labelFontSize)
            .style('font-family', "'Hanken Grotesk', sans-serif")
            .style('fill', '#000')
            .text('# of Players');
    });
</script>

{#if totalPlayers >= 5}
<div class="compare-container">
    <h3 class="title">Compare Your Score</h3>

    {#if loading}
        <div class="loading">Loading comparison data...</div>
    {:else if error}
        <div class="error">Failed to load comparison data</div>
    {:else if scores.length === 0}
        <div class="no-data">No scores available yet</div>
    {:else}
        <div class="chart-wrapper">
            <svg bind:this={svg}></svg>
        </div>
        
    {/if}
</div>
{/if}

<style>
    .compare-container {
        margin: 1rem auto;
        padding: 1rem;
        border-radius: 8px;
    }

    .title {
        text-align: center;
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        font-weight: bold;
        font-family: 'Hanken Grotesk', sans-serif;
        color: #333;
    }

    .chart-wrapper {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-bottom: 0.5rem;
    }

    svg {
        display: block;
        max-width: 100%;
        height: auto;
    }

    .loading,
    .error,
    .no-data {
        text-align: center;
        padding: 2rem;
        font-size: 1rem;
        color: #666;
        font-family: 'Hanken Grotesk', sans-serif;
    }

    .error {
        color: #e74c3c;
    }

    @media (max-width: 768px) {
        .compare-container {
            margin: 0.5rem auto;
            padding: 0.75rem;
        }

        .title {
            font-size: 1.1rem;
        }
    }

    @media (max-width: 400px) {
        .compare-container {
            margin: 0.25rem auto;
            padding: 0.5rem;
        }

        .title {
            font-size: 1rem;
        }
    }
</style>