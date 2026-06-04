# **Real Estate Rental Valuation & Investment Analyzer**

### **AI-Powered Rental Price Prediction, ROI Analysis & Property Investment Dashboard**

This project predicts rental prices across South Africa using machine learning and provides a full financial analysis suite for property investors. It combines automated web scraping, feature engineering, ML modeling (XGBoost, Random Forest, LightGBM), and a Streamlit dashboard for interactive insights.


## **Features**

### **1. AI Rental Price Prediction**

* Trained on **5,200+ rental listings** from Pretoria
* Models implemented:

  * Linear Regression
  * Random Forest Regressor
  * XGBoost Regressor
  * LightGBM Regressor
* Best performing model: **XGBoost (MAE ≈ R2,600 & R² ≈ 0.83)**
* Features used:

  * Bedrooms
  * Bathrooms
  * Parking
  * Floor size
  * Property type (One-hot encoded)
  * Location (Target encoded)

### **2. Automated Data Pipeline**

A full ETL workflow:

#### **Extract**

* Scrapes live rental listings from Property24
* Handles pagination & dynamic HTML structures
* Saves raw JSON + cleaned CSV

#### **Transform**

* Cleans missing values
* Standardizes numerical features
* Encodes categorical columns
* Removes duplicates via listing ID

#### **Load**

* Stores dataset in CSV / SQLite for retraining
* Supports incremental updates (new listings only)


## **3. Investment Analysis Engine**

Includes calculations used by real estate investors:

### **✔ ROI (Return on Investment)**

$$
ROI = \frac{\text{Annual Net Profit}}{\text{Total Investment}} \times 100
$$


### **✔ Cap Rate**

$$
\text{Cap Rate} = \frac{\text{Net Operating Income}}{\text{Property Value}} \times 100
$$

Industry standard for measuring investment strength.


### **✔ Net Rental Return**

$$
\text{Net Rental Return} = \frac{\text{Annual Rent} - \text{Expenses}}{\text{Purchase Price}} \times 100
$$

Includes:

* levies
* maintenance
* taxes
* vacancy loss



### **✔ Expected Vacancy Adjustments**

$$
\text{Vacancy Loss} = \text{Annual Rent} \times \text{Vacancy Rate}
$$

User can adjust vacancy assumptions per suburb.


### **✔ Cashflow Calculation**

$$
\text{Cashflow} = \text{Annual Rent} - (\text{Expenses} + \text{Bond Payments})
$$

Bond payment formula:

```python
import numpy as np
np.pmt(rate/12, years*12, -loan_amount)
```


### **✔ Inflation-Adjusted Rent Projection**

$$
\text{Future Rent} = \text{Rent} \times (1 + \text{inflation})^n
$$

Shows rent growth over 5–10 years.


## **4. Interactive Streamlit Dashboard**

The app includes:

### 🔵 **Rental Price Estimator**

* Input bedrooms/bathrooms/size/location
* Predicts monthly rent
* Shows confidence & feature importance

### 🔵 **Investment Calculator**

* ROI
* Cap rate
* Cashflow
* Vacancy analysis
* Inflation impact

### 🔵 **Market Analytics**

* Average price by suburb
* Correlation heatmaps
* Top 10 highest-rent suburbs
* Size vs price scatterplots
* Feature impact (via SHAP)

### 🔵 **Property Finder**

* Scrapes sale listings
* Estimates expected rental income
* Computes ROI for each
* Ranks properties by **best investment potential**



## **Tech Stack**

### **Backend / ML**

* Python
* Pandas
* NumPy
* Scikit-learn
* XGBoost
* LightGBM
* Joblib

### **Dashboard**

* Streamlit
* Plotly
* Altair

### **Data Pipeline**

* BeautifulSoup4 / Requests
* SQLite / CSV
* Cron jobs (optional)



## Project Structure

```
real-estate-ai/
│── data/
│   ├── rentals_raw.json
│   ├── rentals_clean.csv
│── models/
│   ├── rental_model.pkl
│── src/
│   ├── scrape_rentals.py
│   ├── clean_data.py
│   ├── train_model.py
│   ├── predict.py
│── app/
│   ├── streamlit_app.py
│── README.md
│── requirements.txt
```



##  **Usage**

### **Train Model**

```bash
python src/train_model.py
```

### **Run Streamlit App**

```bash
streamlit run app/streamlit_app.py
```


## **Why This Project Matters**

Most investors rely on **intuition**, not data.
This system gives:

* realistic rental valuations
* historical pricing patterns
* objective ROI + cap rate analysis
* suburb-level insights
* investment recommendations

It replaces guesswork with **data science + machine learning**.


## **Next Improvements**

* NLP on descriptions
* Location → GPS coordinates
* Days-on-market prediction
* Sale price model
* Automatic alerts for undervalued properties
