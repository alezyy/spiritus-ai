import { WEBUI_API_BASE_URL } from '$lib/constants';

export const createCheckoutSession = async (token: string, priceId?: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            price_id: priceId
        })
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            console.log(err);
            error = err.detail;
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const createPortalSession = async (token: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/payments/create-portal-session`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            console.log(err);
            error = err.detail;
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const getSubscriptionStatus = async (token: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/payments/subscription`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            console.log(err);
            error = err.detail;
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};
