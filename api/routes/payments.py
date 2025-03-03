# # api/routes/payments.py
# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from typing import Dict, Any

# from utils.auth import get_admin_user
# from services.payment_service import process_razorpay_webhook

# # Create router
# router = APIRouter()

# @router.post("/webhook")
# async def payment_webhook(request: Request):
#     """
#     Webhook endpoint for Razorpay payment events
#     """
#     # Get the raw request body
#     body = await request.json()
    
#     # Process the webhook
#     await process_razorpay_webhook(body)
    
#     return {"status": "ok"}

# @router.get("/stats")
# async def payment_stats(
#     admin=Depends(get_admin_user)
# ):
#     """
#     Get payment statistics (admin only)
#     """
#     from utils.db import get_db
#     from sqlalchemy.future import select, func
#     from models.payment import Payment
#     from datetime import datetime, timedelta
    
#     async with get_db() as db:
#         # Get total payments
#         total_result = await db.execute(
#             select(func.count(Payment.id), func.sum(Payment.amount))
#             .where(Payment.status == "captured")
#         )
        
#         total_count, total_amount = total_result.one()
        
#         # Get payments in last 30 days
#         thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
#         month_result = await db.execute(
#             select(func.count(Payment.id), func.sum(Payment.amount))
#             .where(
#                 Payment.status == "captured",
#                 Payment.created_at >= thirty_days_ago
#             )
#         )
        
#         month_count, month_amount = month_result.one()
        
#         # Get payments in last 7 days
#         seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
#         week_result = await db.execute(
#             select(func.count(Payment.id), func.sum(Payment.amount))
#             .where(
#                 Payment.status == "captured",
#                 Payment.created_at >= seven_days_ago
#             )
#         )
        
#         week_count, week_amount = week_result.one()
    
#     return {
#         "total_payments": total_count or 0,
#         "total_amount": (total_amount or 0) / 100,  # Convert from paise to rupees
#         "month_payments": month_count or 0,
#         "month_amount": (month_amount or 0) / 100,
#         "week_payments": week_count or 0,
#         "week_amount": (week_amount or 0) / 100,
#         "currency": "INR"
#     }


# # api/routes/payments.py
# import logging
# import json
# import hmac
# import hashlib
# import time
# from fastapi import APIRouter, HTTPException, Request, Depends, Response
# from pydantic import BaseModel
# from typing import Dict, Any, Optional
# from datetime import datetime, timedelta

# from config.settings import (
#     RAZORPAY_KEY_ID,
#     RAZORPAY_KEY_SECRET,
#     WEBHOOK_URL
# )

# logger = logging.getLogger(__name__)

# # Create router
# router = APIRouter()

# # Initialize Razorpay client
# import razorpay
# client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# class CallbackData(BaseModel):
#     razorpay_payment_id: str
#     razorpay_order_id: str
#     razorpay_signature: str
#     order_id: Optional[str] = None

# @router.get("/callback")
# async def payment_callback(
#     razorpay_payment_id: str = None,
#     razorpay_order_id: str = None,
#     razorpay_signature: str = None,
#     order_id: str = None
# ):
#     """
#     Callback endpoint for Razorpay payment completion
#     This endpoint is called by the user's browser after payment
#     """
#     try:
#         logger.info(f"Payment callback received: {razorpay_payment_id}, {razorpay_order_id}, {order_id}")
        
#         # Verify signature
#         if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
#             logger.error("Payment signature verification failed")
#             return {"status": "error", "message": "Payment verification failed"}
        
#         # Process successful payment
#         await process_successful_payment(razorpay_order_id, razorpay_payment_id)
        
#         # Redirect or return success page
#         return {"status": "success", "message": "Payment processed successfully!"}
    
#     except Exception as e:
#         logger.error(f"Error in payment callback: {str(e)}")
#         return {"status": "error", "message": "Error processing payment"}

# @router.post("/webhook/razorpay")
# async def payment_webhook(request: Request):
#     """
#     Webhook endpoint for Razorpay payment events
#     This endpoint is called by Razorpay servers for payment updates
#     """
#     try:
#         # Get webhook data
#         webhook_data = await request.json()
#         logger.info(f"Webhook data received: {json.dumps(webhook_data)}")
        
#         # Get signature from headers
#         webhook_signature = request.headers.get("X-Razorpay-Signature", "")
        
#         # Verify webhook signature
#         if not verify_webhook_signature(webhook_data, webhook_signature):
#             logger.error("Webhook signature verification failed")
#             return {"status": "error"}
        
#         # Process the webhook based on event type
#         event = webhook_data.get("event")
        
#         if event == "payment.authorized":
#             # Payment is authorized
#             payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#             order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
#             if payment_id and order_id:
#                 await process_successful_payment(order_id, payment_id)
        
#         elif event == "payment.failed":
#             # Payment failed
#             payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#             order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
#             if payment_id and order_id:
#                 await process_failed_payment(order_id, payment_id)
        
#         return {"status": "ok"}
    
#     except Exception as e:
#         logger.error(f"Error in payment webhook: {str(e)}")
#         return {"status": "error"}

# def verify_payment_signature(order_id: str, payment_id: str, razorpay_signature: str) -> bool:
#     """
#     Verify Razorpay payment signature
#     """
#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': razorpay_signature
#         })
#         return True
#     except Exception as e:
#         logger.error(f"Payment signature verification error: {str(e)}")
#         return False

# def verify_webhook_signature(webhook_data: Dict[str, Any], signature: str) -> bool:
#     """
#     Verify Razorpay webhook signature
#     """
#     try:
#         # Convert webhook_data to string
#         webhook_body = json.dumps(webhook_data, separators=(',', ':'))
        
#         # Generate expected signature
#         expected_signature = hmac.new(
#             key=RAZORPAY_KEY_SECRET.encode(),
#             msg=webhook_body.encode(),
#             digestmod=hashlib.sha256
#         ).hexdigest()
        
#         # Compare signatures
#         return hmac.compare_digest(expected_signature, signature)
#     except Exception as e:
#         logger.error(f"Webhook signature verification error: {str(e)}")
#         return False

# async def process_successful_payment(order_id: str, payment_id: str):
#     """
#     Process successful payment
#     In a real implementation, this would update the database and notify the user
#     """
#     try:
#         logger.info(f"Processing successful payment: {payment_id} for order {order_id}")
        
#         # Fetch order details from Razorpay
#         order = client.order.fetch(order_id)
        
#         # Get user information from order notes
#         telegram_id = order.get("notes", {}).get("telegram_id")
#         plan_type = order.get("notes", {}).get("plan_type")
        
#         if not telegram_id or not plan_type:
#             logger.error("Missing telegram_id or plan_type in order notes")
#             return
        
#         # In a real implementation, update database and create subscription
#         # For now, just log the information
#         logger.info(f"User {telegram_id} subscribed to plan {plan_type}")
        
#         # Notify user about successful payment
#         # This would typically be done through your notification service
#         # For demonstration, just log it
#         logger.info(f"Notifying user {telegram_id} about successful payment")
        
#         from bot.bot import get_bot_instance
#         from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
#         bot = get_bot_instance()
#         if bot:
#             try:
#                 # Get plan details
#                 from bot.handlers.payment import SUBSCRIPTION_PLANS
#                 plan_details = SUBSCRIPTION_PLANS.get(plan_type, {})
                
#                 success_text = (
#                     "🎉 *Payment Successful!*\n\n"
#                     f"Thank you for subscribing to our {plan_details.get('name', plan_type)} plan.\n"
#                     f"Your subscription is now active for {plan_details.get('duration_days', 30)} days.\n\n"
#                     "Next step: Please upload your resume to start receiving personalized job updates."
#                 )
                
#                 keyboard = InlineKeyboardMarkup([
#                     [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#                     [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#                 ])
                
#                 await bot.send_message(
#                     chat_id=int(telegram_id),
#                     text=success_text,
#                     reply_markup=keyboard,
#                     parse_mode="Markdown"
#                 )
                
#                 logger.info(f"Sent payment success notification to user {telegram_id}")
#             except Exception as e:
#                 logger.error(f"Error sending notification to user {telegram_id}: {str(e)}")
    
#     except Exception as e:
#         logger.error(f"Error processing successful payment: {str(e)}")

# async def process_failed_payment(order_id: str, payment_id: str):
#     """
#     Process failed payment
#     In a real implementation, this would update the database and notify the user
#     """
#     try:
#         logger.info(f"Processing failed payment: {payment_id} for order {order_id}")
        
#         # Fetch order details from Razorpay
#         order = client.order.fetch(order_id)
        
#         # Get user information from order notes
#         telegram_id = order.get("notes", {}).get("telegram_id")
        
#         if not telegram_id:
#             logger.error("Missing telegram_id in order notes")
#             return
        
#         # Notify user about failed payment
#         logger.info(f"Notifying user {telegram_id} about failed payment")
        
#         from bot.bot import get_bot_instance
#         from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
#         bot = get_bot_instance()
#         if bot:
#             try:
#                 failure_text = (
#                     "❌ *Payment Failed*\n\n"
#                     "Your payment was not successful. This could be due to:\n"
#                     "• Insufficient funds\n"
#                     "• Card declined by bank\n"
#                     "• Connection issues\n\n"
#                     "You can try again or contact support if you need assistance."
#                 )
                
#                 keyboard = InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Try Again", callback_data="subscription")],
#                     [InlineKeyboardButton("Contact Support", callback_data="support")]
#                 ])
                
#                 await bot.send_message(
#                     chat_id=int(telegram_id),
#                     text=failure_text,
#                     reply_markup=keyboard,
#                     parse_mode="Markdown"
#                 )
                
#                 logger.info(f"Sent payment failure notification to user {telegram_id}")
#             except Exception as e:
#                 logger.error(f"Error sending notification to user {telegram_id}: {str(e)}")
    
#     except Exception as e:
#         logger.error(f"Error processing failed payment: {str(e)}")


# # api/routes/payments.py
# import logging
# import json
# import hmac
# import hashlib
# import time
# from fastapi import APIRouter, HTTPException, Request, Depends, Response
# from pydantic import BaseModel
# from typing import Dict, Any, Optional
# from datetime import datetime, timedelta

# from config.settings import (
#     RAZORPAY_KEY_ID,
#     RAZORPAY_KEY_SECRET,
#     WEBHOOK_URL
# )

# logger = logging.getLogger(__name__)

# # Create router
# router = APIRouter()

# # Initialize Razorpay client
# import razorpay
# client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# class CallbackData(BaseModel):
#     razorpay_payment_id: str
#     razorpay_order_id: str
#     razorpay_signature: str
#     order_id: Optional[str] = None

# # Update the path to match the incoming webhook URL
# # @router.get("/webhook/razorpay")
# # @router.post("/webhook/razorpay")
# # async def payment_webhook_endpoint(
# #     request: Request,
# #     razorpay_payment_id: Optional[str] = None,
# #     razorpay_order_id: Optional[str] = None,
# #     razorpay_signature: Optional[str] = None,
# #     razorpay_payment_link_id: Optional[str] = None,
# #     razorpay_payment_link_status: Optional[str] = None,
# #     order_id: Optional[str] = None
# # ):
# #     """
# #     Combined webhook endpoint for Razorpay - handles both GET and POST requests
# #     This endpoint is called by Razorpay after payment completion or status updates
# #     """
# #     try:
# #         logger.info(f"Razorpay webhook received: Method={request.method}")
# #         logger.info(f"Query params: {dict(request.query_params)}")
        
# #         if request.method == "GET":
# #             # This is a callback from the browser
# #             logger.info(f"Payment callback received: {razorpay_payment_id}, {razorpay_order_id}, {order_id}")
            
# #             # For GET requests, check if this is a payment completion callback
# #             if razorpay_payment_id and razorpay_signature:
# #                 # Verify signature if provided
# #                 if verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
# #                     # Process successful payment
# #                     await process_successful_payment(razorpay_order_id or order_id, razorpay_payment_id)
# #                     return {"status": "success", "message": "Payment processed successfully!"}
# #                 else:
# #                     logger.error("Payment signature verification failed")
# #                     return {"status": "error", "message": "Payment verification failed"}
            
# #             # If payment_link_status is 'paid', it's a successful payment link completion
# #             elif razorpay_payment_link_status == "paid" and razorpay_payment_link_id and razorpay_payment_id:
# #                 # Process payment link success
# #                 logger.info(f"Payment link success: {razorpay_payment_link_id}, status: {razorpay_payment_link_status}")
                
# #                 # Get the order ID from the payment
# #                 try:
# #                     payment = client.payment.fetch(razorpay_payment_id)
# #                     order_id = payment.get("order_id")
                    
# #                     if order_id:
# #                         await process_successful_payment(order_id, razorpay_payment_id)
# #                         return {"status": "success", "message": "Payment processed successfully!"}
# #                 except Exception as e:
# #                     logger.error(f"Error fetching payment details: {str(e)}")
            
# #             # Return a generic success response for other GET requests
# #             return {"status": "received", "message": "Webhook received"}
        
# #         elif request.method == "POST":
# #             # This is a webhook notification from Razorpay servers
# #             try:
# #                 # Get webhook data
# #                 webhook_data = await request.json()
# #                 logger.info(f"Webhook data received: {json.dumps(webhook_data)}")
                
# #                 # Get signature from headers
# #                 webhook_signature = request.headers.get("X-Razorpay-Signature", "")
                
# #                 # Verify webhook signature
# #                 if webhook_signature and verify_webhook_signature(webhook_data, webhook_signature):
# #                     # Process the webhook based on event type
# #                     event = webhook_data.get("event")
                    
# #                     if event == "payment.authorized" or event == "payment.captured":
# #                         # Payment is authorized or captured
# #                         payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
# #                         order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
                        
# #                         if payment_id and order_id:
# #                             await process_successful_payment(order_id, payment_id)
                    
# #                     elif event == "payment.failed":
# #                         # Payment failed
# #                         payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
# #                         order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
                        
# #                         if payment_id and order_id:
# #                             await process_failed_payment(order_id, payment_id)
                    
# #                     return {"status": "ok"}
# #                 else:
# #                     logger.warning("Webhook signature verification failed or missing")
# #                     # Still return 200 OK to acknowledge receipt
# #                     return {"status": "received", "message": "Webhook received, but signature verification failed"}
                
# #             except Exception as e:
# #                 logger.error(f"Error processing webhook POST data: {str(e)}")
# #                 return {"status": "error", "message": "Error processing webhook data"}
        
# #         # Handle unsupported methods
# #         return {"status": "error", "message": "Unsupported method"}
    
# #     except Exception as e:
# #         logger.error(f"Error in webhook endpoint: {str(e)}")
# #         return {"status": "error", "message": "Error processing request"}

# # Add these additional routes to api/routes/payments.py - keep all the existing code

# # Add this function near the end of the file
# @router.post("/webhook/razorpay")
# @router.get("/webhook/razorpay")
# async def razorpay_webhook_legacy(request: Request):
#     """
#     Legacy webhook endpoint for Razorpay at /webhook/razorpay
#     This redirects to the proper endpoint
#     """
#     try:
#         logger.info(f"Received legacy webhook request: {request.url}")
        
#         # For GET requests (payment callbacks)
#         if request.method == "GET":
#             # Extract query parameters
#             params = dict(request.query_params)
#             logger.info(f"Callback params: {params}")
            
#             # Process payment
#             if "razorpay_payment_id" in params and "razorpay_signature" in params:
#                 razorpay_payment_id = params.get("razorpay_payment_id")
#                 razorpay_order_id = params.get("order_id")  # This might be different based on your setup
#                 razorpay_signature = params.get("razorpay_signature")
                
#                 # Verify signature - adapt this based on your actual parameters
#                 # Note: this might not work directly since the parameters are different
#                 # from the standard Razorpay callback
#                 try:
#                     # Handle payment verification
#                     if razorpay_payment_id and razorpay_signature:
#                         logger.info(f"Processing payment callback: {razorpay_payment_id}")
                        
#                         # Get the order ID from the payment
#                         payment = client.payment.fetch(razorpay_payment_id)
#                         order_id = payment.get("order_id")
                        
#                         if not order_id:
#                             logger.error("Order ID not found in payment")
#                             return {"status": "error", "message": "Order ID not found"}
                        
#                         # Process the payment
#                         await process_successful_payment(order_id, razorpay_payment_id)
                        
#                         # Return success HTML page
#                         html_content = """
#                         <!DOCTYPE html>
#                         <html>
#                         <head>
#                             <title>Payment Successful</title>
#                             <style>
#                                 body {
#                                     font-family: Arial, sans-serif;
#                                     text-align: center;
#                                     padding: 50px;
#                                 }
#                                 .success {
#                                     color: #4CAF50;
#                                     font-size: 24px;
#                                     margin-bottom: 20px;
#                                 }
#                                 .message {
#                                     font-size: 18px;
#                                     margin-bottom: 30px;
#                                 }
#                                 .back-button {
#                                     background-color: #4CAF50;
#                                     color: white;
#                                     padding: 12px 24px;
#                                     text-decoration: none;
#                                     font-size: 16px;
#                                     border-radius: 4px;
#                                 }
#                             </style>
#                         </head>
#                         <body>
#                             <div class="success">✅ Payment Successful!</div>
#                             <div class="message">Your subscription has been activated.</div>
#                             <div class="message">You can now return to the Telegram bot to continue.</div>
#                         </body>
#                         </html>
#                         """
#                         return Response(content=html_content, media_type="text/html")
#                 except Exception as e:
#                     logger.error(f"Error processing payment callback: {str(e)}")
            
#             return {"status": "error", "message": "Invalid callback parameters"}
        
#         # For POST requests (webhook events)
#         elif request.method == "POST":
#             # Parse the request body
#             try:
#                 webhook_data = await request.json()
#                 logger.info(f"Webhook data: {json.dumps(webhook_data)}")
                
#                 # Get signature from headers
#                 webhook_signature = request.headers.get("X-Razorpay-Signature", "")
                
#                 # Process the webhook (reuse existing function)
#                 if webhook_signature:
#                     # Verify webhook signature
#                     if verify_webhook_signature(webhook_data, webhook_signature):
#                         # Process the webhook based on event type
#                         event = webhook_data.get("event")
                        
#                         if event == "payment.authorized":
#                             # Payment is authorized
#                             payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#                             order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
                            
#                             if payment_id and order_id:
#                                 await process_successful_payment(order_id, payment_id)
                        
#                         elif event == "payment.failed":
#                             # Payment failed
#                             payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#                             order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
                            
#                             if payment_id and order_id:
#                                 await process_failed_payment(order_id, payment_id)
#                     else:
#                         logger.error("Webhook signature verification failed")
                
#                 return {"status": "ok"}
#             except Exception as e:
#                 logger.error(f"Error processing webhook data: {str(e)}")
#                 return {"status": "error", "message": "Error processing webhook"}
        
#         return {"status": "error", "method": "unsupported"}
    
#     except Exception as e:
#         logger.error(f"Error in razorpay_webhook_legacy: {str(e)}")
#         return {"status": "error"}

# # Keep the original endpoints for backward compatibility
# @router.get("/callback")
# async def payment_callback(
#     razorpay_payment_id: str = None,
#     razorpay_order_id: str = None,
#     razorpay_signature: str = None,
#     order_id: str = None
# ):
#     """Legacy callback endpoint for Razorpay payment completion"""
#     try:
#         logger.info(f"Legacy payment callback received: {razorpay_payment_id}, {razorpay_order_id}, {order_id}")
        
#         # Verify signature
#         if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
#             logger.error("Payment signature verification failed")
#             return {"status": "error", "message": "Payment verification failed"}
        
#         # Process successful payment
#         await process_successful_payment(razorpay_order_id, razorpay_payment_id)
        
#         # Redirect or return success page
#         return {"status": "success", "message": "Payment processed successfully!"}
    
#     except Exception as e:
#         logger.error(f"Error in payment callback: {str(e)}")
#         return {"status": "error", "message": "Error processing payment"}

# @router.post("/webhook/razorpay")
# async def payment_webhook(request: Request):
#     """Legacy webhook endpoint for Razorpay payment events"""
#     try:
#         # Get webhook data
#         webhook_data = await request.json()
#         logger.info(f"Legacy webhook data received: {json.dumps(webhook_data)}")
        
#         # Get signature from headers
#         webhook_signature = request.headers.get("X-Razorpay-Signature", "")
        
#         # Verify webhook signature
#         if not verify_webhook_signature(webhook_data, webhook_signature):
#             logger.error("Webhook signature verification failed")
#             return {"status": "error"}
        
#         # Process the webhook based on event type
#         event = webhook_data.get("event")
        
#         if event == "payment.authorized":
#             # Payment is authorized
#             payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#             order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
#             if payment_id and order_id:
#                 await process_successful_payment(order_id, payment_id)
        
#         elif event == "payment.failed":
#             # Payment failed
#             payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
#             order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
#             if payment_id and order_id:
#                 await process_failed_payment(order_id, payment_id)
        
#         return {"status": "ok"}
    
#     except Exception as e:
#         logger.error(f"Error in legacy payment webhook: {str(e)}")
#         return {"status": "error"}

# def verify_payment_signature(order_id: str, payment_id: str, razorpay_signature: str) -> bool:
#     """
#     Verify Razorpay payment signature
#     """
#     if not all([order_id, payment_id, razorpay_signature]):
#         logger.warning("Missing parameters for signature verification")
#         return False
    
#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': razorpay_signature
#         })
#         return True
#     except Exception as e:
#         logger.error(f"Payment signature verification error: {str(e)}")
#         return False

# def verify_webhook_signature(webhook_data: Dict[str, Any], signature: str) -> bool:
#     """
#     Verify Razorpay webhook signature
#     """
#     if not signature:
#         logger.warning("Missing webhook signature")
#         return False
    
#     try:
#         # Convert webhook_data to string
#         webhook_body = json.dumps(webhook_data, separators=(',', ':'))
        
#         # Generate expected signature
#         expected_signature = hmac.new(
#             key=RAZORPAY_KEY_SECRET.encode(),
#             msg=webhook_body.encode(),
#             digestmod=hashlib.sha256
#         ).hexdigest()
        
#         # Compare signatures
#         return hmac.compare_digest(expected_signature, signature)
#     except Exception as e:
#         logger.error(f"Webhook signature verification error: {str(e)}")
#         return False

# async def process_successful_payment(order_id: str, payment_id: str):
#     """
#     Process successful payment
#     In a real implementation, this would update the database and notify the user
#     """
#     try:
#         logger.info(f"Processing successful payment: {payment_id} for order {order_id}")
        
#         # Fetch order details from Razorpay
#         order = client.order.fetch(order_id)
        
#         # Get user information from order notes
#         telegram_id = order.get("notes", {}).get("telegram_id")
#         plan_type = order.get("notes", {}).get("plan_type")
        
#         if not telegram_id or not plan_type:
#             logger.error("Missing telegram_id or plan_type in order notes")
#             return
        
#         # In a real implementation, update database and create subscription
#         # For now, just log the information
#         logger.info(f"User {telegram_id} subscribed to plan {plan_type}")
        
#         # Notify user about successful payment
#         # This would typically be done through your notification service
#         # For demonstration, just log it
#         logger.info(f"Notifying user {telegram_id} about successful payment")
        
#         from bot.bot import get_bot_instance
#         from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
#         bot = get_bot_instance()
#         if bot:
#             try:
#                 # Get plan details
#                 from bot.handlers.payment import SUBSCRIPTION_PLANS
#                 plan_details = SUBSCRIPTION_PLANS.get(plan_type, {})
                
#                 success_text = (
#                     "🎉 *Payment Successful!*\n\n"
#                     f"Thank you for subscribing to our {plan_details.get('name', plan_type)} plan.\n"
#                     f"Your subscription is now active for {plan_details.get('duration_days', 30)} days.\n\n"
#                     "Next step: Please upload your resume to start receiving personalized job updates."
#                 )
                
#                 keyboard = InlineKeyboardMarkup([
#                     [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
#                     [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
#                 ])
                
#                 await bot.send_message(
#                     chat_id=int(telegram_id),
#                     text=success_text,
#                     reply_markup=keyboard,
#                     parse_mode="Markdown"
#                 )
                
#                 logger.info(f"Sent payment success notification to user {telegram_id}")
#             except Exception as e:
#                 logger.error(f"Error sending notification to user {telegram_id}: {str(e)}")
    
#     except Exception as e:
#         logger.error(f"Error processing successful payment: {str(e)}")

# async def process_failed_payment(order_id: str, payment_id: str):
#     """
#     Process failed payment
#     In a real implementation, this would update the database and notify the user
#     """
#     try:
#         logger.info(f"Processing failed payment: {payment_id} for order {order_id}")
        
#         # Fetch order details from Razorpay
#         order = client.order.fetch(order_id)
        
#         # Get user information from order notes
#         telegram_id = order.get("notes", {}).get("telegram_id")
        
#         if not telegram_id:
#             logger.error("Missing telegram_id in order notes")
#             return
        
#         # Notify user about failed payment
#         logger.info(f"Notifying user {telegram_id} about failed payment")
        
#         from bot.bot import get_bot_instance
#         from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
#         bot = get_bot_instance()
#         if bot:
#             try:
#                 failure_text = (
#                     "❌ *Payment Failed*\n\n"
#                     "Your payment was not successful. This could be due to:\n"
#                     "• Insufficient funds\n"
#                     "• Card declined by bank\n"
#                     "• Connection issues\n\n"
#                     "You can try again or contact support if you need assistance."
#                 )
                
#                 keyboard = InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Try Again", callback_data="subscription")],
#                     [InlineKeyboardButton("Contact Support", callback_data="support")]
#                 ])
                
#                 await bot.send_message(
#                     chat_id=int(telegram_id),
#                     text=failure_text,
#                     reply_markup=keyboard,
#                     parse_mode="Markdown"
#                 )
                
#                 logger.info(f"Sent payment failure notification to user {telegram_id}")
#             except Exception as e:
#                 logger.error(f"Error sending notification to user {telegram_id}: {str(e)}")
    
#     except Exception as e:
#         logger.error(f"Error processing failed payment: {str(e)}")

# api/routes/payments.py
import logging
import json
import hmac
import hashlib
import time
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from config.settings import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
    WEBHOOK_URL
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize Razorpay client
import razorpay
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class CallbackData(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    order_id: Optional[str] = None

@router.get("/callback")
async def payment_callback(
    razorpay_payment_id: str = None,
    razorpay_order_id: str = None,
    razorpay_signature: str = None,
    order_id: str = None
):
    """
    Callback endpoint for Razorpay payment completion
    This endpoint is called by the user's browser after payment
    """
    try:
        logger.info(f"Payment callback received: {razorpay_payment_id}, {razorpay_order_id}, {order_id}")
        
        # Verify signature if all parameters are present
        if razorpay_payment_id and razorpay_order_id and razorpay_signature:
            if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
                logger.error("Payment signature verification failed")
                return {"status": "error", "message": "Payment verification failed"}
            
            # Process successful payment
            await process_successful_payment(razorpay_order_id, razorpay_payment_id)
        
        # Redirect or return success page
        return {"status": "success", "message": "Payment processed successfully!"}
    
    except Exception as e:
        logger.error(f"Error in payment callback: {str(e)}")
        return {"status": "error", "message": "Error processing payment"}

# Add this route to match what Razorpay is calling
@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):
    """
    Webhook endpoint for Razorpay payment events
    This endpoint is called by Razorpay servers for payment updates
    """
    try:
        # Get webhook data
        webhook_data = await request.json()
        logger.info(f"Webhook data received: {json.dumps(webhook_data)}")
        
        # Get signature from headers
        webhook_signature = request.headers.get("X-Razorpay-Signature", "")
        
        # Verify webhook signature
        if not verify_webhook_signature(webhook_data, webhook_signature):
            logger.error("Webhook signature verification failed")
            return {"status": "error"}
        
        # Process the webhook based on event type
        event = webhook_data.get("event")
        
        if event == "payment.authorized":
            # Payment is authorized
            payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
            order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
            if payment_id and order_id:
                await process_successful_payment(order_id, payment_id)
        
        elif event == "payment.failed":
            # Payment failed
            payment_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
            order_id = webhook_data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
            
            if payment_id and order_id:
                await process_failed_payment(order_id, payment_id)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error in payment webhook: {str(e)}")
        return {"status": "error"}

# Also add this route to match the GET request from Razorpay
@router.get("/webhook/razorpay")
async def razorpay_get_webhook(
    request: Request,
    order_id: Optional[str] = None,
    razorpay_payment_id: Optional[str] = None,
    razorpay_payment_link_id: Optional[str] = None,
    razorpay_payment_link_reference_id: Optional[str] = None,
    razorpay_payment_link_status: Optional[str] = None,
    razorpay_signature: Optional[str] = None
):
    """
    GET webhook endpoint for Razorpay payment link redirect
    """
    try:
        logger.info(f"GET webhook received with params: {request.query_params}")
        
        # If payment was successful
        if razorpay_payment_link_status == "paid" and razorpay_payment_id and order_id:
            logger.info(f"Payment successful for order {order_id}, payment {razorpay_payment_id}")
            
            # Process the successful payment
            await process_successful_payment(order_id, razorpay_payment_id)
            
            # Return a success page (in production, this would redirect to a success page)
            return {
                "status": "success", 
                "message": "Payment successful! You can now return to the Telegram bot."
            }
        
        return {"status": "pending", "message": "Payment status pending."}
    
    except Exception as e:
        logger.error(f"Error in GET webhook: {str(e)}")
        return {"status": "error", "message": f"Error processing payment: {str(e)}"}

# Keep the rest of your code as is...
@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    Legacy webhook endpoint - keep for backward compatibility
    """
    return await razorpay_webhook(request)

def verify_payment_signature(order_id: str, payment_id: str, razorpay_signature: str) -> bool:
    """
    Verify Razorpay payment signature
    """
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        })
        return True
    except Exception as e:
        logger.error(f"Payment signature verification error: {str(e)}")
        return False

def verify_webhook_signature(webhook_data: Dict[str, Any], signature: str) -> bool:
    """
    Verify Razorpay webhook signature
    """
    try:
        # Convert webhook_data to string
        webhook_body = json.dumps(webhook_data, separators=(',', ':'))
        
        # Generate expected signature
        expected_signature = hmac.new(
            key=RAZORPAY_KEY_SECRET.encode(),
            msg=webhook_body.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Webhook signature verification error: {str(e)}")
        return False

async def process_successful_payment(order_id: str, payment_id: str):
    """
    Process successful payment
    In a real implementation, this would update the database and notify the user
    """
    try:
        logger.info(f"Processing successful payment: {payment_id} for order {order_id}")
        
        # Fetch order details from Razorpay
        order = client.order.fetch(order_id)
        
        # Get user information from order notes
        telegram_id = order.get("notes", {}).get("telegram_id")
        plan_type = order.get("notes", {}).get("plan_type")
        
        if not telegram_id or not plan_type:
            logger.error("Missing telegram_id or plan_type in order notes")
            return
        
        # In a real implementation, update database and create subscription
        # For now, just log the information
        logger.info(f"User {telegram_id} subscribed to plan {plan_type}")
        
        # Notify user about successful payment
        # This would typically be done through your notification service
        # For demonstration, just log it
        logger.info(f"Notifying user {telegram_id} about successful payment")
        
        from bot.bot import get_bot_instance
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
        bot = get_bot_instance()
        if bot:
            try:
                # Get plan details
                from bot.handlers.payment import SUBSCRIPTION_PLANS
                plan_details = SUBSCRIPTION_PLANS.get(plan_type, {})
                
                success_text = (
                    "🎉 *Payment Successful!*\n\n"
                    f"Thank you for subscribing to our {plan_details.get('name', plan_type)} plan.\n"
                    f"Your subscription is now active for {plan_details.get('duration_days', 30)} days.\n\n"
                    "Next step: Please upload your resume to start receiving personalized job updates."
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📤 Upload Resume", callback_data="upload_resume")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_main")]
                ])
                
                await bot.send_message(
                    chat_id=int(telegram_id),
                    text=success_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                
                logger.info(f"Sent payment success notification to user {telegram_id}")
            except Exception as e:
                logger.error(f"Error sending notification to user {telegram_id}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")

async def process_failed_payment(order_id: str, payment_id: str):
    """
    Process failed payment
    In a real implementation, this would update the database and notify the user
    """
    try:
        logger.info(f"Processing failed payment: {payment_id} for order {order_id}")
        
        # Fetch order details from Razorpay
        order = client.order.fetch(order_id)
        
        # Get user information from order notes
        telegram_id = order.get("notes", {}).get("telegram_id")
        
        if not telegram_id:
            logger.error("Missing telegram_id in order notes")
            return
        
        # Notify user about failed payment
        logger.info(f"Notifying user {telegram_id} about failed payment")
        
        from bot.bot import get_bot_instance
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        
        bot = get_bot_instance()
        if bot:
            try:
                failure_text = (
                    "❌ *Payment Failed*\n\n"
                    "Your payment was not successful. This could be due to:\n"
                    "• Insufficient funds\n"
                    "• Card declined by bank\n"
                    "• Connection issues\n\n"
                    "You can try again or contact support if you need assistance."
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Try Again", callback_data="subscription")],
                    [InlineKeyboardButton("Contact Support", callback_data="support")]
                ])
                
                await bot.send_message(
                    chat_id=int(telegram_id),
                    text=failure_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                
                logger.info(f"Sent payment failure notification to user {telegram_id}")
            except Exception as e:
                logger.error(f"Error sending notification to user {telegram_id}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error processing failed payment: {str(e)}")