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



## Prompt

I’m planning another F1 watch party and need help choosing two snacks from the four uploaded options.

Please check my connected records for the F1 watch-party context, my earlier trail-mix plan, the store I planned to buy it from, and the gluten-free requirement I mentioned before. These may come from separate events, so don’t combine them.

Review each product using the front and back photos, the product CSV, the event requirements file, and the FDA PDFs. Check package size, ingredients, allergens, gluten-free claims, and whether the photos match the CSV. Keep “Contains” allergens separate from “may contain” warnings, and don’t assume something is gluten-free just because wheat is not listed.

Use the trail-mix photo only as a style reference. Then recommend exactly two products that are locally available, in stock, cost no more than $18 total, do not declare wheat, and have matching package sizes. At least one must clearly say gluten-free.

Save the full review as `snack_packaging_audit.md` and the final two choices as `snack_purchase_plan.csv` using these columns:

candidate,product_name,listed_price_usd,visible_gluten_free,declared_contains,voluntary_warning,package_size_match,trail_mix_similarity,selection_reason


## Updated prompt

I’m planning another F1 watch party and need help choosing two snacks from the four options I uploaded.

Please check my connected records for the F1 watch-party details, my earlier trail-mix idea and the store I mentioned, and the gluten-free requirement from a previous event. These may be from different occasions, so keep them separate.

Compare the four products using the package photos, product CSV, event requirements, and FDA guides. Check whether the package details match the CSV, what allergens are listed, whether the product clearly says gluten-free, and whether anything is missing, unclear, or inconsistent. Please keep “contains” and “may contain” warnings separate, and don’t assume a product is gluten-free just because wheat is not listed.

Use the trail-mix photo only to see which option is most similar. Then choose exactly two snacks that are in stock locally, cost no more than $18 in total, do not declare wheat, and have matching package sizes. At least one of them must clearly be labeled gluten-free.

Save the full audit as `snack_packaging_audit.md` and the final two choices as `snack_purchase_plan.csv` with these columns:

candidate,product_name,listed_price_usd,visible_gluten_free,declared_contains,voluntary_warning,package_size_match,trail_mix_similarity,selection_reason