
from pathlib import Path
from PIL import Image
from backend.detector import analyze_image

DATASET = Path(__file__).parent / "tests" / "dataset"

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

def main():
    correct = 0
    wrong = 0
    inconclusive = 0
    total = 0

    for folder, expected in [
        ("real", "Likely real"),
        ("ai_generated", "Likely fake"),
    ]:
        image_folder = DATASET / folder

        if not image_folder.exists():
            print(f"Missing folder: {image_folder}")
            continue

        for path in sorted(image_folder.iterdir()):
            if path.suffix.lower() not in SUPPORTED:
                continue

            total += 1

            try:
                with Image.open(path) as image:
                    result = analyze_image(image.copy())

                prediction = result["prediction"]

                if prediction == "Inconclusive":
                    inconclusive += 1
                    status = "INCONCLUSIVE"
                elif prediction == expected:
                    correct += 1
                    status = "CORRECT"
                else:
                    wrong += 1
                    status = "WRONG"

                print(
                    f"{path.name}: {prediction} | "
                    f"Expected: {expected} | {status}"
                )

            except Exception as error:
                total -= 1
                print(f"SKIPPED {path.name}: {error}")

    print("\n===== VERIFYAI TEST SUMMARY =====")
    print(f"Images tested: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Wrong predictions: {wrong}")
    print(f"Inconclusive predictions: {inconclusive}")

    if total:
        print(f"Correct / all tested: {correct / total * 100:.1f}%")

    decisive = correct + wrong
    if decisive:
        print(
            "Accuracy on decisive predictions: "
            f"{correct / decisive * 100:.1f}%"
        )
        print(
            "Decisive coverage: "
            f"{decisive / total * 100:.1f}%"
        )

    print(
        "\nThis is a small preliminary test, not a reliable "
        "measure of general detection accuracy."
    )

if __name__ == "__main__":
    main()
