"""
FACE VERIFICATION MODEL (IMAGE ↔ IMAGE)
--------------------------------------
Verifies:
- Face in an uploaded image matches face on citizenship ID

Used for:
- Signed PDF photo verification
- Image-based identity confirmation
- Guarantor image verification (optional)

NO audio
NO speech
NO liveness (hackathon scope)

Uses:
- DeepFace (ArcFace)
"""

import os

# =========================
# CONFIG
# =========================

FACE_MODEL = "ArcFace"
DETECTOR_BACKEND = "opencv"


# =========================
# FACE MATCH FUNCTION
# =========================

def verify_face_identity(
    image_path: str,
    citizenship_image_path: str,
) -> dict:
    """
    Compare face from uploaded image with citizenship ID image
    """
    from deepface import DeepFace # Deferred import

    if not os.path.exists(image_path):
        raise Exception("Uploaded image not found")

    if not os.path.exists(citizenship_image_path):
        raise Exception("Citizenship image not found")

    try:
        result = DeepFace.verify(
            img1_path=image_path,
            img2_path=citizenship_image_path,
            model_name=FACE_MODEL,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True,
        )

        verified = result["verified"]
        distance = result["distance"]
        threshold = result["threshold"]

        print("\n[DEBUG] FACE VERIFICATION (IMAGE)")
        print(f"  Verified:  {verified}")
        print(f"  Distance:  {distance:.4f}")
        print(f"  Threshold: {threshold:.4f}")

        return {
            "face_match": verified,
            "distance": distance,
            "threshold": threshold,
            "final_status": "APPROVED" if verified else "REJECTED",
        }

    except ValueError as e:
        # No face detected / poor image
        print(f"[DEBUG] Face detection failed: {e}")
        return {
            "face_match": False,
            "final_status": "REJECTED",
            "reason": "Face not detected clearly",
        }

    except Exception as e:
        print(f"[DEBUG] Face verification error: {e}")
        return {
            "face_match": False,
            "final_status": "REJECTED",
            "reason": str(e),
        }


# =========================
# LOCAL TESTING
# =========================

if __name__ == "__main__":
    result = verify_face_identity(
        image_path="signed_photo.jpg",
        citizenship_image_path="citizenship.jpg",
    )

    print("FACE VERIFICATION RESULT:")
    print(result)
