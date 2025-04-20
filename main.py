from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

app = Flask(__name__)
DATA_FILE = "offers.json"

# تحميل العروض
def load_offers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# حفظ العروض
def save_offers(offers):
    with open(DATA_FILE, "w") as f:
        json.dump(offers, f, indent=4)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    media_url = request.values.get("MediaUrl0", "")  # صورة إن وجدت

    offers = load_offers()
    response = MessagingResponse()
    msg = response.message()

    # أوامر البداية
    if incoming_msg.lower() in ["start", "السلام عليكم", "مرحبا", "hi", "hello"]:
        msg.body("أهلاً بك في *بورصة كردستان لمشتقات النفط*.\nاكتب (بيع) لنشر عرضك أو (شراء) لعرض العروض المتوفرة.")
    
    elif incoming_msg.lower() == "بيع":
        msg.body("أرسل تفاصيل العرض بهذا الشكل:\n\nنوع المنتج:\nالكمية (طن):\nالسعر:\nاسم التاجر:\n\n(يمكنك إرفاق صورة للمنتج)")

    elif incoming_msg.lower() == "شراء":
        if not offers:
            msg.body("لا توجد عروض حالياً.")
        else:
            reply = "*العروض الحالية:*\n"
            for idx, offer in enumerate(offers, 1):
                reply += f"\n{idx}. {offer['details']}\nالتاجر: {offer['seller']}"
                if offer["image"]:
                    reply += f"\nصورة: {offer['image']}"
                reply += "\n"
            msg.body(reply)

    # استلام عرض
    elif "نوع المنتج" in incoming_msg and "الكمية" in incoming_msg and "السعر" in incoming_msg:
        new_offer = {
            "details": incoming_msg,
            "seller": sender,
            "image": media_url if media_url else ""
        }
        offers.append(new_offer)
        save_offers(offers)
        msg.body("تم استلام عرضك وسيتم عرضه للمشترين.")

    else:
        msg.body("يرجى اختيار (بيع) أو (شراء) أو إرسال تفاصيل عرضك بالشكل الصحيح.")

    return str(response)

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
