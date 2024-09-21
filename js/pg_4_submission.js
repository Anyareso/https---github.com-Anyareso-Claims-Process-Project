document.addEventListener("DOMContentLoaded", function() {
    console.log("Entered signature logic...");
    var signaturePads = [];

    function initializeSignaturePad(canvasId, cancelBtnId, acceptBtnId) {
        var canvasContainer = document.getElementById("signature-pad-container");
        if (!canvasContainer) {
            console.error("Signature pad container element not found. ");
            return;
        }

        var canvas = canvasContainer.querySelector("#" + canvasId); // Use the container to scope the canvas selection
        if (!canvas) {
          console.error("Canvas element with ID " + canvasId + " not found. ");
          return;
        }

        var signaturePad = new SignaturePad(canvas);
        signaturePads.push(signaturePad);

        var cancelBtn =  canvasContainer.querySelector("#" + cancelBtnId); // Use the container to scope the cancel button selection
        if (cancelBtn) {
            cancelBtn.addEventListener("click", function() {
                signaturePad.clear();
            });
        } else {
            console.error("Cancel button with ID " + cancelBtnId + " not found.");
        }

        var acceptBtn = canvasContainer.querySelector("#" + acceptBtnId); // Use the container to scope the accept button selection
        if (acceptBtn) {
            acceptBtn.addEventListener("click", function() {
                if (signaturePad.isEmpty()) {
                    alert("Please provide a signature first.");
                } else {
                    var dataURL = signaturePad.toDataURL();
                    console.log("Signature accepted:", dataURL);
                }
            });
        } else {
            console.error("Accept button with ID " + acceptBtnId + " not found.");
        }
    }

    // Initialize signature pads
    initializeSignaturePad("signature-pad-1", "cancel-1", "accept-1");

    // Personal relief section handling
    var personalReliefYes = document.getElementById("personal-relief-yes");
    var personalReliefNo = document.getElementById("personal-relief-no");
    var personalReliefSection = document.getElementById("personal-relief-section");

    if (personalReliefYes && personalReliefNo && personalReliefSection) {
        personalReliefYes.addEventListener("change", function() {
            if (this.checked) {
                personalReliefSection.style.display = "block";
                console.log("Redirecting to pg_4_submission_relief_form.html");
                window.location.href = 'pg_4_submission_relief_form.html';
            }
        });

        personalReliefNo.addEventListener("change", function() {
            if (this.checked) {
                personalReliefSection.style.display = "none";
            }
        });
    } else {
        if (!personalReliefYes) console.error("Personal relief 'Yes' radio button not found.");
        if (!personalReliefNo) console.error("Personal relief 'No' radio button not found.");
        if (!personalReliefSection) console.error("Personal relief section not found.");
    }

    // Modal handling
    const modal = document.getElementById("dataProtectionModal");
    const link = document.getElementById("dataProtectionLink");
    const span = document.getElementsByClassName("close")[0];
    const completeButton = document.getElementById("completeButton");
    const rejectButton = document.getElementById("rejectButton");

    link.onclick = function(event) {
        event.preventDefault();
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    completeButton.onclick = function() {
        alert("Completed");
        modal.style.display = "none";
    }

    rejectButton.onclick = function() {
        alert("Rejected");
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});

// signature
const canvas = document.getElementById("signature-pad-1");
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth * 0.5;
canvas.height = window.innerHeight * 0.5;
canvas.style.background = "white";


let mouseX = 0;
let mouseY = 0;


let isDrawing = false;
canvas.addEventListener("mousedown", function (e) {
    isDrawing = true;

    ctx.beginPath();
    mouseX = e.clientX;
    mouseY = e.clientY;
    ctx.moveTo(mouseX, mouseY)

})

canvas.addEventListener("mousemove", function (e) {
    if (isDrawing) {
        ctx.lineTo(e.clientX, e.clientY);
        ctx.stroke();
    }

})

canvas.addEventListener("mouseup", function (e) {
    isDrawing = false;
})

function downloadCanvas() {
    var imageData = canvas.toDataURL("image/png");
    let anchorTag = document.createElement("a");
    document.body.appendChild(anchorTag);
    anchorTag.href = imageData;
    anchorTag.download = "imageData";
    anchorTag.click();
    document.body.removeChild(anchorTag);
}