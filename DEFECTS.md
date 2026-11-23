#Defects
1. checkout.py: Updates inventory before payment has been processed. This will lead to mismatch inventory because when a customer's payment declines. Inventory is already adjusted and not corrected. The fix, to adjust inventory after the system confirms it's paid.
2. cart.py: apply_discount() The discount code SAVE15 will make the total negative if the cart total is less than $15. This will mean the store "owes" money to the customer. Make sure the coupon only applies if the total is over or equal to $15.
3. repository.py: get_saved_cart() is susceptible to SQL injection. To fix this add ?.
4. repository.py: get_product() is sisceptible to SQL injection. To fix this add ?.
5. repository.py: list_orders() list every user's order. Function wants to list all user's order. To fix this, add WHERE user_id = ?
6. cart.py: add_item() can add negative quantity. To fix, check if the given quantity is greater then 0.
7. cart.py: remove_item() can remove negative quantity. To fix, check if the given quantity is greater then 0.
8. cart.py: apply_discount() discount is being discounted from the total price. So when the customer applies a 2nd discount, it will use the discounted price not the original. To fix this, assign amount = self.subtotal().
