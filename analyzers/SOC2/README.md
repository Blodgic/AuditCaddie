```bash
├── SOC2/
│   ├── hf_format_model/                      # Locally saved Hugging Face model
│   └── distilroberta_tokenizer_CADDIE_phase2/
│       ├── merges.txt
│       ├── special_tokens_map.json
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       └── vocab.json
├── src/
│   ├── main.py                # Command-line interface (predict, parse PDFs, etc.)
│   ├── model.py               # Loads HF model, performs inference
│   ├── pdf_parser.py          # Extracts text per page from PDFs to CSV
│   └── label_mapping.json     # SOC 2 label-to-index dictionary
├── data/
│   └── [Place PDFs and CSV files here]
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation file


## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/BERTGRC.git
   cd BERTGRC
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run PDF Parser to Convert Policies**
   Place your `.pdf` policy documents in the `data/` folder and run:
   ```bash
   python src/pdf_parser.py --input_dir data/ --output_file data/parsed_policies.csv
   ```

4. **Run SOC 2 Model Inference**
   ```bash
   python src/main.py predict      --input_file data/parsed_policies.csv      --output_file data/predictions.csv      --model_path SOC2/hf_format_model      --tokenizer_path SOC2/distilroberta_tokenizer_CADDIE_phase2      --label_file src/label_mapping.json
   ```

---

## Input File Format

The CSV should contain the following column:
- `Text` – required text of the policy
- `Class` – optional, preserved in output

---

## Output File

The predictions CSV will include:
- `predicted_class_1, 2, 3` – top 3 SOC 2 domain predictions
- `predicted_class_value_1, 2, 3` – label indices
- `probability_1, 2, 3` – softmax confidence scores

---

## How It Works

1. **Model + Tokenizer** are loaded from local Hugging Face directories.
2. **PDF Parser** creates CSV with `Text` per page per row.
3. **`main.py predict`** passes the CSV to `model.py` for classification.
4. Predictions are appended to the CSV and saved.

---

## Training Overview

The model is trained using synthetic policies created via RAG and Acme survey data to map policies to all 62 SOC 2 domains. It is saved with:
```python
model.save_pretrained("SOC2/hf_format_model")
tokenizer.save_pretrained("SOC2/hf_format_model")
```

This lets you run:
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
model = AutoModelForSequenceClassification.from_pretrained("SOC2/hf_format_model")
tokenizer = AutoTokenizer.from_pretrained("SOC2/hf_format_model")
```

---

## Contribution & Customization

Contributions are welcome — to add additional RAG data sources, update inference, or expand to new domains.

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

---

## License

This project is proprietary and intended for internal use only. Please do not redistribute.

---

## Contact

Brennan Lodge — blodge@blodgic.com
