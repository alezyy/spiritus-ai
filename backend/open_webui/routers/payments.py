import logging
import os
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from open_webui.models.users import Users
from open_webui.models.groups import Groups
from open_webui.utils.auth import get_verified_user
from open_webui.env import SRC_LOG_LEVELS
from open_webui.config import WEBUI_URL

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID")  # The ID of the subscription price

class CheckoutSessionRequest(BaseModel):
    price_id: Optional[str] = None

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    user=Depends(get_verified_user)
):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")

    price_id = request.price_id or STRIPE_PRICE_ID
    if not price_id:
        raise HTTPException(status_code=400, detail="Price ID is required")

    try:
        # Check if user already has a customer ID
        user_info = Users.get_user_by_id(user.id).info or {}
        customer_id = user_info.get("stripe_customer_id")

        checkout_session_params = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            "mode": "subscription",
            "success_url": f"{WEBUI_URL.value.rstrip('/')}/subscription?success=true",
            "cancel_url": f"{WEBUI_URL.value.rstrip('/')}/subscription?canceled=true",
            "client_reference_id": user.id,
            "metadata": {
                "user_id": user.id
            }
        }

        if customer_id:
            checkout_session_params["customer"] = customer_id
        else:
            checkout_session_params["customer_email"] = user.email

        checkout_session = stripe.checkout.Session.create(**checkout_session_params)

        return {"url": checkout_session.url}
    except Exception as e:
        log.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-portal-session")
async def create_portal_session(user=Depends(get_verified_user)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")

    user_info = Users.get_user_by_id(user.id).info or {}
    customer_id = user_info.get("stripe_customer_id")

    if not customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer found for this user")

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{WEBUI_URL.value.rstrip('/')}/subscription",
        )
        return {"url": portal_session.url}
    except Exception as e:
        log.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscription")
async def get_subscription_status(user=Depends(get_verified_user)):
    user_info = Users.get_user_by_id(user.id).info or {}
    return {
        "status": user_info.get("subscription_status", "inactive"),
        "plan": user_info.get("subscription_plan"),
        "current_period_end": user_info.get("subscription_current_period_end")
    }

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_session_completed(session)
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription)
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription)

    return {"status": "success"}

async def handle_checkout_session_completed(session):
    user_id = session.get("client_reference_id")
    customer_id = session.get("customer")
    
    if user_id:
        user = Users.get_user_by_id(user_id)
        if user:
            info = user.info or {}
            info["stripe_customer_id"] = customer_id
            
            # Fetch subscription details to update status immediately
            subscription_id = session.get("subscription")
            if subscription_id:
                try:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    info["subscription_status"] = subscription.get("status")
                    info["subscription_plan"] = subscription.get("plan", {}).get("id")
                    info["subscription_current_period_end"] = subscription.get("current_period_end")
                except Exception as e:
                    log.error(f"Error fetching subscription details: {e}")

            Users.update_user_by_id(user_id, {"info": info})

            # Add user to premium group
            try:
                # Check if group exists, if not create it
                groups = Groups.get_groups()
                premium_group = next((g for g in groups if g.name == "group_premium"), None)
                
                if not premium_group:
                    premium_group = Groups.create_groups_by_group_names(user.id, ["group_premium"])[0]
                
                Groups.add_users_to_group(premium_group.id, [user.id])
            except Exception as e:
                log.error(f"Error adding user to premium group: {e}")

async def handle_subscription_updated(subscription):
    customer_id = subscription.get("customer")
    status = subscription.get("status")
    plan_id = subscription.get("plan", {}).get("id")
    current_period_end = subscription.get("current_period_end")

    user = Users.get_user_by_stripe_customer_id(customer_id)
    if user:
        info = user.info or {}
        info["subscription_status"] = status
        info["subscription_plan"] = plan_id
        info["subscription_current_period_end"] = current_period_end
        Users.update_user_by_id(user.id, {"info": info})

        # Manage group membership
        try:
            groups = Groups.get_groups()
            premium_group = next((g for g in groups if g.name == "group_premium"), None)
            
            if status in ["active", "trialing"]:
                if not premium_group:
                    premium_group = Groups.create_groups_by_group_names(user.id, ["group_premium"])[0]
                Groups.add_users_to_group(premium_group.id, [user.id])
            else:
                if premium_group:
                    Groups.remove_users_from_group(premium_group.id, [user.id])
        except Exception as e:
            log.error(f"Error managing premium group membership: {e}")

async def handle_subscription_deleted(subscription):
    pass
