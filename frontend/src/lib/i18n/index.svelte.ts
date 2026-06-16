// Reactive i18n: holds the active locale, persists it, and exposes the merged message tree
// as `i18n.m`. English is the fallback locale; a partial translation is overlaid on top of
// it so untranslated keys still render (see mergeMessages). Adding a language means
// importing its file and adding one entry to `locales` -- nothing else changes.

import { en } from "./en";
import type { Messages, PartialMessages } from "./en";

export type { Messages } from "./en";

export type Locale = "en" | "zh";

interface LocaleEntry {
	readonly name: string; // endonym shown in the language picker
	readonly messages: PartialMessages<Messages>;
}

import { zh } from "./zh";

export const locales: Record<Locale, LocaleEntry> = {
	en: { name: "English", messages: en },
	zh: { name: "中文", messages: zh },
};

// Picker-ready list derived from the registry; order follows declaration order above.
export const localeOptions: { value: Locale; name: string }[] = (
	Object.keys(locales) as Locale[]
).map((value) => ({ value, name: locales[value].name }));

const LOCALE_KEY = "pdl.locale";

function loadInitialLocale(): Locale {
	const saved = localStorage.getItem(LOCALE_KEY);
	if (saved !== null && saved in locales) return saved as Locale;
	const sys = navigator.language.split("-")[0];
	return sys in locales ? (sys as Locale) : "en";
}

function isMergeable(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

// Overlay a partial translation onto the English base: recurse into nested objects, fall
// back to English for any key the translation omits. Functions and primitives are leaves
// (replaced wholesale), so interpolation functions remain callable.
function mergeMessages<T>(base: T, override: PartialMessages<T>): T {
	// Rebuilt key-by-key from a shallow clone; cast at the boundary, returned as T below.
	const result = { ...(base as Record<string, unknown>) };
	for (const key of Object.keys(override)) {
		const overrideValue = (override as Record<string, unknown>)[key];
		if (overrideValue === undefined) continue;
		const baseValue = result[key];
		result[key] =
			isMergeable(baseValue) && isMergeable(overrideValue)
				? mergeMessages(baseValue, overrideValue)
				: overrideValue;
	}
	return result as T;
}

let locale = $state<Locale>(loadInitialLocale());

// Recomputed only when the locale changes; English is returned as-is (no merge needed).
const messages = $derived(
	locale === "en" ? en : mergeMessages(en, locales[locale].messages),
);

// Read-only reactive accessor. Components read `i18n.m.<section>.<key>`; every access
// re-runs on locale change because `messages` is a derived rune read through the getter.
export const i18n = {
	get locale(): Locale {
		return locale;
	},
	get m(): Messages {
		return messages;
	},
};

export function setLocale(next: Locale): void {
	locale = next;
	localStorage.setItem(LOCALE_KEY, next);
}
