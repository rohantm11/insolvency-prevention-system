/**
 * Tracked (recently analyzed) companies stored in localStorage.
 * Keeps the last 5 single-company insolvency analyses for the Dashboard.
 */

export const WATCHLIST_STORAGE_KEY = 'solvency-insight-tracked-companies';
const MAX_TRACKED = 5;

export interface TrackedCompany {
  company_id: string | null;
  company_name: string | null;
  risk_category: 'Low' | 'Medium' | 'High';
  z_score: number;
  timestamp: string; // ISO
}

export function getTrackedCompanies(): TrackedCompany[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(WATCHLIST_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function addTrackedCompany(entry: Omit<TrackedCompany, 'timestamp'>): void {
  if (typeof window === 'undefined') return;
  const list = getTrackedCompanies();
  const withTimestamp: TrackedCompany = { ...entry, timestamp: new Date().toISOString() };
  const filtered = list.filter(
    (c) =>
      (c.company_id && c.company_id !== entry.company_id) ||
      (c.company_name && c.company_name !== entry.company_name)
  );
  const next = [withTimestamp, ...filtered].slice(0, MAX_TRACKED);
  localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(next));
}
