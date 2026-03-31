# AI-Powered Fraud Detection System

## 1. Overview
This system is a specialized fraud detection engine designed for a parametric insurance platform. It evaluates insurance claims filed by gig workers after a disruption event (like heavy rain or a heatwave). 

The engine uses a **hybrid approach**:
1.  **Rule-Based Logic:** For clear-cut violations (duplicates, wrong city).
2.  **Mathematical Geofencing:** To verify if the worker was actually in the disaster zone.
3.  **Machine Learning (Isolation Forest):** To detect anomalous work patterns that suggest "gaming" the system.



## 2. File Structure & Responsibilities
```text
fraud_detection/
├── mock_data.py          # Simulated Database (Workers, History, Events)
├── checks/
│   ├── duplicate_check.py# Rule-based: Prevents double-dipping
│   ├── location_check.py # Math-based: Verifies GPS proximity
│   └── activity_check.py # ML-based: Analyzes work behavior patterns
├── aggregator.py         # The Decision Maker: Weighs all scores
└── fraud_detector.py     # Entry Point: Orchestrates the entire flow
```

## 3. Data Models (Inputs & Storage)

### A. The Input
To run a check, you only need two pieces of information:
*   `worker_id` (e.g., "W001")
*   `event_id` (e.g., "EVT001")

### B. Mock Data (`mock_data.py`)
In a real app, this would be a SQL database. Here, it is represented as Python dictionaries:

1.  **Worker Profile:** Contains `coords` (Lat/Lon) and `activity`.
    *   **Activity History:** A dictionary mapping the last 60 days to the number of deliveries made (`"2024-01-01": 12`). This creates a "behavioral fingerprint" for the worker.
2.  **Event Profile:** Contains the epicenter of the disruption (`center_coords`) and the `radius_km` (how far the damage reached).
3.  **Existing Claims:** A list of claims already processed. This is used to catch duplicates.



## 4. How the "Checks" Work (Internal Logic)

### 1. Duplicate Check (`duplicate_check.py`)
*   **Logic:** It iterates through the history of paid claims. 
*   **Trigger 1 (Identical):** If the worker is claiming the same event twice $\rightarrow$ **Score: 1.0 (Definite Fraud)**.
*   **Trigger 2 (Rapid Re-claim):** If a worker claims for two different events within 30 minutes $\rightarrow$ **Score: 0.8 (Highly Suspicious)**.

### 2. Location Check (`location_check.py`)
*   **Logic:** Uses the **Haversine Formula** to calculate the distance between two points on a sphere (Earth).
*   **The Calculation:** 
    *   If `distance <= radius`: **Score: 0.0 (Clean)**.
    *   If `distance > radius`: It calculates an "Overshoot Ratio." A worker 2km outside the zone gets a lower fraud score than a worker 200km away.

### 3. Activity Check (`activity_check.py`) — The ML Part
This is the most advanced check. It looks for "Ghost Workers" (people who don't work but buy insurance).

*   **Step 1: Segmentation:** It splits history into a **Baseline** (Days 1–53) and a **Pre-Event Window** (The 7 days before the claim).
*   **Step 2: Feature Engineering:** It calculates the mean, standard deviation, and "zero-work days" for these windows.
*   **Step 3: Isolation Forest (ML):** 
    *   The model "learns" the worker's normal cluster of activity.
    *   It then looks at the 7 days before the event. If those 7 days are "easy to isolate" (meaning they look nothing like the past 53 days), the model flags it as an anomaly.
*   **Patterns Detected:**
    *   *Inactive:* Worker had almost 0 deliveries before the event (buying insurance for a job they aren't doing).
    *   *Hyperactive:* Worker suddenly did 5x more work than usual (possibly account sharing or faking data to increase payout).


## 5. The Aggregation Engine (`aggregator.py`)
The system doesn't just say "Yes" or "No." It calculates a **Weighted Average Score**.

| Check | Weight | Why? |
| :--- | :--- | :--- |
| **Duplicate** | 45% | This is the most objective proof of cheating. |
| **Location** | 30% | Strong proof, but allows for slight GPS inaccuracy. |
| **Activity** | 25% | ML behavior is "softer" and used to support other flags. |

**Final Score Calculation:**
$$\text{Total Score} = (Dup \times 0.45) + (Loc \times 0.30) + (Act \times 0.25)$$

**Threshold:** If the result is **$\ge$ 0.35**, the claim is blocked for Admin Review.


## 6. Execution Flow (Call Order)

1.  **Start:** Call `run_fraud_check(worker_id, event_id)`.
2.  **Fetch:** Load `worker`, `event`, and `existing_claims` from `mock_data`.
3.  **Inspect:** 
    *   Call `check_duplicate()`.
    *   Call `check_location()`.
    *   Call `check_activity()`.
4.  **Decide:** Pass those 3 results into `aggregate()`.
5.  **Output:** Return a JSON-style dictionary with the `is_flagged` boolean and a `message` for the admin.


## 7. Integration Guide
To use this in a real insurance platform (e.g., a FastAPI backend), you would follow these steps:

### 1. Install Requirements
```bash
pip install numpy scikit-learn
```

### 2. Create an API Endpoint
You would wrap the `run_fraud_check` function in a route:
```python
@app.post("/process-claim")
def process_claim(worker_id: str, event_id: str):
    # 1. Run Fraud Detection
    assessment = run_fraud_check(worker_id, event_id)
    
    if assessment["is_flagged"]:
        return {"status": "held_for_review", "reason": assessment["message"]}
    
    # 2. If clean, proceed to Payout Logic
    return {"status": "approved", "payout": 500.00}
```

### 3. Replace Mock Data
Connect the `get_workers()` and `get_events()` functions to your real database (PostgreSQL/MongoDB) so the system analyzes real-time worker history.


## 8. Summary of Results (Test Scenarios)
*   **Scenario A (Clean):** Worker is in the city, has consistent history, and no duplicates. **Score: 0.0**.
*   **Scenario B (The Cheat):** Worker tries to claim an event they already got paid for. **Score: 0.45+ (Flagged)**.
*   **Scenario C (The Ghost):** Worker is in the city, but has 0 deliveries in the last month. ML flags "Inactivity." **Score: ~0.20** (Might not flag alone, but combined with other small issues, it will).