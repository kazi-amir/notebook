# Screening - Part 2

## 🔎 Spotting Rubric Issues 🔎

Below you will see the building blocks of a real task: task parameters, a prompt, a workspace, and the agent’s original trajectory. Review these, and then examine the rubric criteria closely.

Your task is to **identify ALL the rubric criteria** that contain one of the following issue types:

- Atomicity
- Self-containment
- Positive language
- Grading issue (incorrectly marked Present / Not Present)

There are multiple issues to find. Do not stop after identifying one or two! Make sure to label ALL of them for full credit.

For each issue you find, provide:

1. Criterion number

2. Issue type

3. (for Grading issues): The correct label

You do not need to write long explanations. A concise list is preferred.

Use this format:

- Criterion X: issue type + brief explanation of where you see it

- Criterion Y: Marked Present / Not Present, should be Not Present / Present because of brief explanation

Examples:

“Criteria 17: Atomicity issue because it validates both the report structure and the correctness of the financial calculations within the same rubric.”

“Criteria 23: Marked Present, but it should be Not Present because the trajectory never generated the required CSV file.”

**Only evaluate atomicity, self-containment, positive language, and Present/Not Present grading.**

Do not flag missing or overly specific rubrics in this question. The issues in this question are clear and unambiguous; we are not asking trick questions or looking for hidden problems!

# PROMPT

I have been thinking for a long time about investing in real estate so I can build a source of passive income that could eventually help support Sofia and Diego when they reach university. I have always had this idea in mind, but I need your help turning it into a concrete plan.

I have several properties saved on Zillow and would like you to, based on the properties priced under $170,000, record the property's full address (omit the country) and listing price, determine how much of the purchase price I could cover immediately using 50% of my current net worth, and calculate the resulting loan amount I'll need. For each property, estimate the monthly mortgage payment assuming I finance the remaining balance through a mortgage with a fixed 5.0% interest rate over 30 years. Then calculate the monthly rent I would need to charge in order to get a 10% profit of that monthly mortgage payment. Finally, show how much my total yearly income would increase after combining my salary and the rental profit. Round all calculated values to two decimal places.

Materialize all this in a file named `real_estate_investment_plan.csv` with the columns (I want these exact names): `property_address`, `listing_price`, `down_payment_coverage_pct`, `loan_amount`, `monthly_mortgage_payment`, `required_monthly_rent`, `total_salary_plus_rent`.

Finally, as a final part of this plan, I need to correctly organize the properties files. I'm attaching several folders containing property feature photos. These were sent to me by different listing agents, and I'm no longer sure which folder belongs to which property because I originally saved them using generic names (`property_1`, `property_2`), and so on. I need you to, for each selected property under $170,000, identify which folder belongs to it based on the visual features shown in the photos and rename it following the “property address - zip code” format. If a photo cannot be confidently matched to any feature from the corresponding listing, remove it from the folder and mention it in your final message along with a brief rationale. If a property folder is missing to upload, flag it to me as well in the final message.

# Download the Workspace and the Agent Original Trajectory

- **Workspace** → This is the final artifacts created by the model. Final property listings remaed are under `workspace-openclaw-7f32afde40fb (6).tar.gz\openclaw-workspace\inputs\properties\saved_listings`.

- **Trajectory** → This section contains the model’s step-by-step actions with full execution detail.

# Rubrics

1. A file named `real_estate_investment_plan.csv` is saved in the workspace. → **Present**

2. `real_estate_investment_plan.csv` contains exactly these columns: `property_address`, `listing_price`, `down_payment_coverage_pct`, `loan_amount`, `monthly_mortgage_payment`, `required_monthly_rent`, `total_salary_plus_rent`. → **Not Present**

3. The model correctly determines the user's annual salary from the email notification received. → **Not Present**

4. The model correctly concludes 50% of the user's net worth after reviewing available accounts: `Checking`, `Savings`, `Retirement`, and `Credit Card debt`. → **Present**

5. The `real_estate_investment_plan.csv` file contains a row for `415 Poss Rd, Leon Valley, TX 78240` with `listing_price` `155000`, `down_payment_coverage_pct` `4.24%`,`loan_amount` `148430`, `monthly_mortgage_payment` `796.80`, `required_monthly_rent` `876.48`, `total_salary_plus_rent` `48956.16`. → **Not Present**

6. The `real_estate_investment_plan.csv` file contains a row for `4401 Callaghan Rd, Balcones Heights, TX 78228` with `listing_price` `159900`, `down_payment_coverage_pct` `4.11%`, `loan_amount` `153330`, `monthly_mortgage_payment` `823.11`, `required_monthly_rent` `905.42`, `total_salary_plus_rent` `48987.72`. → **Present**

7. The `real_estate_investment_plan.csv` file contains a row for `142 Pleasanton Dr, Balcones Heights, TX 78201` with `listing_price` `162000`, `down_payment_coverage_pct` `4.06%`, `loan_amount` `155430`, `monthly_mortgage_payment` `834.38`, `required_monthly_rent` `917.82` and `total_salary_plus_rent` `49001.28`. → Not Present

8. The `real_estate_investment_plan.csv` file contains a row for `207 Charm Dr, Balcones Heights, TX 78201` with `listing_price` `168500`, `down_payment_coverage_pct` `3.90%`, `loan_amount` `161930`, `monthly_mortgage_payment` `869.28`, `required_monthly_rent` `956.20` and `total_salary_plus_rent` `49043.04`. → Not Present

9. In the renamed folder `415 Poss Rd - 78240`, `IMG_1099.jpg`, `IMG_1023.jpg`, and `DSC_4421.jpg` are removed as they cannot be confidently matched to features listed for the property. → Present

10. The folder originally named `property_1` is renamed to `4401 Callaghan Rd - 78228`, the folder originally named `property_` is renamed to `415 Poss Rd - 7824`, and the folder originally named `proprty_` is renamed to `142 Pleasanton Dr - 78201`. → Not Present

11. In the renamed folder `142 Pleasanton Dr - 78201`, all images are retained as each can be confidently matched to the property's listed features. → Not Present

12. In the renamed folder `142 Pleasanton Dr - 78201`, `DSC_2891.jpg` is removed as it cannot be confidently matched to the features listed for the property. → Present

13. The final user-facing message states that `207 Charm Dr, Balcones Heights, TX 78201` (listing price `$168,500`) does not have a corresponding photo folder. → Present

14. The final user-facing message reports that `IMG_1099.jpg` was removed from `415 Poss Rd - 78240`, stating that the image depicts a swimming pool, a feature not referenced anywhere in the property's listing. → Present

15. The final user-facing message reports that `DSC_4421.jpg` was removed from `415 Poss Rd - 78240`, citing wood fencing as the rationale for removal. → Present

16. The final user-facing message reports that `IMG_1023.jpg` was removed from `415 Poss Rd - 78240`, mentioning tile flooring as the rationale for removal. → Present

17. The final user-facing message reports that `IMG_2021.jpg` was removed from `4401 Callaghan Rd - 78228`, citing laminate flooring as the rationale for removal. → Present

18. The final user-facing message reports that `Screenshot_2026-01-31 185224.jpg` was removed from `4401 Callaghan Rd - 78228`, citing laminate flooring as the rationale for removal. → Present

19. The model removes photos that can be objectively associated with evaluated property features (e.g., `IMG_3121.png` from `4401 Callaghan Rd - 78228` or `IMG_6652.jpg` from `142 Pleasanton Dr - 78201`). → Negative Present

20. The model does not prioritize evidence of the property's key foreground features and instead focuses on secondary details when making decisions, as seen with `DSC_2891.jpg`. → Present