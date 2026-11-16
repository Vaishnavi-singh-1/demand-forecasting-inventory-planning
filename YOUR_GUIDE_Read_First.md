# Your Project Guide: Read This First

**Keep this file private.** Don't upload it to GitHub. The `README.md` is the public version.

---

## 1. Make the project yours (about 2 hours, this week)

You need to run it yourself and understand every step, because interviewers will ask about it.

1. Go to **colab.research.google.com** and sign in with Google.
2. Click **File → Upload notebook** and choose `Demand_Forecasting_Project.ipynb`.
3. Click **Runtime → Run all**. It takes about 1 minute and creates the data, the charts and the Excel file.
4. Read each step's explanation, and the code under it, slowly. Change one thing and run it again. For example:
   - Change `window=3` to `window=6` in the moving average.
   - Change the service level in the Excel file (Inventory Plan, cell B3) from 95% to 98% and watch the safety stock go up.
5. Download the `outputs/` folder (folder icon on the left), open the Excel file, and click through every sheet.
6. **Post it on GitHub:**
   - Create a free account and a new repository named `demand-forecasting-inventory-planning`.
   - Upload `README.md`, the notebook, the three `.py` files, and the `outputs/` folder.
   - **Don't upload this guide.**
7. Add the GitHub link to your resume (next to the project title) and to the "Featured" section of your LinkedIn profile.

---

## 2. Resume section (paste into Word)

```
PROJECTS
Demand Forecasting & Inventory Planning Model | Python, Excel | github.com/[you]/demand-forecasting-inventory-planning     Nov 2026
• Forecasted 6-month demand for 15 packaging SKUs from 36 months of sales history, comparing 5 methods
  (moving average, exponential smoothing, Holt-Winters, seasonal naive) to capture trend and Q4 seasonality.
• Achieved 91% forecast accuracy on a held-out test period, reducing forecast error 40% vs. a naive
  baseline (WAPE 14.9% → 8.9%), using a validation/test split to select the best method per SKU.
• Calculated safety stock and reorder points at a 95% service level, requiring 21% ($16.8K) less safety
  stock than naive forecasting; built an Excel dashboard with SUMIFS, INDEX/MATCH and scenario inputs.
```

These numbers are real outputs of the project, so you can defend every one. If you change the code and the numbers change, update the bullets to match.

---

## 3. Explain it in 60 seconds (practice out loud)

> "I built a demand-forecasting and inventory-planning model for a packaging distributor. I used 3 years of simulated monthly sales for 15 SKUs, like boxes, tape and mailers, with growth and a big Q4 holiday peak, similar to what a company like Uline sees.
>
> I compared five forecasting methods, from a simple naive forecast up to Holt-Winters, which handles trend and seasonality. To avoid overfitting, I picked the best method for each SKU on one period and measured accuracy on a later period the selection had never seen. The chosen methods hit about 91% accuracy and cut forecast error by 40% compared with the naive baseline.
>
> Then I turned the forecast into an inventory plan: safety stock and reorder points at a 95% service level, based on each SKU's forecast error and supplier lead time. Because the forecast was more accurate, the plan needed about 21% less safety stock for the same service level, which is real cash that isn't sitting on a shelf."

---

## 4. Interview questions you will get

**"Is this real data?"**
No, it's simulated. I designed it with realistic patterns (yearly growth, Q4 peak, random noise) so I could practice the full forecasting and inventory process end to end. The methods work the same on real data. Always say this honestly.

**"What is WAPE / MAPE? Why use WAPE?"**
- **MAPE** is the average percentage miss per item per month.
- **WAPE** is total units missed divided by total units sold.
- I used WAPE as the headline metric because it's weighted by volume. Missing 10% on a SKU selling 9,000 units matters more than missing 10% on one selling 180 units. MAPE also blows up when sales are small.

**"What's the naive forecast and why compare against it?"**
It says next month will equal this month. It's the simplest possible forecast, so any model worth using has to beat it.

**"What is Holt-Winters?"**
It's exponential smoothing that tracks three things: the current **level**, the **trend** (growing or shrinking), and the **seasonal** pattern (for example, December is always high). Three smoothing weights control how fast each one reacts to new data. I tuned them by trying combinations and keeping the one with the lowest error.

**"Why didn't one model win everywhere?"**
SKUs behave differently. Seasonal naive did well on stable SKUs with a clear yearly pattern. Holt-Winters did better on fast-growing SKUs like poly mailers. Gloves had almost no seasonality, so a simple naive forecast worked. That's why I chose a method per SKU.

**"How did you avoid overfitting?"**
I used separate validation and test periods:
- Trained on 2023–2024 and chose the best method using Jan–Jun 2025.
- Retrained and measured final accuracy on Jul–Dec 2025, which the selection never saw.
If I had chosen methods based on the test period, the accuracy would look better than it really is.

**"Explain safety stock and reorder point."**
- **Safety stock** is extra inventory that protects against forecast error during the supplier lead time: Z × forecast error × √(lead time). At 95%, Z is 1.645.
- **Reorder point** is when to order: expected demand during the lead time plus safety stock.
- A longer lead time or a less accurate forecast means more safety stock.

**"What would you do differently with real data?"**
- Add promotions, price changes and new-customer events as demand drivers.
- Review forecasts with sales and merchandising (the S&OP process).
- Use daily or weekly data for fast movers.
- Forecast new products from similar existing items' history ("like-item" forecasting). The Uline posting asks about new product launches, so this answer fits them well.

**"What tools would a company use?"**
Planning systems like SAP IBP, Blue Yonder, Kinaxis or o9, plus Excel and SQL for analysis. The logic in those systems is the same as in this project.

---

## 5. The percentages for your real experience (Taco Pros)

I can't write those numbers for you. They have to come from what actually happened, because interviewers ask "how did you measure that?" Estimates are fine as long as they're honest. Answer these and I'll turn them into bullets:

1. About how many purchase orders did you track per week, and how many vendors or distributors did you work with?
2. Before your tracker existed, how often did deliveries arrive late or incomplete? After you started following up, roughly how often? (For example, "about 4 late deliveries a week dropped to 1 or 2.")
3. Did you ever adjust order quantities based on usage? Did that reduce waste (spoiled produce) or running out of items? Roughly how often did each happen before and after?
4. How often did you send reports to leadership (weekly, monthly), and did they change anything because of them (switched a supplier, changed par levels)?
5. How much time did your tracker save, compared with how things were done before? (For example, "managers stopped calling vendors themselves.")

Don't use "approximately" or "~" in bullets. Write the number plainly and be ready to explain how you estimated it.
