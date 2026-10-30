# Skincare Product Analysis

Code and data for SkinSense, a skincare product analysis system built on product and review data from SOCO by Sociolla, plus ingredient data from EWG Skin Deep and INCIDecoder. It currently covers data preparation, from scraping to text normalization (CODE 1 to CODE 6), and claim verification (CODE 7A and CODE 8A). The sentiment classification and recommendation parts (CODE 7B, CODE 8B, and CODE 9) are not included yet.

Each folder holds its notebooks together with the data they produce, so the result of every step is available without rerunning it. You don't have to run everything from the start: each notebook reads the files saved by the steps before it, so you can start from any step.

## 📁 Folder structure

```
.
├── README.md
├── Data Scraping/
│   ├── Scraping_Products.ipynb                 # CODE 1: scrape product details per category
│   ├── Scraping_Reviews.ipynb                  # CODE 2: merge the categories, then scrape reviews
│   ├── output_per_category/                    # output of CODE 1 (one CSV per category)
│   │   ├── essence_20260519_101758.csv
│   │   ├── face_cream_&_lotion_20260519_141007.csv
│   │   ├── face_wash_20260519_114631.csv
│   │   ├── sunscreen_20260519_152735.csv
│   │   └── toner_20260519_095412.csv
│   ├── products_data.csv                       # output of CODE 2 (all categories merged)
│   └── reviews_data.csv                        # output of CODE 2 (raw reviews)
│
├── Data Preprocessing/
│   ├── EDA_Cleaning_and_Translation.ipynb      # CODE 3: EDA, data cleaning, translation
│   ├── Ingredient_Extraction.ipynb             # CODE 4: ingredient list extraction with an LLM
│   ├── Ingredient_Standardization.ipynb        # CODE 5: ingredient name standardization and data collection
│   ├── Text_Normalization.ipynb                # CODE 6: text normalization
│   │
│   ├── data_after_cleaning/                    # output of CODE 3 (cleaning)
│   │   ├── products_data_cleaned.csv
│   │   └── reviews_data_cleaned.csv
│   ├── data_after_translated/                  # output of CODE 3 (translation)
│   │   ├── products_data_translated.csv
│   │   └── reviews_data_translated.csv
│   ├── data_after_ingredient_extraction/       # output of CODE 4
│   │   └── products_ingredients_extracted.csv
│   ├── data_after_ingredient_standardization/  # output of CODE 5
│   │   ├── products_ingredients_standardized.csv
│   │   └── ingredients_data.csv
│   └── data_after_normalization/               # output of CODE 6 (final preprocessed data)
│       ├── products_normalized.csv
│       ├── reviews_normalized.csv
│       └── ingredients_data_normalized.csv
│
├── Ingredients Manual Data Collection/
│   └── ingredients_data_collection.xlsx        # created by CODE 5, filled in by hand
│
├── Data Labeling/
│   ├── Claim_Gold.ipynb                        # CODE 7A: gold standard for claim verification
│   ├── claim_gold.xlsx                         # created by CODE 7A, filled in by three annotators
│   └── claim_gold_final.csv                    # output of CODE 7A (final labels)
│
└── Claim Verification/
    ├── Claim_Verification.ipynb                # CODE 8A: claim verification with IndoSBERT
    └── data_after_claim_verification/          # output of CODE 8A
        ├── claim_verification_ewg.csv
        ├── claim_verification_ewg_inci.csv
        └── evaluation_metrics.csv
```

## ⚙️ Before you run

- This repository stores its `.csv` and `.ipynb` files with Git LFS. Install Git LFS before cloning (`git lfs install`), otherwise those files come down as small pointer files instead of their real content.
- Use Python 3.10 with Jupyter (for example in VS Code). The notebooks use relative paths, so each notebook must run from its own folder, which is the default in VS Code and Jupyter.
- **CODE 4** calls an LLM through the Groq API, so it needs a Groq API key. The key is not included in this repository. Create a `.env` file next to this `README.md` with one line, `GROQ_API_KEY=your_key`, and never commit it.
- **CODE 8A** downloads the IndoSBERT model (`firqaaa/indo-sentence-bert-base`) from Hugging Face and the NLTK `punkt` data on its first run, so it needs an internet connection the first time.

## ▶️ Run order

Every notebook reads the output of the steps before it. Only the products go through CODE 4 and CODE 5. CODE 6 reads the reviews straight from the translation output of CODE 3. CODE 7A and CODE 8A read the products and ingredients saved by CODE 6, and CODE 8A also reads the final labels from CODE 7A.

### Data Preparation
1. **Data Scraping** (CODE 1 `Scraping_Products.ipynb`, CODE 2 `Scraping_Reviews.ipynb`) — CODE 1 scrapes the product details (name, brand, description, ingredients, rating) of five categories on SOCO by Sociolla (Toner, Essence, Face Wash, Face Cream & Lotion, Sunscreen) into one CSV per category in `output_per_category/`. CODE 2 merges those files into `products_data.csv`, then scrapes every review of each product into `reviews_data.csv`. Both notebooks drive Google Chrome with Selenium.
2. **EDA, Data Cleaning, and Translation** (CODE 3 `EDA_Cleaning_and_Translation.ipynb`) — explore the raw data, then clean it: missing values, duplicates, products whose description is identical to their ingredient list, products with rating 0, non-Indonesian descriptions and reviews, products with fewer than 300 reviews, and emoji and symbols in the reviews. The result (40 products, 22.258 reviews) is saved to `data_after_cleaning/`. After that, the English words, phrases, and sentences inside the descriptions and reviews are translated into Indonesian with `facebook/nllb-200-distilled-1.3B` on CPU (brand and product names are kept as they are) and saved to `data_after_translated/`. Translating the reviews takes about **14.5 hours**, so **don't use Run All on this notebook**. The translated files are already in `data_after_translated/`.
3. **Ingredient Extraction** (CODE 4 `Ingredient_Extraction.ipynb`) — tidy each product's raw `ingredients` text, have an LLM (`openai/gpt-oss-120b` on Groq) split it into a list of ingredient names copied exactly as written, then check the result. Saves `data_after_ingredient_extraction/products_ingredients_extracted.csv`. LLM output is not guaranteed to be identical between runs, so after rerunning this step the collection file in step 5 may need new rows (CODE 5 lists them).
4. **Ingredient Standardization, pass 1** (CODE 5 `Ingredient_Standardization.ipynb`) — Run All. It tidies the name format, gathers the unique ingredient names, and creates `Ingredients Manual Data Collection/ingredients_data_collection.xlsx`. The Excel file is only created when it doesn't exist yet, so a filled-in file is never overwritten. Nothing is saved at this point: the SAVE cell prints "Belum disimpan" until the Excel file is complete.
5. **Ingredients Manual Data Collection** — fill in `ingredients_data_collection.xlsx` by hand, one row per extracted name.
   - **Name standardization:** correct the name in `ingredient_name` (capitalization, typo, synonym, not an ingredient, missing comma) and write the reason in `keterangan`.
   - **Data collection:** fill `function_ewg`, `hazard_level` (Low, Moderate, or High), and the two EWG URL columns from EWG Skin Deep, then `function_inci` and `ingredient_inci_url` from INCIDecoder. If an ingredient isn't on either site, write that in `catatan`.

   The full rules, with examples, are in the MANUAL DATA COLLECTION section of CODE 5. You can fill the file in gradually and rerun CODE 5 to see the progress.
6. **Ingredient Standardization, pass 2** (CODE 5) — Run All again. Every check in CHECK DATA COLLECTION FILE must show 0. Then the standard names are applied to every product's ingredient list, and the result is saved to `data_after_ingredient_standardization/` (`products_ingredients_standardized.csv` and `ingredients_data.csv`).
7. **Text Normalization** (CODE 6 `Text_Normalization.ipynb`) — Run All. It cleans the noise from the descriptions and reviews (emoji, symbols, invisible characters, styled letters, NLLB codes such as `{\cH00FFFF}`, extra spaces) and tidies the ingredient function text (separators, capital letters, duplicate items). The final data is saved to `data_after_normalization/`.

### Claim Verification
8. **Claim Gold, pass 1** (CODE 7A `Claim_Gold.ipynb`) — Run All. It builds the labeling file for the answer key (gold standard) of claim verification: `claim_gold.xlsx`, made from the 40 products and 423 ingredients of CODE 6, with a `klaim` sheet, a `bahan` sheet, and a `petunjuk` sheet with the labeling rules. Like the collection file of CODE 5, it is only created when it doesn't exist yet, so filled-in labels are never overwritten. On this first run the notebook stops at CHECK LABELING FILE with an error, because the labels are still empty.
9. **Manual Labeling** — three annotators fill in `claim_gold.xlsx`, each only in their own columns, following the `petunjuk` sheet.
   - **`klaim` sheet:** put 1 on every effect (brightening, hydrating, anti-aging, anti-acne, soothing) that the product description claims.
   - **`bahan` sheet:** put 1 on every effect that the ingredient's function supports. Ingredients without function data are greyed out and stay empty.
10. **Claim Gold, pass 2** (CODE 7A) — Run All again. Every check in CHECK LABELING FILE must show 0. Each annotator's labels are turned into verified labels (an effect is verified when it is claimed and supported by at least one of the product's ingredients), the agreement between annotators is measured with Krippendorff's Alpha, and the final label is the majority vote (at least 2 of 3 annotators). `claim_gold_final.csv` is only saved when the alpha of the verified labels is at least 0.67.
11. **Claim Verification** (CODE 8A `Claim_Verification.ipynb`) — Run All. Using IndoSBERT (`firqaaa/indo-sentence-bert-base`) on CPU, it checks whether the effects claimed in each product description are supported by the product's ingredients. Each description is split into sentences, and every sentence is compared with an anchor for each of the five effects (the same effect definitions the annotators used) to find the claimed effects. Each ingredient's function text is compared with the same anchors to find the effects it supports, and a product supports an effect when at least one of its ingredients does. An effect is verified when it is both claimed and supported. The ingredient side runs twice, with EWG functions only (`ewg`) and with EWG plus INCIDecoder functions (`ewg_inci`), while everything else stays the same. Both results are compared with `claim_gold_final.csv` (precision, recall, F1, and accuracy) and saved to `data_after_claim_verification/`.