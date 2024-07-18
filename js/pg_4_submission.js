document.addEventListener("DOMContentLoaded", function() {
    var signaturePads = [];
    
    function initializeSignaturePad(canvasId, cancelBtnId, acceptBtnId) {
        var canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error("Canvas element with ID " + canvasId + " not found.");
            return;
        }

        var signaturePad = new SignaturePad(canvas);
        signaturePads.push(signaturePad);

        var cancelBtn = document.getElementById(cancelBtnId);
        if (cancelBtn) {
            cancelBtn.addEventListener("click", function() {
                signaturePad.clear();
            });
        } else {
            console.error("Cancel button with ID " + cancelBtnId + " not found.");
        }

        var acceptBtn = document.getElementById(acceptBtnId);
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
                // Replace 'relief_form.html' with the URL of the new HTML page
                location.href = 'pg_4_submission_relief_form.html';
            }
        });
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
        if (!personalReliefYes) {
            console.error("Personal relief 'Yes' radio button not found.");
        }
        if (!personalReliefNo) {
            console.error("Personal relief 'No' radio button not found.");
        }
        if (!personalReliefSection) {
            console.error("Personal relief section not found.");
        }
    }
});

function clearSignature(id) {
    var signaturePad = signaturePads.find(function(pad) {
        return pad._canvas.id === id;
    });

    if (!signaturePad) {
        console.error("Signature pad with ID " + id + " not found.");
        return;
    }

    signaturePad.clear();
}

// Get the modal
const modal = document.getElementById("dataProtectionModal");

// Get the link that opens the modal
const link = document.getElementById("dataProtectionLink");

// Get the <span> element that closes the modal
const span = document.getElementsByClassName("close")[0];

// Get the complete and reject buttons
const completeButton = document.getElementById("completeButton");
const rejectButton = document.getElementById("rejectButton");

// When the user clicks the link, open the modal 
link.onclick = function(event) {
    event.preventDefault();
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks on the complete button, perform the action and close the modal
completeButton.onclick = function() {
    // Perform the action for completion
    alert("Completed");
    modal.style.display = "none";
}

// When the user clicks on the reject button, perform the action and close the modal
rejectButton.onclick = function() {
    // Perform the action for rejection
    alert("Rejected");
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

