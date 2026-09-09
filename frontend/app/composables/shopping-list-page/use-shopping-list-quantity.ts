/**
 * Shopping list quantities are stored rounded to two decimal places (see the backend
 * shopping list service), so the list renders them as plain decimals rather than fractions.
 */
export const SHOPPING_LIST_QUANTITY_PRECISION = 2;

export function roundShoppingListQuantity(quantity: number | null | undefined): number {
  if (!quantity || Number.isNaN(quantity)) {
    return 0;
  }

  const factor = 10 ** SHOPPING_LIST_QUANTITY_PRECISION;
  return Math.round(quantity * factor) / factor;
}

export function formatShoppingListQuantity(quantity: number | null | undefined): string {
  const rounded = roundShoppingListQuantity(quantity);
  return rounded ? rounded.toString() : "";
}
