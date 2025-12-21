# Story 8.4: Fix QR Code Rendering on Player Page

Status: done

## Story

As a **player**,
I want **the QR code to render correctly on the player lobby page**,
so that **I can invite friends to join the game**.

## Root Cause Analysis

The player.js `renderQRCode()` function uses the **wrong QR code library API**:

- **Current code uses:** `qrcode(0, 'M')` - This is the **qrcode-generator** library syntax
- **Library loaded:** `qrcode.min.js` - This is the **qrcodejs** library which uses `new QRCode()` constructor

The admin.js correctly uses the qrcodejs API, but player.js was written for a different library.

## Acceptance Criteria

1. **Given** a player joins the game and reaches the lobby view **When** the QR code section renders **Then** a valid QR code image is displayed
2. **Given** a player is on the lobby view **When** the QR code displays **Then** the QR code is scannable and leads to the join URL
3. **Given** a player taps the QR code to enlarge **When** the modal opens **Then** a larger QR code is displayed correctly
4. **Given** the QR code modal **When** displayed **Then** the QR code encodes the same join URL

## Tasks / Subtasks

- [x] Task 1: Fix `renderQRCode()` function (AC: 1, 2)
  - [x] Replace qrcode-generator API with qrcodejs API (lines 198-225)
  - [x] Match the pattern used in admin.js for consistency (128x128 for inline)

- [x] Task 2: Fix `openQRModal()` function (AC: 3, 4)
  - [x] Replace qrcode-generator API with qrcodejs API (lines 230-250)
  - [x] Use larger dimensions for modal QR code (256x256)

## Dev Notes

### Current Broken Code (player.js lines 198-225)

```javascript
function renderQRCode(joinUrl) {
    if (!joinUrl) return;
    currentJoinUrl = joinUrl;

    const container = document.getElementById('player-qr-code');
    if (!container) return;

    // Clear previous QR
    container.innerHTML = '';

    // WRONG API - qrcode-generator syntax
    var qr = qrcode(0, 'M');
    qr.addData(joinUrl);
    qr.make();
    container.innerHTML = qr.createImgTag(4, 0);

    // Add click handler for modal
    container.onclick = openQRModal;
    container.onkeydown = function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openQRModal();
        }
    };
}
```

### Fixed Code (matching admin.js pattern)

```javascript
function renderQRCode(joinUrl) {
    if (!joinUrl) return;
    currentJoinUrl = joinUrl;

    var container = document.getElementById('player-qr-code');
    if (!container) return;

    // Clear previous QR
    container.innerHTML = '';

    // CORRECT API - qrcodejs syntax (matches admin.js)
    if (typeof QRCode !== 'undefined') {
        new QRCode(container, {
            text: joinUrl,
            width: 128,
            height: 128,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });
    } else {
        container.innerHTML = '<p class="status-error">QR code library not loaded</p>';
    }

    // Add click handler for modal
    container.onclick = openQRModal;
    container.onkeydown = function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openQRModal();
        }
    };
}
```

### Current Broken Modal Code (player.js lines 230-250)

```javascript
function openQRModal() {
    if (!currentJoinUrl) return;

    var modal = document.getElementById('qr-modal');
    var modalCode = document.getElementById('qr-modal-code');
    if (!modal || !modalCode) return;

    // Clear and render larger QR
    modalCode.innerHTML = '';
    // WRONG API
    var qr = qrcode(0, 'M');
    qr.addData(currentJoinUrl);
    qr.make();
    modalCode.innerHTML = qr.createImgTag(8, 0);  // Larger cell size

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Focus close button for accessibility
    var closeBtn = document.getElementById('qr-modal-close');
    if (closeBtn) closeBtn.focus();
}
```

### Fixed Modal Code

```javascript
function openQRModal() {
    if (!currentJoinUrl) return;

    var modal = document.getElementById('qr-modal');
    var modalCode = document.getElementById('qr-modal-code');
    if (!modal || !modalCode) return;

    // Clear and render larger QR
    modalCode.innerHTML = '';

    // CORRECT API - qrcodejs syntax with larger size for modal
    if (typeof QRCode !== 'undefined') {
        new QRCode(modalCode, {
            text: currentJoinUrl,
            width: 256,
            height: 256,
            colorDark: '#000000',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });
    }

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Focus close button for accessibility
    var closeBtn = document.getElementById('qr-modal-close');
    if (closeBtn) closeBtn.focus();
}
```

### Reference: Working admin.js QR Code (lines 411-427)

```javascript
if (typeof QRCode !== 'undefined') {
    new QRCode(qrContainer, {
        text: gameData.join_url,
        width: 300,
        height: 300,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.M
    });
} else {
    qrContainer.innerHTML = '<p class="status-error">QR code library not loaded</p>';
}
```

### File Locations

| File | Path | Lines to Modify |
|------|------|-----------------|
| player.js | `custom_components/beatify/www/js/player.js` | 198-225 (renderQRCode), 230-250 (openQRModal) |

### Testing

1. Join a game as a player
2. Verify QR code displays correctly on lobby view
3. Verify QR code is scannable (test with phone camera)
4. Tap QR code to open modal
5. Verify larger QR code displays in modal
6. Verify modal QR code is scannable
7. Scan QR code and verify it opens correct join URL

### QRCode.js Library Reference

The qrcodejs library is loaded via:
```html
<script src="/beatify/static/js/vendor/qrcode.min.js"></script>
```

API:
```javascript
new QRCode(element, {
    text: "string to encode",
    width: 128,           // pixels
    height: 128,          // pixels
    colorDark: "#000000", // QR code color
    colorLight: "#ffffff", // background color
    correctLevel: QRCode.CorrectLevel.M  // L, M, Q, H
});
```

### References

- [Source: epics.md#Story 8.4]
- [Source: project-context.md#Frontend Rules]
- [Source: admin.js lines 411-427 for working implementation]

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
N/A

### Completion Notes List
- Fixed renderQRCode() to use qrcodejs API (new QRCode()) instead of qrcode-generator
- Fixed openQRModal() to use qrcodejs API for larger modal QR code
- Inline QR code: 128x128 pixels
- Modal QR code: 256x256 pixels
- Both now match the working admin.js pattern
- Added error handling with fallback message if QRCode library not loaded

### File List
- custom_components/beatify/www/js/player.js
