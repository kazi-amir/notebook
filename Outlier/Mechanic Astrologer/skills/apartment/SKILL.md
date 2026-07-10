---
name: apartment
description: Search apartments, view details, save favorites, and filter by price, bedrooms, pet policy, amenities, and more. Use when the user asks about apartments, rentals, housing, real estate listings, or finding a place to live.
---

# Apartment

Search apartment listings, view details, save favorites, and filter by location, price, amenities, and more.

Data is pre-loaded. No setup needed.

## Browsing

```bash
# List all apartments
python3 {baseDir}/apartment_data.py list-all

# Get details for a specific apartment
python3 {baseDir}/apartment_data.py get-details --apartment-id APT001
```

## Searching

```bash
# Search by location
python3 {baseDir}/apartment_data.py search --location "Downtown"

# Search by name
python3 {baseDir}/apartment_data.py search --name "Sunset"

# Filter by price range
python3 {baseDir}/apartment_data.py search --min-price 1000 --max-price 2500

# Filter by bedrooms and bathrooms
python3 {baseDir}/apartment_data.py search --number-of-bedrooms 2 --number-of-bathrooms 1

# Filter by property type and furnished status
python3 {baseDir}/apartment_data.py search --property-type "Condo" --furnished-status "Furnished"

# Filter by pet policy and lease term
python3 {baseDir}/apartment_data.py search --pet-policy "Pets allowed" --lease-term "1 year"

# Filter by floor level
python3 {baseDir}/apartment_data.py search --floor-level "Penthouse"

# Filter by amenities (JSON array)
python3 {baseDir}/apartment_data.py search --amenities '["Pool", "Gym"]'

# Show only saved apartments
python3 {baseDir}/apartment_data.py search --saved-only true

# Combine multiple filters
python3 {baseDir}/apartment_data.py search --location "Midtown" --min-price 1500 --max-price 3000 --number-of-bedrooms 2 --pet-policy "Pets allowed"
```

### Search Filters

| Filter | Flag | Example |
|--------|------|---------|
| Name | `--name` | `--name "Sunset Lofts"` |
| Location | `--location` | `--location "Downtown"` |
| Zip code | `--zip-code` | `--zip-code 90210` |
| Price range | `--min-price`, `--max-price` | `--min-price 1000 --max-price 2500` |
| Bedrooms | `--number-of-bedrooms` | `--number-of-bedrooms 2` |
| Bathrooms | `--number-of-bathrooms` | `--number-of-bathrooms 1` |
| Property type | `--property-type` | `--property-type "Condo"` |
| Square footage | `--square-footage` | `--square-footage 800` |
| Furnished | `--furnished-status` | `--furnished-status "Furnished"` |
| Floor level | `--floor-level` | `--floor-level "Penthouse"` |
| Pet policy | `--pet-policy` | `--pet-policy "Pets allowed"` |
| Lease term | `--lease-term` | `--lease-term "1 year"` |
| Amenities | `--amenities` | `--amenities '["Pool", "Gym"]'` |
| Saved only | `--saved-only` | `--saved-only true` |

### Property Types

`Apartment`, `Condo`, `Loft`, `Studio`, `Townhouse`, `House`

### Furnished Status

`Furnished`, `Unfurnished`, `Semi-furnished`

### Floor Levels

`Ground floor`, `Upper floors`, `Penthouse`, `Basement`

### Pet Policies

`Pets allowed`, `No pets`, `Cats allowed`, `Dogs allowed`

### Lease Terms

`Month-to-month`, `6 months`, `1 year`, `Long term`

## Favorites

```bash
# Save an apartment
python3 {baseDir}/apartment_data.py save --apartment-id APT001

# Remove a saved apartment
python3 {baseDir}/apartment_data.py remove-saved --apartment-id APT001

# List all saved apartments
python3 {baseDir}/apartment_data.py list-saved
```

## Utility

```bash
# Show raw apartment data
python3 {baseDir}/apartment_data.py show
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me apartments downtown" | `search --location "Downtown"` |
| "Find 2-bedroom apartments under $2000" | `search --number-of-bedrooms 2 --max-price 2000` |
| "Any pet-friendly places?" | `search --pet-policy "Pets allowed"` |
| "Tell me about apartment APT005" | `get-details --apartment-id APT005` |
| "Save this apartment" | `save --apartment-id <id>` |
| "Show my saved apartments" | `list-saved` |
| "Remove APT003 from favorites" | `remove-saved --apartment-id APT003` |
| "Find furnished condos" | `search --property-type "Condo" --furnished-status "Furnished"` |
| "Apartments with pool and gym" | `search --amenities '["Pool", "Gym"]'` |
| "Show all listings" | `list-all` |
| "Month-to-month rentals?" | `search --lease-term "Month-to-month"` |

## Data Entities

### Apartment

| Field | Description |
|-------|-------------|
| `apartment_id` | Unique identifier |
| `name` | Listing name |
| `location` | Neighborhood or area |
| `zip_code` | 5-digit zip code |
| `price` | Monthly rent |
| `bedrooms` | Number of bedrooms |
| `bathrooms` | Number of bathrooms |
| `property_type` | Apartment, Condo, Loft, Studio, Townhouse, or House |
| `square_footage` | Living area in sq ft |
| `furnished_status` | Furnished, Unfurnished, or Semi-furnished |
| `floor_level` | Ground floor, Upper floors, Penthouse, or Basement |
| `pet_policy` | Pets allowed, No pets, Cats allowed, or Dogs allowed |
| `lease_term` | Month-to-month, 6 months, 1 year, or Long term |
| `amenities` | List of amenity strings (e.g., Pool, Gym, Parking) |
| `saved` | Whether the listing is saved as a favorite |
