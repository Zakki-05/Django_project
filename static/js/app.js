document.addEventListener("DOMContentLoaded", () => {
    
    // Low-impact Tilt effect for Glass cards
    const cards = document.querySelectorAll(".glass-card");
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg)`;
        });
    });

    // Patient Dashboard Logic
    const patientDashboard = document.getElementById("patient-dashboard");
    if (patientDashboard) {
        let isActivating = false;
        
        let previousStatus = null;

        const playAlarm = () => {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                const buzz = (time) => {
                    const oscillator = audioCtx.createOscillator();
                    const gainNode = audioCtx.createGain();
                    oscillator.type = 'square'; // More buzzer-like
                    oscillator.frequency.setValueAtTime(440, time);
                    
                    gainNode.gain.setValueAtTime(0, time);
                    gainNode.gain.linearRampToValueAtTime(0.3, time + 0.05);
                    gainNode.gain.linearRampToValueAtTime(0, time + 0.4);
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(audioCtx.destination);
                    oscillator.start(time);
                    oscillator.stop(time + 0.5);
                };

                // Play 3 buzzes
                const now = audioCtx.currentTime;
                buzz(now);
                buzz(now + 0.6);
                buzz(now + 1.2);
                
                if ("vibrate" in navigator) {
                    navigator.vibrate([400, 200, 400, 200, 400]);
                }
            } catch (e) {
                console.error("Could not play alarm:", e);
            }
        };

        const showTurnNotification = () => {
            const overlay = document.createElement('div');
            overlay.innerHTML = `
                <div style="position:fixed; top:0; left:0; width:100%; height:100%; 
                            background:rgba(0,0,0,0.9); z-index:9999; display:flex; 
                            flex-direction:column; align-items:center; justify-content:center;
                            color:white; text-align:center; padding:2rem; backdrop-filter:blur(10px);">
                    <div style="font-size:5rem; color:var(--accent); margin-bottom:1rem;">
                        <i class="fa-solid fa-bell-concierge fa-bounce"></i>
                    </div>
                    <h1 style="font-size:3rem; font-weight:900; margin-bottom:1rem; color:white;">IT'S YOUR TURN!</h1>
                    <p style="font-size:1.5rem; margin-bottom:2rem; color:var(--text-muted);">Please proceed to the consultation room.</p>
                    <button id="close-notif" class="btn btn-primary" style="padding:1rem 3rem; font-size:1.2rem;">OK, I'm Going</button>
                </div>
            `;
            document.body.appendChild(overlay);
            document.getElementById('close-notif').onclick = () => {
                overlay.remove();
            };
        };

        const updateStatusUI = (data) => {
            if (data.serving !== undefined) {
                const el = document.getElementById('serving-token');
                if (el) el.innerText = data.serving;
            }
            if (data.estimated_wait !== undefined) {
                const el = document.getElementById('est-wait-time');
                if (el) el.innerText = `${data.estimated_wait} min`;
            }
            if (data.waiting_count !== undefined) {
                const el = document.getElementById('waiting-count');
                if (el) el.innerText = data.waiting_count;
            }

            if (data.user_status) {
                // Play alarm if status just changed to SERVING
                if (data.user_status === 'SERVING' && previousStatus !== 'SERVING') {
                    playAlarm();
                    showTurnNotification();
                }
                previousStatus = data.user_status;

                const statusBadge = document.getElementById('token-status');
                if (statusBadge) {
                    statusBadge.innerText = data.user_status;
                    statusBadge.className = `status-badge status-${data.user_status}`;
                }

                const tokenCircle = document.querySelector('.token-circle');
                if (tokenCircle) {
                    if (data.user_status === 'SERVING') {
                        tokenCircle.style.boxShadow = '0 0 40px var(--accent-glow)';
                        tokenCircle.style.borderColor = 'var(--accent)';
                        tokenCircle.style.borderStyle = 'solid';
                    } else {
                        tokenCircle.style.boxShadow = 'none';
                        tokenCircle.style.borderStyle = 'dashed';
                    }
                }
            }
        };

        const pollQueue = () => {
            fetch('/api/status/')
                .then(res => res.json())
                .then(data => updateStatusUI(data))
                .catch(err => console.error("Polling error:", err));
        };

        setInterval(pollQueue, 5000);
        pollQueue(); 
        
        const attemptActivation = () => {
            if (isActivating) return;
            isActivating = true;
            
            const msgEl = document.getElementById('location-msg');
            msgEl.innerText = 'Checking location...';
            
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        
                        fetch('/api/activate/', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ lat, lng })
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                msgEl.innerText = `GPS Sync Complete. Token ${data.status.toLowerCase()}.`;
                                msgEl.style.color = "var(--accent)";
                                pollQueue();
                            } else {
                                msgEl.innerText = data.message;
                                msgEl.style.color = "var(--warning)";
                            }
                        })
                        .catch(err => {
                            msgEl.innerText = 'GPS Sync Error.';
                            console.error(err);
                        })
                        .finally(() => { isActivating = false; });
                    },
                    (error) => {
                        msgEl.innerText = 'GPS access required for activation.';
                        msgEl.style.color = "var(--danger)";
                        isActivating = false;
                    },
                    { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
                );
            } else {
                msgEl.innerText = "GPS not supported.";
                isActivating = false;
            }
        };

        if (document.getElementById('token-status').innerText === 'INACTIVE') {
            attemptActivation();
            setInterval(() => {
                if (document.getElementById('token-status').innerText === 'INACTIVE') {
                    attemptActivation();
                }
            }, 10000);
        }
    }
});
