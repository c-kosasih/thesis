# Skincare Product Analysis

🌐 **Website:** https://skinsense-skincare-analysis.streamlit.app/

Code and data for SkinSense, a skincare product analysis system built on product and review data from SOCO by Sociolla, plus ingredient data from EWG Skin Deep and INCIDecoder. It currently covers data preparation, from scraping to text normalization (CODE 1 to CODE 6), claim verification (CODE 7A and CODE 8A), sentiment classification (CODE 7B and CODE 8B), the recommender system (CODE 9), the AI summary (CODE 10), and the website.

Each folder holds its notebooks together with the data they produce, so the result of every step is available without rerunning it. You don't have to run everything from the start: each notebook reads the files saved by the steps before it, so you can start from any step.

## 📁 Folder structure

```
.
├── README.md
├── .streamlit/
│   └── config.toml                             # website theme (colors and fonts)
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
│   ├── claim_gold_final.csv                    # output of CODE 7A (final labels)
│   ├── Sentiment_Gold.ipynb                    # CODE 7B: gold standard for sentiment classification
│   ├── sentiment_gold.xlsx                     # created by CODE 7B, filled in by three annotators
│   └── sentiment_gold_final.csv                # output of CODE 7B (final labels)
│
├── Claim Verification/
│   ├── Claim_Verification.ipynb                # CODE 8A: claim verification with IndoSBERT
│   └── data_after_claim_verification/          # output of CODE 8A
│       ├── claim_verification_ewg.csv
│       ├── claim_verification_ewg_inci.csv
│       └── evaluation_metrics.csv
│
├── Sentiment Classification/
│   ├── Sentiment_Classification.ipynb          # CODE 8B: multi-stage sentiment classification with IndoBERT
│   └── data_after_sentiment_classification/    # output of CODE 8B
│       ├── tuning_results.csv
│       ├── training_history.csv
│       ├── evaluation_per_stage.csv
│       ├── evaluation_per_class.csv
│       ├── evaluation_cascade.csv
│       ├── test_predictions.csv
│       └── sentiment_classification.csv
│
├── Recommender System/
│   ├── Recommender_System.ipynb                # CODE 9: verified capabilities, effect cards, and content-based filtering
│   ├── AI_Summary.ipynb                        # CODE 10: AI summary with an LLM
│   ├── data_after_recommender_system/          # output of CODE 9
│   │   ├── product_profile.csv
│   │   ├── effect_cards.csv
│   │   ├── review_examples.csv
│   │   └── recommendations.csv
│   └── data_after_ai_summary/                  # output of CODE 10
│       └── ai_summary.csv
│
└── Website/
    ├── app.py                                  # the SkinSense website (Streamlit)
    └── requirements.txt                        # packages for the website
```

## ⚙️ Before you run

- This repository stores its `.csv` and `.ipynb` files with Git LFS. Install Git LFS before cloning (`git lfs install`), otherwise those files come down as small pointer files instead of their real content.
- Use Python 3.10 with Jupyter (for example in VS Code). The notebooks use relative paths, so each notebook must run from its own folder, which is the default in VS Code and Jupyter.
- **CODE 4** and **CODE 10** call an LLM through the Groq API, so they need a Groq API key. The key is not included in this repository. Create a `.env` file next to this `README.md` with one line, `GROQ_API_KEY=your_key`, and never commit it. CODE 10 only uses the key for products that don't have a summary yet, so with the complete `ai_summary.csv` in this repository it runs without one.
- **CODE 8A** downloads the IndoSBERT model (`firqaaa/indo-sentence-bert-base`) from Hugging Face and the NLTK `punkt` data on its first run, so it needs an internet connection the first time.
- **CODE 8B** downloads IndoBERT (`indolem/indobert-base-uncased`) from Hugging Face on its first run, so it also needs an internet connection the first time. It trains on an NVIDIA GPU (on the CPU it would take days), which needs the CUDA build of PyTorch: a plain `pip install torch` on Windows installs the CPU build. RTX 50-series GPUs need a build for CUDA 12.8 or newer: `pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`. The trained models are saved in `Sentiment Classification/models/` (about 440 MB each) and are not included in this repository.

## ▶️ Run order

Every notebook reads the output of the steps before it. Only the products go through CODE 4 and CODE 5. CODE 6 reads the reviews straight from the translation output of CODE 3. CODE 7A and CODE 8A read the products and ingredients saved by CODE 6, and CODE 8A also reads the final labels from CODE 7A. CODE 7B reads the reviews and products saved by CODE 6, and CODE 8B reads the final labels from CODE 7B. CODE 9 reads the products and ingredients saved by CODE 6, the claim verification result of CODE 8A (`ewg_inci`), and the sentiment labels of CODE 8B. CODE 10 reads the product profile and effect cards saved by CODE 9, and the products and ingredients saved by CODE 6. The website reads the files of CODE 9 and CODE 10, plus the products and ingredients saved by CODE 6.

### Data Preparation
1. **Data Scraping** (CODE 1 `Scraping_Products.ipynb`, CODE 2 `Scraping_Reviews.ipynb`) — CODE 1 scrapes the product details (name, brand, description, ingredients, rating) of five categories on SOCO by Sociolla (Toner, Essence, Face Wash, Face Cream & Lotion, Sunscreen) into one CSV per category in `output_per_category/`. CODE 2 merges those files into `products_data.csv`, then scrapes every review of each product into `reviews_data.csv`. Both notebooks drive Google Chrome with Selenium.
2. **EDA, Data Cleaning, and Translation** (CODE 3 `EDA_Cleaning_and_Translation.ipynb`) — explore the raw data, then clean it: missing values, duplicates, products whose description is identical to their ingredient list, products with rating 0, non-Indonesian descriptions and reviews, products with fewer than 300 reviews, and emoji and symbols in the reviews. The result (40 products, 22,258 reviews) is saved to `data_after_cleaning/`. After that, the English words, phrases, and sentences inside the descriptions and reviews are translated into Indonesian with `facebook/nllb-200-distilled-1.3B` on CPU (brand and product names are kept as they are) and saved to `data_after_translated/`. Translating the reviews takes about **14.5 hours**, so **don't use Run All on this notebook**. The translated files are already in `data_after_translated/`.
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
10. **Claim Gold, pass 2** (CODE 7A) — Run All again. Every check in CHECK LABELING FILE must show 0. Each annotator's labels are turned into verified labels (an effect is verified when it is claimed and supported by at least one of the product's ingredients), the agreement between annotators is measured with Krippendorff's Alpha, and the final label is the majority vote (at least 2 of 3 annotators). `claim_gold_final.csv` is only saved when the alpha of the verified labels is at least 0.8.
11. **Claim Verification** (CODE 8A `Claim_Verification.ipynb`) — Run All. Using IndoSBERT (`firqaaa/indo-sentence-bert-base`) on CPU, it checks whether the effects claimed in each product description are supported by the product's ingredients. Each description is split into sentences, and every sentence is compared with an anchor for each of the five effects (the same effect definitions the annotators used) to find the claimed effects. Each term in an ingredient's function text is compared with the same anchors and supports only the effect with the highest score, as long as that score is at least 0.5. An ingredient supports every effect chosen by at least one of its terms, and a product supports an effect when at least one of its ingredients does. An effect is verified when it is both claimed and supported. The ingredient side runs twice, with EWG functions only (`ewg`) and with EWG plus INCIDecoder functions (`ewg_inci`), while everything else stays the same. Both results are compared with `claim_gold_final.csv` (precision, recall, F1, and accuracy) and saved to `data_after_claim_verification/`.



### Sentiment Classification
12. **Sentiment Gold, pass 1** (CODE 7B `Sentiment_Gold.ipynb`) — Run All. It builds the labeling file for the answer key (gold standard) of sentiment classification. From every product, 70% of the reviews of CODE 6 are sampled at random for labeling (15,579 of 22,258 reviews). The other 6,679 reviews stay unlabeled and will be predicted by the model in CODE 8B. The sample is split into a shared part of 5,000 reviews, labeled by all three annotators to measure their agreement, and the rest is divided equally so that each of those reviews is labeled by one annotator. The result is `sentiment_gold.xlsx`, with a `petunjuk` sheet with the labeling rules, a `bersama` sheet, and the sheets `anotator_1`, `anotator_2`, and `anotator_3`. Like the other labeling files, it is only created when it doesn't exist yet. On this first run the notebook stops at CHECK LABELING FILE with an error, because the `bersama` sheet is still empty.
13. **Manual Labeling** — three annotators fill in `sentiment_gold.xlsx`, following the `petunjuk` sheet. For every review, each of the five effects gets 0 (not discussed), 1 (positive), or 2 (negative). The annotators read the original review text (`review_text`), while the model in CODE 8B will read the normalized text (`review_text_normalized`).
      - **`bersama` sheet first:** all three annotators label all 5,000 reviews, each only in their own columns, without looking at the other columns or discussing the labels. Then run CODE 7B again to measure the agreement with Krippendorff's Alpha.
      - **Own sheets after that:** when the alpha of all effects is at least 0.8, each annotator labels their own sheet. If it is lower, clarify the rules in the `petunjuk` sheet, clear the `bersama` sheet, and label it again.
      - You can label gradually and rerun CODE 7B to see the progress in LABELING PROGRESS.
14. **Sentiment Gold, pass 2** (CODE 7B) — Run All again. Every check in CHECK LABELING FILE and CHECK FINAL LABEL must show 0. The final label of the `bersama` sheet is the majority vote (at least 2 of 3 annotators). When all three annotators chose a different label for an effect, that effect has no majority and is left empty. The other reviews keep the labels of the annotator who labeled them. `sentiment_gold_final.csv` is only saved when the alpha of all effects is at least 0.8 and every annotator's own sheet is complete. It holds all 22,258 reviews, with empty effect columns for the unlabeled ones. The LABEL ANALYSIS section at the end summarizes the final labels: the label counts per effect, the empty effects, the number of effects per review, and the label rates per part.
15. **Sentiment Classification** (CODE 8B `Sentiment_Classification.ipynb`) — Run All first with `TRIAL_MODE = True`. This runs every step on a small part of the data with 2 epochs and saves the result to `trial_run/`, so you can check that everything works (every check must show 0) and see how long one combination takes. Then set `TRIAL_MODE = False` and Run All again for the real run. The reviews with complete labels from CODE 7B are split into train, validation, and test (70:15:15, stratified). Each of the three stages has its own IndoBERT model (`indolem/indobert-base-uncased`, trained in FP32): stage 1 decides whether a review discusses any effect, stage 2 decides which effects it discusses (yes or no for each effect), and stage 3 decides whether each discussed effect is positive or negative, with the input `[EFEK] {efek}: {review}`. Every stage is trained with six combinations of learning rate (2e-5, 3e-5, 5e-5) and batch size (16, 32), for up to 4 epochs each. The baseline is learning rate 2e-5 with batch size 16, and the combination with the highest validation macro-F1 is chosen as the best. Training can be resumed: combinations already recorded in `tuning_results.csv` are skipped when the notebook runs again. The baseline and best models are evaluated on the test set, per stage and with the three stages combined. The best models then predict the unlabeled reviews and the empty effects, while the manual labels stay as they are. Everything is saved to `data_after_sentiment_classification/`. If the GPU runs out of memory, set `MICRO_BATCH_SIZE = 8`. The real run is already done. Training all 18 combinations took about **9.4 hours** on a GeForce GTX 1650, and the results are in `data_after_sentiment_classification/`, so there is no need to run this notebook again to use them. The trained models are not in this repository, so running it again right after cloning skips every combination (they are already recorded in `tuning_results.csv`) and then stops at CHECK TUNING with an error. To train from the start, delete `data_after_sentiment_classification/` and `models/` first.

### Recommender System
16. **Recommender System** (CODE 9 `Recommender_System.ipynb`) — Run All. It uses no model, so it finishes in a few seconds. For every product and effect, it counts the positive and negative reviews from CODE 8B (manual and predicted labels together), and an effect is rated positive when its positive reviews outnumber its negative ones. The Verified Capabilities of a product are the effects verified by CODE 8A (`ewg_inci`) that are also rated positive. Each effect card gets up to three example reviews: the number of positive and negative examples follows their percentages, manual labels come before predicted ones, reviews about that effect alone come first, and the rest is picked at random with a fixed seed. Similar products are found with content-based filtering, Match = 100 × (0.6 × cosine similarity of the Verified Capabilities + 0.3 × same category + 0.1 × same brand), among the products that have no more Moderate and High ingredients than the product being viewed, and the top 4 are kept, or fewer when not enough products pass. Every check must show 0. Everything is saved to `data_after_recommender_system/`.
17. **AI Summary** (CODE 10 `AI_Summary.ipynb`) — Run All. For every product, it builds a fact sheet from the output of CODE 9: the effects that the description claims, each with its status (a Verified Capability, not supported by the ingredients, or supported by the ingredients but not rated positive) and its review numbers, plus the number of Low, Moderate, and High ingredients and the names of the High ones. From that fact sheet only, an LLM (`openai/gpt-oss-120b` on Groq, the same as CODE 4) writes a summary of three to five sentences in Indonesian, guided by three made-up examples: the Verified Capabilities, the claims that are not Verified Capabilities and why, and the ingredient safety. Every summary is checked automatically: each part must have the right number of sentences, every number must appear in the fact sheet, every effect must be in the right part, and no ingredient other than the High ones may be named. When a check fails, the LLM is told what is wrong and writes the summary again, up to three attempts. Each summary is saved as soon as it passes, so running the notebook again skips the products that already have one and doesn't call the LLM; delete `ai_summary.csv` to make them all again. LLM output is not guaranteed to be identical between runs. Every check must show 0. The summaries are saved to `data_after_ai_summary/`.

### Website
18. **Website** (`Website/app.py`) — the SkinSense website, built with Streamlit. The catalog page lists every product with its ingredient safety and Verified Capabilities, with a search by product name or brand and filters for category and Verified Capability. When nothing matches, it says so and suggests the closest spelling. The product page shows the ingredient safety (with the ingredient names per hazard level), the Verified Capabilities, the AI summary, the five effect cards (claim checks, review percentages, and example reviews), and the similar products. The About page explains how all of this is decided. The website runs no model: it only reads the four files of CODE 9, `ai_summary.csv` of CODE 10, and `products_normalized.csv` and `ingredients_data_normalized.csv` of CODE 6 (for the SOCO link and the ingredient names). Install its packages with `python -m pip install -r Website/requirements.txt` (Streamlit 1.65.0 is the newest version that still runs on Python 3.10), then run `python -m streamlit run Website/app.py` from the folder of this `README.md`, so that the theme in `.streamlit/config.toml` is used. Writing `python -m` in both commands makes sure they use the same Python, so an older Streamlit installed in another Python can't run the website. The website opens at `http://localhost:8501`. The online version, linked at the top of this README, runs on Streamlit Community Cloud with `Website/app.py` as the main file path.
