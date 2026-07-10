# Named Constants to replace magic numbers
TOPPING_PRICE = 1.5
LONG_DELIVERY_THRESHOLD = 5
LONG_DELIVERY_FEE = 5
STANDARD_DELIVERY_FEE = 2

# Dictionary to map pizza sizes to their base prices, removing nested if/else logic
PIZZA_BASE_PRICES = {
    "S": 10,
    "M": 15,
    "L": 20
}

def calculate_pizza_price(pizza_size, num_toppings, delivery_distance):
    # Retrieve base price using the dictionary
    price = PIZZA_BASE_PRICES.get(pizza_size, 0)
    
    # Calculate topping costs
    if num_toppings > 0:
        price += (num_toppings * TOPPING_PRICE)
        
    # Calculate delivery fees
    if delivery_distance > LONG_DELIVERY_THRESHOLD:
        price += LONG_DELIVERY_FEE
    else:
        price += STANDARD_DELIVERY_FEE
        
    return price
