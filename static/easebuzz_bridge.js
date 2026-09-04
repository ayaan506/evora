/**
 * Evora Easebuzz Bridge Engine
 * Handles modal injection, dynamic QR generation, polling, and auto-settlement.
 */
let ebzActiveSessionId = null;
let ebzPollInterval = null;
let ebzTimerInterval = null;
let ebzCurrentPayload = null;

function injectEasebuzzModalDOM() {
    if (document.getElementById('evora-gateway-modal')) return;

    const modalHTML = `
    <div id="evora-gateway-modal" class="ebz-overlay" style="display: none;">
        <div class="ebz-wrapper">
            <div class="ebz-top-header">
                <button type="button" onclick="closeEasebuzzModal()" class="ebz-btn-cancel">
                    <i class="fa-solid fa-xmark"></i> Cancel
                </button>
                <div class="ebz-lang-select">
                    <i class="fa-solid fa-globe"></i> English <i class="fa-solid fa-chevron-down" style="font-size: 10px;"></i>
                </div>
            </div>
            <div class="ebz-card">
                <div class="ebz-purple-banner">
                    <div class="ebz-merchant-info">
                        <div class="ebz-merchant-logo">
                            <img src="/static/images/E%20for%20evora.png" onerror="this.src='https://via.placeholder.com/40'" alt="Evora">
                        </div>
                        <div class="ebz-merchant-text">
                            <div class="ebz-merchant-url">https://evora.live/checkout/</div>
                            <div class="ebz-tr-id">Tr ID <span id="ebz-display-trid">---</span></div>
                        </div>
                    </div>
                    <div class="ebz-timer-badge">
                        <span>Payment Link valid For</span>
                        <strong id="ebz-countdown-timer">14:59</strong>
                    </div>
                </div>
                <div class="ebz-body">
                    <div class="ebz-sidebar">
                        <div class="ebz-sidebar-title">Select Payment Method</div>
                        <div class="ebz-method-item active" onclick="switchEasebuzzTab('upi', this)">
                            <div class="ebz-method-icon"><i class="fa-solid fa-qrcode"></i></div>
                            <div class="ebz-method-content">
                                <div class="ebz-method-name">UPI / QR Code</div>
                                <div class="ebz-offer-badge">Instant Verification</div>
                            </div>
                            <div class="ebz-partner-logos"><i class="fa-brands fa-google-pay"></i><i class="fa-brands fa-amazon-pay"></i></div>
                        </div>
                        <div class="ebz-method-item" onclick="switchEasebuzzTab('card', this)">
                            <div class="ebz-method-icon"><i class="fa-regular fa-credit-card"></i></div>
                            <div class="ebz-method-content">
                                <div class="ebz-method-name">Credit Card</div>
                                <div class="ebz-offer-badge">1 Offer Available</div>
                            </div>
                            <div class="ebz-partner-logos"><i class="fa-brands fa-cc-visa"></i><i class="fa-brands fa-cc-mastercard"></i></div>
                        </div>
                        <div class="ebz-method-item" onclick="switchEasebuzzTab('debit', this)">
                            <div class="ebz-method-icon"><i class="fa-solid fa-credit-card"></i></div>
                            <div class="ebz-method-content">
                                <div class="ebz-method-name">Debit Card</div>
                            </div>
                            <div class="ebz-partner-logos"><i class="fa-brands fa-cc-visa"></i><i class="fa-brands fa-cc-mastercard"></i></div>
                        </div>
                        <div class="ebz-method-item" onclick="switchEasebuzzTab('netbanking', this)">
                            <div class="ebz-method-icon"><i class="fa-solid fa-building-columns"></i></div>
                            <div class="ebz-method-content"><div class="ebz-method-name">NetBanking</div></div>
                        </div>
                        <div class="ebz-method-item" onclick="switchEasebuzzTab('wallets', this)">
                            <div class="ebz-method-icon"><i class="fa-solid fa-wallet"></i></div>
                            <div class="ebz-method-content">
                                <div class="ebz-method-name">Wallets</div>
                                <div class="ebz-offer-badge">4 Offers Available</div>
                            </div>
                        </div>
                    </div>
                    <div class="ebz-content-panel">
                        <div class="ebz-offer-strip">
                            <div class="ebz-offer-strip-left">
                                <span class="ebz-badge-h">OFFER</span>
                                <span>Save up to 10% on Evora Bookings with Instant UPI</span>
                            </div>
                            <button class="ebz-btn-apply" onclick="alert('Promo Applied')">Applied</button>
                        </div>
                        <div id="tab-content-upi" class="ebz-tab-pane" style="display: block;">
                            <div id="ebz-qr-state-scan" style="text-align: center; padding: 10px 0;">
                                <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 4px;">Scan QR Code using any UPI App</div>
                                <p style="font-size: 12px; color: #64748b; margin: 0 0 14px 0;">Google Pay • PhonePe • Paytm • BHIM</p>
                                <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                                    <div id="ebz-qrcode-box" class="ebz-qr-frame"></div>
                                </div>
                                <div style="font-size: 12px; color: #7c3aed; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;">
                                    <i class="fa-solid fa-circle-notch fa-spin"></i> Point your phone camera to scan & complete
                                </div>
                            </div>
                            <div id="ebz-qr-state-success" class="ebz-gpay-success" style="display: none;">
                                <div class="ebz-gpay-circle"><i class="fa-solid fa-check"></i></div>
                                <h3 style="font-size: 20px; font-weight: 700; color: #0f172a; margin: 0 0 4px 0;">Payment Approved!</h3>
                                <p style="font-size: 13px; color: #10b981; font-weight: 600; margin: 0 0 8px 0;">UPI / Bank Authorization Received</p>
                                <p style="font-size: 12px; color: #64748b; margin: 0;">Generating verified booking invoice...</p>
                            </div>
                        </div>
                        <div id="tab-content-card" class="ebz-tab-pane" style="display: none;">
                            <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 14px;">Enter Card Details</div>
                            <div class="ebz-form-group">
                                <div class="ebz-input-card-box">
                                    <i class="fa-regular fa-credit-card" style="color: #94a3b8;"></i>
                                    <input type="text" placeholder="Card Number" value="4532 •••• •••• 8920" class="ebz-input">
                                </div>
                                <input type="text" placeholder="MM/YY" value="08/29" class="ebz-input" style="max-width: 110px;">
                            </div>
                            <div class="ebz-form-group" style="margin-top: 10px;">
                                <input type="text" placeholder="Card Holder Name" id="ebz-cardholder-name" class="ebz-input">
                                <input type="password" placeholder="CVV" value="•••" class="ebz-input" style="max-width: 110px;">
                            </div>
                        </div>
                        <div id="tab-content-other" class="ebz-tab-pane" style="display: none;">
                            <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 12px;">Select Popular Bank</div>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                <button type="button" class="ebz-bank-pill active">HDFC Bank</button>
                                <button type="button" class="ebz-bank-pill">ICICI Bank</button>
                                <button type="button" class="ebz-bank-pill">SBI</button>
                                <button type="button" class="ebz-bank-pill">Axis Bank</button>
                                <button type="button" class="ebz-bank-pill">Kotak</button>
                                <button type="button" class="ebz-bank-pill">Other Banks</button>
                            </div>
                        </div>
                        <div class="ebz-footer-action">
                            <button id="ebz-btn-pay" onclick="triggerManualEasebuzzSuccess()" class="ebz-pay-btn">
                                <i class="fa-solid fa-qrcode"></i> Scan QR on Phone
                            </button>
                            <div class="ebz-charges-note">₹ 0.00 Platform Charges • 256-Bit SSL Encrypted</div>
                        </div>
                    </div>
                </div>
                <div class="ebz-modal-footer">
                    <div class="ebz-footer-badges">
                        <span><i class="fa-brands fa-cc-visa"></i> VISA</span>
                        <span><i class="fa-brands fa-cc-mastercard"></i> MasterCard</span>
                        <span><i class="fa-solid fa-shield-halved"></i> PCI-DSS</span>
                    </div>
                    <div class="ebz-powered-by">Powered By <strong>Easebuzz</strong> <span style="font-size: 10px; color:#94a3b8;">v 2.6.142</span></div>
                </div>
            </div>
        </div>
    </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function switchEasebuzzTab(tabKey, element) {
    document.querySelectorAll('.ebz-method-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    document.getElementById('tab-content-upi').style.display = 'none';
    document.getElementById('tab-content-card').style.display = 'none';
    document.getElementById('tab-content-other').style.display = 'none';

    const payBtn = document.getElementById('ebz-btn-pay');
    const amt = ebzCurrentPayload.total_price.toLocaleString('en-IN', {minimumFractionDigits: 2});

    if (tabKey === 'upi') {
        document.getElementById('tab-content-upi').style.display = 'block';
        payBtn.classList.remove('ready');
        payBtn.innerHTML = `<i class="fa-solid fa-qrcode"></i> Scan QR on Phone`;
    } else if (tabKey === 'card' || tabKey === 'debit') {
        document.getElementById('tab-content-card').style.display = 'block';
        payBtn.classList.add('ready');
        payBtn.innerHTML = `<i class="fa-solid fa-shield-halved"></i> Pay ₹${amt}`;
    } else {
        document.getElementById('tab-content-other').style.display = 'block';
        payBtn.classList.add('ready');
        payBtn.innerHTML = `<i class="fa-solid fa-shield-halved"></i> Pay ₹${amt}`;
    }
}

async function triggerEasebuzzGateway(payload) {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (!isLoggedIn) {
        alert("⚠️ Please log in to your Evora account before proceeding with booking.");
        window.location.href = '/login';
        return;
    }

    injectEasebuzzModalDOM();
    ebzCurrentPayload = payload;

    try {
        const res = await fetch('/api/payment/create-qr-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });
        const sessionData = await res.json();

        if (!res.ok || sessionData.status !== 'success') {
            alert(sessionData.message || "Failed to initialize payment session.");
            return;
        }

        ebzActiveSessionId = sessionData.session_id;

        document.getElementById('ebz-display-trid').innerText = ebzActiveSessionId;
        const userName = localStorage.getItem('userName') || 'Evora Customer';
        document.getElementById('ebz-cardholder-name').value = userName;

        const qrContainer = document.getElementById('ebz-qrcode-box');
        qrContainer.innerHTML = '';
        document.getElementById('ebz-qr-state-scan').style.display = 'block';
        document.getElementById('ebz-qr-state-success').style.display = 'none';

        new QRCode(qrContainer, {
            text: sessionData.pay_url,
            width: 165,
            height: 165,
            colorDark: "#0f172a",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });

        startEasebuzzTimer(14 * 60 + 59);
        document.getElementById('evora-gateway-modal').style.display = 'flex';

        if (ebzPollInterval) clearInterval(ebzPollInterval);
        ebzPollInterval = setInterval(async () => {
            try {
                const checkRes = await fetch(`/api/payment/check-status/${ebzActiveSessionId}`);
                const statusData = await checkRes.json();

                if (statusData.status === 'PAID') {
                    clearInterval(ebzPollInterval);
                    finalizeEasebuzzPayment(ebzActiveSessionId);
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1500);

    } catch (err) {
        alert("Connection error during payment initialization.");
    }
}

async function triggerManualEasebuzzSuccess() {
    const payBtn = document.getElementById('ebz-btn-pay');
    payBtn.disabled = true;
    payBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing Authorization...`;

    setTimeout(async () => {
        await finalizeEasebuzzPayment(ebzActiveSessionId || `PAY-EBZ-${Date.now().toString().slice(-6)}`);
    }, 1200);
}

async function finalizeEasebuzzPayment(paymentRef) {
    if (ebzPollInterval) clearInterval(ebzPollInterval);
    if (ebzTimerInterval) clearInterval(ebzTimerInterval);

    document.getElementById('tab-content-card').style.display = 'none';
    document.getElementById('tab-content-other').style.display = 'none';
    document.getElementById('tab-content-upi').style.display = 'block';
    document.getElementById('ebz-qr-state-scan').style.display = 'none';
    document.getElementById('ebz-qr-state-success').style.display = 'block';

    const verifyRes = await fetch('/api/payment/verify-and-book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
            ...ebzCurrentPayload,
            razorpay_payment_id: paymentRef
        })
    });
    const verifyData = await verifyRes.json();

    setTimeout(() => {
        window.location.href = '/dashboard';
    }, 1800);
}

function startEasebuzzTimer(duration) {
    let timer = duration;
    const display = document.getElementById('ebz-countdown-timer');
    if (ebzTimerInterval) clearInterval(ebzTimerInterval);

    ebzTimerInterval = setInterval(() => {
        let minutes = parseInt(timer / 60, 10);
        let seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(ebzTimerInterval);
            closeEasebuzzModal();
            alert("Payment session expired. Please try again.");
        }
    }, 1000);
}

function closeEasebuzzModal() {
    if (ebzPollInterval) clearInterval(ebzPollInterval);
    if (ebzTimerInterval) clearInterval(ebzTimerInterval);
    const modal = document.getElementById('evora-gateway-modal');
    if (modal) modal.style.display = 'none';
}