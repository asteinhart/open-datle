import { writable } from 'svelte/store';
import type { UserLine } from '$lib/types/UserLine';

export const guesses = writable<UserLine[]>([]);

export const currentGuess = writable<UserLine>({ points: [] });

export const revealAnswer = writable<boolean>(false);

export const orderSlots = writable<(string | null)[]>([null, null, null, null, null]);

export const score = writable<string>('');

export const lastScorePercentage = writable<number | null>(null);

export const correctSlots = writable<Set<number>>(new Set());

export const incorrectSlots = writable<Set<number>>(new Set());
