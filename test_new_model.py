
import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_DIR = Path(r"D:\verify-ai-models\ItsNotAI-v2")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_new_model.py <image_path>")
        return

    image_path = Path(sys.argv[1])

    if not image_path.is_file():
        print(f"Image not found: {image_path}")
        return

    print("Loading model. First load may take a few minutes...")

    with open(MODEL_DIR / "source_meta.json", encoding="utf-8") as file:
        meta = json.load(file)

    model = AutoModelForImageClassification.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True
    )
    processor = AutoImageProcessor.from_pretrained(
        str(MODEL_DIR),
        local_files_only=True
    )
    model.eval()

    hidden_size = meta.get("hidden_size", model.config.hidden_size)
    binary_head = nn.Sequential(
        nn.Dropout(0.1),
        nn.Linear(hidden_size, 2)
    )

    state = torch.load(
        MODEL_DIR / "binary_head.pt",
        map_location="cpu",
        weights_only=True
    )
    binary_head.load_state_dict(state)
    binary_head.eval()

    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        inputs = processor(image, return_tensors="pt")

    with torch.inference_mode():
        pixels = inputs["pixel_values"]

        if hasattr(model, "beit"):
            features = model.beit(pixels).last_hidden_state[:, 0]
        elif hasattr(model, "vit"):
            features = model.vit(pixels).last_hidden_state[:, 0]
        else:
            raise RuntimeError("Could not find the model backbone.")

        scores = torch.softmax(binary_head(features), dim=-1)[0]

    real_score = scores[0].item()
    ai_score = scores[1].item()
    verdict = "Likely real" if real_score >= ai_score else "Likely AI-generated"

    print("\n===== VERIFYAI NEW MODEL TEST =====")
    print("Image:", image_path.name)
    print("Prediction:", verdict)
    print(f"Real model score: {real_score:.4f}")
    print(f"AI model score:   {ai_score:.4f}")
    print("\nThese scores are not calibrated probabilities.")
    print("The prediction is experimental, not proof of authenticity.")


if __name__ == "__main__":
    main()
