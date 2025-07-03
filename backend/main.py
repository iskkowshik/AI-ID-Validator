from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import base64

# Import your OCR + text validation function
from ocr_validator import run_text_validation  
from template_validator import validation_score_from_base64

# Import your image classification function and model loader
from image_classifier import predict_from_base64

app = FastAPI(
    title="College ID Validator API",
    description="API for validating college ID cards using OCR and AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IDValidationRequest(BaseModel):
    user_id: str
    image_base64: str

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>College ID Validator API</title>
        </head>
        <body>
            <h1>Welcome to the College ID Validator API</h1>
            <p>Use the <code>/validate-id</code> POST endpoint to validate ID cards.</p>
            <p>Go to <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """

from fastapi.responses import JSONResponse

@app.post("/validate-id")
async def validate_id(data: IDValidationRequest):
    # --- Default values to avoid UnboundLocalError ---
    genuine_confidence = 0.0
    all_probabilities = {}
    predicted_class = "unknown"
    template_score = 0.0
    ocr_results = {"ocr_confidence": 0.0, "is_fake": True, "validation": {}, "extracted_text": ""}
    face_photo_found = False  # NEW

    try:
        # --- Image-based prediction ---
        try:
            result = predict_from_base64(data.image_base64)
            genuine_confidence = float(result.get("genuine_confidence", 0))
            all_probabilities = result.get("all_probabilities", {})
            predicted_class = max(all_probabilities, key=all_probabilities.get) if all_probabilities else "unknown"
        except Exception as e_img:
            print(f"Image prediction error: {e_img}")

        # --- Template similarity score ---
        try:
            template_score = float(validation_score_from_base64(data.image_base64))
        except Exception as e_temp:
            print(f"Template validation error: {e_temp}")

        # --- OCR Validation ---
        try:
            ocr_results = run_text_validation(data.image_base64, data.user_id)
        except Exception as e_ocr:
            print(f"OCR error: {e_ocr}")

        ocr_confidence = float(ocr_results.get("ocr_confidence", 0))
        is_fake_based_on_ocr = ocr_results.get("is_fake", True)
        face_photo_found = ocr_results.get("validation", {}).get("face_photo_found", False)  # NEW

        # --- Combined Validation Score ---
        weight_image = 0.3
        weight_ocr = 0.3
        weight_template = 0.4
        validation_score = round(
            weight_image * genuine_confidence +
            weight_ocr * ocr_confidence +
            weight_template * template_score,
            4
        )

        # --- Decision logic ---
        threshold = 0.7
        if not face_photo_found:
            label = "fake"
            status = "rejected"
            reason = "Face photo not found in ID card"
        elif ocr_confidence == 0.0 or validation_score < 0.6:
            label = "fake"
            status = "rejected"
            reason = "OCR failed completely or validation score is too low"
        elif validation_score > 0.85:
            label = "genuine"
            status = "approved"
            reason = "High confidence from all validators (image, OCR, template)"
        elif 0.6 <= validation_score <= 0.85 or ocr_confidence < 0.6:
            label = "suspicious"
            status = "manual_review"
            reason = "Moderate score or low OCR confidence"
        else:
            label = "suspicious"
            status = "manual_review"
            reason = "Uncertain case, needs manual review"

        return {
            "status": "success",
            "message": "Validation completed",
            "user_id": data.user_id,
            "validation_score": float(validation_score),
            "threshold": float(threshold),
            "label": label,
            "action": status,
            "reason": reason,
            "image_classification": {
                "predicted_class": predicted_class,
                "genuine_confidence": round(genuine_confidence, 4),
                "all_probabilities": {
                    k: round(float(v), 4) for k, v in all_probabilities.items()
                },
                "template_similarity_score": round(template_score, 4)
            },
            "text_validation": ocr_results.get("validation", {}),
            "extracted_text": ocr_results.get("extracted_text", ""),
            "ocr_confidence": round(ocr_confidence, 4),
            "is_fake_based_on_ocr": is_fake_based_on_ocr
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "status": "error",
            "message": "Unexpected error during processing",
            "user_id": data.user_id,
            "validation_score": 0.0,
            "threshold": 0.7,
            "label": "unknown",
            "action": "manual_review",
            "reason": "Exception occurred during processing",
            "image_classification": {
                "predicted_class": predicted_class,
                "genuine_confidence": round(genuine_confidence, 4),
                "all_probabilities": {
                    k: round(float(v), 4) for k, v in all_probabilities.items()
                },
                "template_similarity_score": round(template_score, 4)
            },
            "text_validation": {},
            "extracted_text": "",
            "ocr_confidence": 0.0,
            "is_fake_based_on_ocr": True
        }



@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/version")
async def version_info():
    return {
        "version": "1.0.0",
        "model": "AI ID Validator",
        "last_updated": "2025-05-20"
    }
