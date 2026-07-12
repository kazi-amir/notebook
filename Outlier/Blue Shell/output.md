## Story title

**Snack Packaging Audit for Michelle’s F1 Watch Party**

## Scenario

Michelle is planning another F1 watch party. Her past records show that she has bought trail mix from Whole Foods and has previously needed food suitable for a gluten-free guest.

She has four packaged-snack options, with front and back photos plus a CSV containing prices, package sizes, stock, and availability. She wants the packaging checked before buying.

The trail-mix and gluten-free details come from separate past events and must not be described as part of the same event.

## Agent objective

Review Michelle’s universe, the snack images, product CSV, event rules, and FDA references.

For each candidate, check:

* product and package size;
* Nutrition Facts and ingredients;
* declared allergens and “may contain” warnings;
* visible gluten-free claims;
* front/back image consistency;
* image-to-CSV package-size consistency.

Reject products that declare wheat or have conflicting package sizes.

Recommend exactly two locally available products with a combined price of no more than **$18**. At least one selected product must clearly show a gluten-free label.

## Desired outcome

Create a short audit that includes:

* relevant universe context;
* trail-mix reference observations;
* a comparison of all four candidates;
* package, allergen, and gluten-free findings;
* rejected products and reasons;
* exactly two recommended products;
* final combined price.

Do not treat missing gluten ingredients as proof that a product is gluten-free. Do not claim legal certification.

## Required files

### `snack_packaging_audit.md`

Include the context, candidate comparison, FDA-based findings, final recommendation, price total, and limitations.

### `snack_purchase_plan.csv`

Use these columns:

```csv
candidate,product_name,listed_price_usd,visible_gluten_free,declared_contains,voluntary_warning,package_size_match,trail_mix_similarity,selection_reason
```

Include exactly two selected products.

## Expected result

Select:

* **B — KIND**, $8.49, visibly gluten-free and similar to trail mix.
* **C — Nature Valley**, $5.99, package details match and suitable for sharing.

**Total: $14.48**

Reject:

* **A — SkinnyPop:** image shows 1 oz, but CSV says 4.4 oz.
* **D — Chex Mix:** declares wheat and has a likely size mismatch.
