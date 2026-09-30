# Skincare Product Analysis

Code for the data pipeline of a skincare product analysis project, and the first analysis stage built on top of it, claim verification. The remaining analysis stages (sentiment, recommendation) are still in progress.
 
This repository contains only the **code** (`.ipynb`). The datasets are too large for GitHub, so they live on **Google Drive**. Each folder has a `... Data Link.txt` with the Drive links. **Download the data into the folder where its `Data Link.txt` sits**, then run the notebooks in the order below.

## 📁 Folder structure
 
```
.
├── README.md
└── Code/
    ├── Data Scraping/                       
    │   ├── Scraping_Products.ipynb          # scrape product data
    │   ├── Scraping_Reviews.ipynb           # scrape review data
    │   └── Scrape Data Link.txt             # Drive links: raw products, reviews, per-category
    │
    ├── Data Preprocessing/                  
    │   ├── Data_Preprocessing.ipynb         # EDA, cleaning, text preprocessing, remove unused column
    │   ├── Ingredient_Name_Cleaning.ipynb   # fix ingredient names in the products and ingredients data
    │   └── Preprocessing Data Link.txt      # Drive links: all preprocessing output data
    │
    ├── Ingredients Manual Data Collection/  
    │    └── Ingredients Data Link.txt        # Drive links: ingredients_data (xlsx and csv) and changes
    │
    ├── Data Labeling/                       
    │   ├── Krippendorff_Alpha_Claim.ipynb      # inter-annotator reliability (Krippendorff's alpha), then fill label_final
    │   ├── Sentiment_Gold_Sampling.ipynb       # sample reviews to build the sentiment_gold template for manual labeling
    │   ├── Krippendorff_Alpha_Sentiment.ipynb  # inter-annotator reliability (Krippendorff's alpha), then fill label_final
    │   └── Labeling Data Link.txt              # Drive link: claim_gold, sentiment_gold (labeled gold standard)
    │
    └── Claim Verification/                  
        ├── Claim_Verification_EWG.ipynb       # claim verification with EWG function text
        ├── Claim_Verification_EWG_INCI.ipynb  # claim verification with EWG + INCI function text
        └── Claim Verification Data Link.txt   # Drive links: saved_data_ewg, saved_data_ewg_inci (results)  
```

## ▶️ Run order
Run the data preparation steps first. After them, the **Claim Verification** and **Sentiment Analysis** tracks both build on the preprocessed data and do not depend on each other, so they can be run in parallel. Each track is numbered on its own, starting from 1. `Data_Preprocessing.ipynb` runs in two passes (the two Data Preprocessing steps below), because the manual ingredient collection happens in between. For each step, the files to download are listed in that folder's `... Data Link.txt`, and they go into that same folder.
 
### Data Preparation
1. **Data Scraping** (`Scraping_Products.ipynb`, `Scraping_Reviews.ipynb`) — scrape the raw product and review data.
2. **Data Preprocessing, pass 1** (`Data_Preprocessing.ipynb`) — run from the top through the ingredient extraction (EDA & data cleaning, translate data, emoji handling & replacement, ingredient list extraction using LLM), then stop before the text normalization section. This produces the list of unique ingredients to collect.
3. **Ingredients Manual Data Collection** — using that list, collect `ingredients_data.xlsx` from EWG and INCIDecoder, then write the name fixes in `changes.xlsx`.
4. **Ingredient Name Cleaning** (`Ingredient_Name_Cleaning.ipynb`) — apply `changes.xlsx` to the products and `ingredients_data`, producing `ingredients_data.csv`.
5. **Data Preprocessing, pass 2** (`Data_Preprocessing.ipynb`) — run the rest from text normalization, remove the unused column, and save the preprocessed data.

### Claim Verification track
1. **Claim Gold Selection** — manually pick 50 products and put them into `claim_gold.xlsx` (the `pelabelan` tab) for the annotators to label. This is done by hand, without a notebook.
2. **Data Labeling** (`Krippendorff_Alpha_Claim.ipynb`) — after the annotators label the `pelabelan` tab, this notebook measures inter-annotator reliability with Krippendorff's alpha and, once it passes the threshold, fills `label_final` by majority vote. The result is the gold standard used to evaluate claim verification.
3. **Claim Verification** (`Claim_Verification_EWG.ipynb`, `Claim_Verification_EWG_INCI.ipynb`) — check whether each product's claimed effects are supported by its ingredients, in two variants (EWG only, and EWG + INCI). Each variant saves `claim_verification_result.csv` into its own folder, `saved_data_ewg` and `saved_data_ewg_inci`.

### Sentiment Analysis track
1. **Sentiment Gold Sampling** (`Sentiment_Gold_Sampling.ipynb`) — take a random sample of 70% of the preprocessed reviews and build `sentiment_gold.xlsx`, the empty template the annotators label manually.
2. **Manual Labeling, shared part** — reviews R00001 to R10000 are labeled by all three annotators independently in the `pelabelan` tab, so their agreement can be measured.
3. **Data Labeling** (`Krippendorff_Alpha_Sentiment.ipynb`) — measure inter-annotator reliability with Krippendorff's alpha on the reviews labeled by all three, then fill `label_final` by majority vote once it passes the threshold. The result is saved as `sentiment_gold_after_krippendorff_alpha.xlsx`, which keeps one agreed label per review and effect and drops the annotator columns.
4. **Manual Labeling, divided part** — once the reliability check passes, the labeling rules are settled, so the remaining reviews (R10001 onward) are split evenly between the three annotators and labeled straight into the `label_final` column of `sentiment_gold_after_krippendorff_alpha.xlsx`, one annotator per review, until every sampled review is done.
