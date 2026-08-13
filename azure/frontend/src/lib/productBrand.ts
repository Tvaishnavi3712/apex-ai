/**
 * Product brand toggle — flips the user-visible product name between
 * "Apex" (default) and "Regulus Lens" (white-label deployment).
 *
 * When `regulus` is active:
 *   • Wordmark "APEX" → "REGULUS LENS"
 *   • "ApexSignal" → "Regulus Signal"
 *   • "Agent Hub" → "Regulus Hub"
 *   • "ApexLens"  → "Regulus Doc"
 *   • Page <title> and topbar wordmark follow the same swap
 *
 * Apex is the engineering codename; Regulus Lens is the customer-facing
 * product brand used in some white-label deployments. The toggle lives in
 * the Settings page and persists to localStorage.
 *
 * Storage key:  `apex.productBrand`  ('apex' | 'regulus')
 * Default:      'apex'
 */
import { useCallback, useEffect, useState } from 'react';

export type ProductBrand = 'apex' | 'regulus';

export const PRODUCT_BRAND_STORAGE_KEY = 'apex.productBrand';

/** Read the persisted brand, falling back to 'apex'. SSR-safe. */
function readPersisted(): ProductBrand {
  if (typeof window === 'undefined') return 'apex';
  try {
    const v = window.localStorage.getItem(PRODUCT_BRAND_STORAGE_KEY);
    if (v === 'regulus') return 'regulus';
  } catch { /* ignore */ }
  return 'apex';
}

/** Hook — returns [brand, setBrand]. Listens for cross-tab changes too. */
export function useProductBrand(): [ProductBrand, (b: ProductBrand) => void] {
  const [brand, setBrandState] = useState<ProductBrand>('apex');

  useEffect(() => {
    setBrandState(readPersisted());
    const onStorage = (e: StorageEvent) => {
      if (e.key === PRODUCT_BRAND_STORAGE_KEY) setBrandState(readPersisted());
    };
    const onCustom = () => setBrandState(readPersisted());
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', onStorage);
      window.addEventListener('apex:brandChange', onCustom);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('storage', onStorage);
        window.removeEventListener('apex:brandChange', onCustom);
      }
    };
  }, []);

  const setBrand = useCallback((b: ProductBrand) => {
    if (typeof window !== 'undefined') {
      try { window.localStorage.setItem(PRODUCT_BRAND_STORAGE_KEY, b); } catch { /* ignore */ }
      // Custom event so other components in the same tab pick up the change
      // immediately (the native storage event only fires for OTHER tabs).
      window.dispatchEvent(new Event('apex:brandChange'));
    }
    setBrandState(b);
  }, []);

  return [brand, setBrand];
}

/* ──────────────────────── Brand-aware label helpers ──────────────────────── */

/** Wordmark for the sidebar logo. */
export function brandWordmark(brand: ProductBrand): string {
  return brand === 'regulus' ? 'REGULUS LENS' : 'APEX';
}

/** Sub-text below the wordmark. */
export function brandSubtitle(brand: ProductBrand): string {
  return brand === 'regulus' ? 'DOCUMENT INTELLIGENCE' : 'AI PLATFORM';
}

/** Per-product-feature label swaps. Keep narrow and explicit. */
const APEX_TO_REGULUS: Record<string, string> = {
  'Apex Signal':  'Regulus Signal',
  'ApexSignal':   'Regulus Signal',
  'Agent Hub':    'Regulus Hub',
  'Apex Lens':    'Regulus Doc',
  'ApexLens':     'Regulus Doc',
  // Bare brand
  'Apex':         'Regulus Lens',
  'APEX':         'REGULUS LENS',
};
const REGULUS_TO_APEX = Object.entries(APEX_TO_REGULUS).reduce<Record<string, string>>((acc, [k, v]) => {
  acc[v] = k;
  return acc;
}, {});

/** Convert any product label to the active brand's variant. Idempotent. */
export function brandLabel(label: string, brand: ProductBrand): string {
  if (brand === 'regulus') {
    return APEX_TO_REGULUS[label] ?? label;
  }
  // Apex mode: undo a previously-applied Regulus label (defensive).
  return REGULUS_TO_APEX[label] ?? label;
}

/** Friendly display label of the active brand for the Settings dropdown etc. */
export function brandDisplayName(brand: ProductBrand): string {
  return brand === 'regulus' ? 'Regulus Lens' : 'Apex';
}
