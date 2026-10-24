# VerifyAI — AI Media Detection Platform

## Project Overview
VerifyAI is a web-based application that analyzes uploaded images and provides an experimental assessment of whether an image may be real or AI-generated.

## Features
- Image upload and analysis
- Support for JPG, JPEG, PNG, and WEBP images
- Python-based AI detection backend
- Real-versus-AI model scores
- File validation and a 10 MB upload limit
- Clear warnings about experimental results

## Technology Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python and FastAPI
- Image processing: Pillow
- AI model: ItsNotAI-v2
- Machine learning: PyTorch and Transformers

## Project Structure
- `frontend/` — Website interface
- `backend/` — API and image-analysis code
- `tests/` — Testing resources
- `reports/` — Evaluation reports
- `test_new_model.py` — Model testing script
- `evaluate_dataset.py` — Dataset evaluation script
- `compare_models.py` — Model comparison script

## Local Setup
1. Install Python 3.10 or a compatible version.
2. Install the required Python dependencies.
3. Ensure the AI model files are available at `D:\verify-ai-models\ItsNotAI-v2`, or update the model path in the backend configuration.
4. Start the backend from the project root:

   `python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`

5. In a separate terminal, start the frontend:

   `python -m http.server 5501 --bind 127.0.0.1 --directory "D:\verify ai"`

6. Open `http://127.0.0.1:5501/frontend/index.html` in a browser.
7. Check the API health endpoint at `http://127.0.0.1:8000/api/health`.

Install dependencies according to the project's verified dependency list before running the application on another computer.

## Important Limitations
VerifyAI provides experimental model outputs. Scores are not calibrated probabilities and cannot prove that an image is real or AI-generated. Predictions may be incorrect.

## Project Status
Developed as an AI media analysis web application. Test the backend, frontend, and model integration before deployment or production use.

## License
See the `LICENSE` file included with this project.
