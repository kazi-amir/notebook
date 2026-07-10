# Walmart Shopping Guide

## Departments & Categories

Walmart organizes products in a two-level hierarchy: Departments (broad) and Categories (specific).

### Department Overview

| Department | What's Inside | Price Range |
|-----------|--------------|-------------|
| Grocery & Essentials | Produce, dairy, meat, bakery, pantry staples, beverages | $0.50 – $50 |
| Electronics | TVs, computers, phones, gaming, smart home, accessories | $5 – $10,000+ |
| Home | Kitchen appliances, home decor, furniture, bedding, storage | $5 – $1,000+ |
| Clothing | Men's, women's, kids' apparel, shoes, accessories | $5 – $200 |
| Toys | Action figures, dolls, building sets, games, outdoor toys | $5 – $300 |
| Pets | Dog & cat food, treats, toys, health, beds, aquarium supplies | $2 – $200 |
| Pharmacy | OTC medications, vitamins, supplements, first aid, personal care | $2 – $80 |
| Sports & Outdoors | Fitness, camping, cycling, team sports, hunting, fishing | $5 – $1,000+ |
| Home Appliances | Major appliances, small kitchen appliances, vacuums, laundry | $20 – $2,000+ |

### Source Store Mapping

Products come from 9 specialized source stores:

| Source Store | Maps To | Products |
|-------------|---------|----------|
| grocery | Grocery & Essentials | ~920 |
| electronics_store | Electronics | ~240 |
| fashion | Clothing | ~180 |
| toy_store | Toys | ~260 |
| pet_store | Pets | ~214 |
| pharmacy | Pharmacy | ~127 |
| bakery | Grocery & Essentials (Bakery) | ~75 |
| sporting_goods | Sports & Outdoors | ~213 |
| home_appliances | Home Appliances | ~80 |

## Savings & Deals

### Identifying Deals
- Products with an `original_price` higher than the current `price` are on sale
- The `savings` and `savings_percent` fields show exactly how much you save
- Compare deals across brands for the best value

### Store Brand vs Name Brand
- Walmart's store brands (Great Value, Equate, Ol' Roy) typically cost 20-40% less than name brands
- For staple items (milk, bread, cleaning supplies), store brands are often comparable quality
- For specialty items, name brands may offer better formulation or taste

## Spending Analysis Guidance

### Monthly Trends
- Compare 3+ months to identify patterns
- Grocery spending tends to be consistent month-to-month; large swings indicate stock-up trips or special occasions
- Electronics/home purchases create spending spikes — these are normal one-time purchases

### Department Balance
- **Grocery-heavy**: The user relies on Walmart for food shopping — suggest checking weekly deals
- **Electronics-heavy**: Likely buying tech or gaming — check if items are still available for warranty purposes
- **Diverse spread**: General household shopper — benefits from Walmart+ for free delivery

### Category Insights
- Heavy spending in a single category may indicate a hobby, pet ownership, or specific household need
- Cross-reference with `favorites` to find reorder opportunities
- Low-variety favorites suggest strong brand loyalty — suggest trying alternatives for savings

### Order Frequency Patterns
- **Weekly** (4+ orders/month): Grocery-focused shopper, likely benefits from pickup or delivery
- **Biweekly** (2-3/month): Moderate shopper, mix of grocery and general merchandise
- **Monthly** (1/month): Stock-up shopper, likely buys in bulk

## Smart Shopping Tips

1. **Compare departments**: The same type of product may exist under different categories — search broadly first
2. **Check for savings**: Products with `original_price` > `price` show rollback/clearance deals
3. **Track spending by department**: Set category budgets (e.g., $400/month for groceries)
4. **Monitor favorites**: Frequently purchased items are worth checking for price drops
5. **Use subcategories**: Narrow searches with specific categories (e.g., "Produce" vs broad "Grocery")
6. **Review order history**: Past purchases help identify seasonal buying patterns and unnecessary recurring expenses
