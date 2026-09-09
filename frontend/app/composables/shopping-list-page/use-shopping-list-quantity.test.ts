import { describe, expect, test } from "vitest";
import { formatShoppingListQuantity, roundShoppingListQuantity } from "./use-shopping-list-quantity";

describe("roundShoppingListQuantity", () => {
  test("rounds to two decimal places", () => {
    expect(roundShoppingListQuantity(1 / 3)).toStrictEqual(0.33);
    expect(roundShoppingListQuantity(2 / 3)).toStrictEqual(0.67);
    expect(roundShoppingListQuantity(0.126)).toStrictEqual(0.13);
  });

  test("keeps whole and short decimals as they are", () => {
    expect(roundShoppingListQuantity(3)).toStrictEqual(3);
    expect(roundShoppingListQuantity(4.5)).toStrictEqual(4.5);
    expect(roundShoppingListQuantity(0.25)).toStrictEqual(0.25);
  });

  test("treats missing values as zero", () => {
    expect(roundShoppingListQuantity(0)).toStrictEqual(0);
    expect(roundShoppingListQuantity(null)).toStrictEqual(0);
    expect(roundShoppingListQuantity(undefined)).toStrictEqual(0);
  });
});

describe("formatShoppingListQuantity", () => {
  test("renders decimals without trailing zeros", () => {
    expect(formatShoppingListQuantity(2 / 3)).toStrictEqual("0.67");
    expect(formatShoppingListQuantity(1.5)).toStrictEqual("1.5");
    expect(formatShoppingListQuantity(2)).toStrictEqual("2");
  });

  test("renders nothing for zero or missing quantities", () => {
    expect(formatShoppingListQuantity(0)).toStrictEqual("");
    expect(formatShoppingListQuantity(null)).toStrictEqual("");
  });
});
