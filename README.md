# AI-Powered Parametric Insurance Platform for Gig Workers

## 1. Overview

This project proposes an AI-driven parametric insurance platform designed to protect gig economy delivery workers from income loss caused by external disruptions such as extreme weather, pollution, and local restrictions.

The system provides **automated weekly insurance coverage**, dynamic premium pricing, real-time disruption monitoring, and instant payouts without requiring manual claims.

---

## 2. Problem Statement

Gig workers depend on daily earnings through delivery platforms. External factors such as heavy rainfall, heatwaves, flooding, and high pollution levels can significantly reduce their ability to work, leading to direct income loss.

Currently:

* There is no structured mechanism to compensate for income disruption
* Traditional insurance models are claim-based and slow
* Workers bear the full financial risk

The need is for a **real-time, automated, and scalable income protection system**.

---

## 3. Proposed Solution

We design a **parametric insurance system** where payouts are automatically triggered when predefined external conditions are met.

The system operates on a **weekly insurance model**, aligned with the earning cycle of gig workers, and uses AI for pricing, event detection, and fraud prevention.

---

## 4. System Workflow

```id="flow1"
Worker Registration
        ↓
Location and profile captured
        ↓
AI Risk & Pricing Model computes weekly premium
        ↓
Worker purchases policy
        ↓
Background scheduler monitors external conditions
        ↓
Event Engine detects disruption
        ↓
Affected workers identified
        ↓
Fraud validation performed
        ↓
Automatic payout triggered
```

---

## 5. Pricing Model (Core Innovation)

The weekly premium is dynamically calculated using a combination of predictive modeling and financial safeguards.

### 5.1 Inputs to Pricing Model

* Forecasted weather probability (rain, heat, pollution)
* Historical disruption patterns
* Worker location risk profile
* Estimated daily income of worker

---

### 5.2 Premium Calculation Logic

The premium is computed as:

```id="formula1"
Premium = Expected Loss + Platform Fee + Risk Margin
```

Where:

**Expected Loss**

```id="formula2"
Expected Loss = P(disruption) × Estimated Income Loss
```

* Probability derived from weather prediction model
* Income loss estimated from worker’s average earnings

**Platform Fee**

* Fixed operational cost component

**Risk Margin**

* Buffer to ensure system sustainability during extreme events

---

### 5.3 Dynamic Pricing Behavior

* If forecast predicts low disruption → lower premium
* If forecast predicts high disruption → higher premium
* Ensures affordability while maintaining financial viability

This creates a **balanced pricing system that minimizes loss risk for the platform**.

---

## 6. AI/ML Architecture

### 6.1 Risk & Pricing Model

* Models: Scikit-learn / XGBoost
* Output: Risk score and expected loss
* Purpose: Weekly premium calculation

---

### 6.2 Event Forecasting Model

* Predicts probability of disruption using weather data
* Inputs:

  * Rainfall forecast
  * Temperature
  * AQI levels

---

### 6.3 Event Severity Model

* Converts real-time conditions into severity score
* Used to determine payout amount

---

### 6.4 Fraud Detection Model

* Detects anomalies such as:

  * Location inconsistencies
  * Duplicate payouts
  * Inactive worker behavior

---

### 6.5 Explainability Layer

* SHAP (SHapley Additive Explanations) used to:

  * Explain premium calculation
  * Increase transparency
  * Build user trust

---

## 7. Event Engine and Automation

The event engine continuously monitors external data sources and triggers disruptions.

### Components:

* Weather API integration
* Rule-based + ML-based threshold detection
* Real-time event creation

---

### Background Processing

* Celery used for asynchronous task execution
* Redis used as message broker

Tasks include:

* Scheduled weather checks
* Event detection
* Claim triggering
* Notification handling

---

## 8. Claims and Payout System

* Fully automated claim generation
* No manual user input required

### Payout Flow

```id="flow2"
Event detected
        ↓
Eligible workers identified
        ↓
Fraud checks executed
        ↓
Payout calculated
        ↓
Transaction processed via sandbox API
```

* Payment gateway simulated using sandbox environment

---

## 9. System Architecture

### Frontend

* Next.js (Worker + Admin dashboards)
* Figma-based UI prototype integrated

### Backend

* FastAPI 
* REST-based microservice structure

### Core Services

* Policy Service
* Event Engine
* Claims Service
* Fraud Detection Service

### AI Layer

* Risk Pricing Model
* Event Forecast Model
* Severity Model
* Fraud Detection Model

### Data Layer

* SqlLite

### Infrastructure

* Celery + Redis for background jobs

---

## 10. Data Model

### Entities

* Worker
* Policy
* Event
* Claim
* Payment

### Relationships

* Worker purchases Policy
* Policy linked to Worker
* Event triggers Claim
* Claim generates Payment

---

## 11. Data Sources

* Weather Data: External APIs (e.g., OpenWeather)
* Pollution Data: AQI APIs
* Worker Data: Simulated dataset
* Delivery Activity: Mocked

---

## 12. Dashboards

### Worker Dashboard

* Active policy
* Weekly premium
* Coverage usage
* Payout history

### Admin Dashboard

* Disruption events
* Claims overview
* Risk heatmaps
* Fraud alerts

---

## 13. UI/UX Design

Our platform UI has been designed using Figma, covering multiple workflows including worker onboarding, policy management, and admin analytics.

View the complete interactive prototype here:
https://www.figma.com/proto/UuKRiV0disS98rJceBoaxu/DevTrails?node-id=1-2&t=RqRnX5P4xGej5gPn-1

---

## 14. Demo Plan

The system demonstration will include:

* Policy purchase simulation
* Triggering a disruption event (e.g., heavy rainfall)
* Automatic claim generation
* Fraud validation
* Instant payout via sandbox API

---

## 15. Future Scope

* Integration with real delivery platforms
* Advanced predictive modeling
* Multi-region scaling
* Personalized dynamic coverage

---

## 16. Conclusion

This system provides a scalable and automated insurance solution tailored for gig workers, combining AI-driven pricing, real-time event monitoring, and instant payouts to ensure financial resilience against unpredictable external disruptions.
