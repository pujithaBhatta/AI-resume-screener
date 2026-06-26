"""
scripts/download_models.py - Download NLP Models
==================================================
Run this after pip install to download required ML models.

    python scripts/download_models.py
"""

import subprocess
import sys


def run(cmd):
    print(f"▶ Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ Done")
    else:
        print(f"  ⚠️  Warning: {result.stderr[:200]}")


print("📦 Downloading NLP models...\n")

# spaCy English model
run(f"{sys.executable} -m spacy download en_core_web_sm")

# NLTK data
import nltk
for pkg in ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']:
    try:
        nltk.download(pkg, quiet=True)
        print(f"  ✅ NLTK: {pkg}")
    except Exception as e:
        print(f"  ⚠️  NLTK {pkg}: {e}")

# Sentence Transformers (downloads automatically on first use)
print("\n📥 Pre-downloading Sentence Transformer model...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("  ✅ Sentence Transformer: all-MiniLM-L6-v2")
except Exception as e:
    print(f"  ⚠️  Sentence Transformers: {e}")
    print("     Install with: pip install sentence-transformers")

print("\n🎉 All models ready!")
