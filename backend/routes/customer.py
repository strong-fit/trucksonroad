from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from database import db
from auth import get_current_user

router = APIRouter()


@router.get("/customer/inquiries")
async def customer_get_inquiries(request: Request):
    user = await get_current_user(request)
    return await db.inquiries.find({"customer_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1).to_list(200)


@router.get("/customer/inquiries/{inquiry_id}")
async def customer_get_inquiry(inquiry_id: str, request: Request):
    user = await get_current_user(request)
    doc = await db.inquiries.find_one({"id": inquiry_id, "customer_id": str(user["_id"])}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return doc


@router.get("/customer/profile")
async def customer_get_profile(request: Request):
    user = await get_current_user(request)
    return {
        "email": user["email"], "name": user.get("name", ""),
        "first_name": user.get("first_name", ""), "last_name": user.get("last_name", ""),
        "company": user.get("company", ""), "phone": user.get("phone", ""),
        "role": user.get("role", "customer"), "lang": user.get("lang", "de")
    }


@router.put("/customer/profile")
async def customer_update_profile(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    update_fields = {}
    if "lang" in body and body["lang"] in ("de", "en", "fr", "it"):
        update_fields["lang"] = body["lang"]
        await db.inquiries.update_many({"customer_id": user["_id"]}, {"$set": {"lang": body["lang"]}})
    if "first_name" in body:
        update_fields["first_name"] = body["first_name"]
    if "last_name" in body:
        update_fields["last_name"] = body["last_name"]
    if "phone" in body:
        update_fields["phone"] = body["phone"]
    if "company" in body:
        update_fields["company"] = body["company"]
    if update_fields:
        await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_fields})
    return {"message": "Updated"}


@router.put("/customer/inquiries/{inquiry_id}/confirm")
async def customer_confirm_offer(inquiry_id: str, request: Request):
    user = await get_current_user(request)
    body = await request.json()
    payment_method = body.get("payment_method", "invoice")
    inquiry = await db.inquiries.find_one({"id": inquiry_id, "customer_id": str(user["_id"])}, {"_id": 0})
    if not inquiry:
        raise HTTPException(404, "Nicht gefunden")
    if inquiry.get("status") not in ("offer_sent",):
        raise HTTPException(400, "Offerte kann nicht bestätigt werden")
    from datetime import datetime, timezone
    await db.inquiries.update_one({"id": inquiry_id}, {"$set": {
        "status": "confirmed",
        "payment_method": payment_method,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }})
    return {"message": "Offerte bestätigt", "payment_method": payment_method}


@router.get("/customer/inquiries/{inquiry_id}/offer-pdf")
async def customer_offer_pdf(inquiry_id: str, request: Request):
    user = await get_current_user(request)
    inquiry = await db.inquiries.find_one({"id": inquiry_id, "customer_id": str(user["_id"])}, {"_id": 0})
    if not inquiry:
        raise HTTPException(404, "Nicht gefunden")
    from services.pdf import generate_offer_pdf
    from services.email import get_email_t
    from starlette.responses import Response as FastAPIResponse
    pdf_bytes = generate_offer_pdf(inquiry, inquiry.get("lang", "de"))
    it = get_email_t(inquiry.get("lang", "de"))
    name = f"{inquiry.get('first_name', '')}_{inquiry.get('last_name', '')}".strip("_") or "Anfrage"
    return FastAPIResponse(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={it['pdf_offer']}_{name}.pdf"})
