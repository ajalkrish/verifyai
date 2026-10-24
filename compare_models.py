
from pathlib import Path
from PIL import Image, ImageOps

from backend.detector import analyze_image
from test_new_model import MODEL_DIR
import test_new_model

DATASET = Path(r"D:\verify ai\tests\dataset")
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}


def predict_new(image_path):
    # Reuse the new model tester's loading and prediction logic.
    # The existing test script expects a file path, so use a
    # separate helper below for a full comparison.
    import json
    import torch
    import torch.nn as nn
    from transformers import AutoImageProcessor, AutoModelForImageClassification

    if not hasattr(predict_new, "loaded"):
        predict_new.model = AutoModelForImageClassification.from_pretrained(
            str(MODEL_DIR), local_files_only=True
        ).eval()
        predict_new.processor = AutoImageProcessor.from_pretrained(
            str(MODEL_DIR), local_files_only=True
        )
        with open(MODEL_DIR / "source_meta.json", encoding="utf-8") as f:
            meta = json.load(f)
        hidden = meta.get("hidden_size", predict_new.model.config.hidden_size)
        predict_new.head = nn.Sequential(nn.Dropout(0.1), nn.Linear(hidden, 2))
        predict_new.head.load_state_dict(torch.load(
            MODEL_DIR / "binary_head.pt", map_location="cpu", weights_only=True
        ))
        predict_new.head.eval()
        predict_new.loaded = True

    with Image.open(image_path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        inputs = predict_new.processor(im, return_tensors="pt")

    with torch.inference_mode():
        model = predict_new.model
        pixels = inputs["pixel_values"]
        if hasattr(model, "beit"):
            features = model.beit(pixels).last_hidden_state[:, 0]
        elif hasattr(model, "vit"):
            features = model.vit(pixels).last_hidden_state[:, 0]
        else:
            raise RuntimeError("Unknown model backbone")
        scores = torch.softmax(predict_new.head(features), dim=-1)[0]

    return "Likely real" if scores[0].item() >= scores[1].item() else "Likely fake"


def main():
    correct_old = wrong_old = inconclusive_old = 0
    correct_new = wrong_new = 0
    tested = 0

    for folder, expected in [
        ("real", "Likely real"),
        ("ai_generated", "Likely fake"),
    ]:
        directory = DATASET / folder
        if not directory.is_dir():
            print("Missing dataset folder:", directory)
            continue

        for path in sorted(directory.iterdir()):
            if path.suffix.lower() not in SUPPORTED:
                continue
            try:
                with Image.open(path) as im:
                    image = ImageOps.exif_transpose(im).convert("RGB")

                old = analyze_image(image.copy())["prediction"]
                new = predict_new(path)
                tested += 1

                if old == "Inconclusive":
                    inconclusive_old += 1
                elif old == expected:
                    correct_old += 1
                else:
                    wrong_old += 1

                if new == expected:
                    correct_new += 1
                else:
                    wrong_new += 1

                print(f"\n{path.name}")
                print(f"  Expected: {expected}")
                print(f"  Existing model: {old}")
                print(f"  New model:      {new}")

            except Exception as error:
                print(f"\nSKIPPED {path.name}: {error}")

    print("\n===== MODEL COMPARISON =====")
    print("Images tested:", tested)
    print("\nExisting model:")
    print("Correct:", correct_old)
    print("Wrong:", wrong_old)
    print("Inconclusive:", inconclusive_old)
    print("\nNew model:")
    print("Correct:", correct_new)
    print("Wrong:", wrong_new)

    print("\nCheck the source of every image label.")
    print("A small or unverified dataset cannot establish real-world accuracy.")


if __name__ == "__main__":
    main()
