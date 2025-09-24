const html5QrCode = new Html5Qrcode("qr-video");
const stopBtn = document.getElementById("stopBtn");
const status = document.getElementById("status");
const resultBox = document.getElementById("result");

let scannerRunning = false;

function startScanner() {
  Html5Qrcode.getCameras().then(cameras => {
    if (cameras && cameras.length) {
      const cameraId = cameras[0].id;
      html5QrCode.start(
        cameraId,
        { fps: 10, qrbox: 250 },
        qrCodeMessage => {
          resultBox.innerHTML = `<strong>QR Code Detected:</strong><br>${qrCodeMessage}`;
          resultBox.style.display = "block";
          status.textContent = "QR code detected!";
        },
        errorMessage => {
          // Optional: handle scan failures
        }
      );
      scannerRunning = true;
    } else {
      status.textContent = "No camera found.";
    }
  }).catch(err => {
    status.textContent = "Camera error: " + err;
  });
}

stopBtn.addEventListener("click", () => {
  if (scannerRunning) {
    html5QrCode.stop().then(() => {
      status.textContent = "Scanner stopped.";
      scannerRunning = false;
    });
  }
});

startScanner();
