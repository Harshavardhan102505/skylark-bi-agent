# Skylark Drones - BI Agent Decision Log

## 1. Key Assumptions
* **Real-Time Polling:** Assumed on-demand GraphQL polling from monday.com is ideal to prevent stale data.
* **Currency Standard:** All deal values were converted to `float` numbers handling strings like `$50k` or `₹10,000`.
* **Date Parsing:** Normalized varied date formats into ISO standard (`YYYY-MM-DD`). Unparseable dates are labeled `UNKNOWN` rather than crashing the system.

## 2. Trade-offs
* **In-Memory Cleaning vs ETL Pipeline:** Chose dynamic pandas cleaning inside the API wrapper over an external DB pipeline to stay lightweight and meet the 6-hour timeline.
* **Streamlit UI vs Custom React UI:** Chose Streamlit for rapid deployment, allowing full focus on LLM tool-calling reliability.

## 3. Leadership Updates Interpretation
Interpreted "Leadership Updates" as structured executive summaries that do not just return raw numbers, but extract:
1. **Headline Metrics:** Key revenue and pipeline figures.
2. **Operational Bottlenecks:** Cross-referencing delayed Work Orders with unclosed Deals.
3. **Data Health Warning:** Flagging missing fields so executives know confidence levels.

## 4. Future Enhancements
* Implement Webhooks for instant cache invalidation.
* Add automated write-back to tag dirty records directly on monday.com.
