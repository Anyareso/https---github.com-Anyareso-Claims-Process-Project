'use strict';

      const video = document.getElementById('video');
      const canvas = document.getElementById('canvas');
      const snap = document.getElementById('snap');
      const context = canvas.getContext('2d');
      const redo = document.getElementById('redo');
      const confirm = document.getElementById('confirm');
      
      const constraints = {
          audio: false,
          video: {
              width: 320, 
              height: 320
          }
      };

      // Access Webcam
      async function init() {
          try {
              const stream = await navigator.mediaDevices.getUserMedia(constraints);
              handleSuccess(stream);
          } catch (e) {
              console.error('navigator.getUserMedia error:', e);
          }
      }

      // Success
      function handleSuccess(stream) {
          window.stream = stream;
          video.srcObject = stream;
      }

      // Load init
      init();

      // Draw Image
      snap.addEventListener("click", function () {
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
      });

      // Clearing canvas
      redo.addEventListener("click", function () {
          context.clearRect(0, 0, canvas.width, canvas.height);
      });

      // Saving the image
      confirm.addEventListener("click", function () {
          const imageData = canvas.toDataURL();
          const link = document.createElement('a');
          link.href = imageData;
          link.download = 'selfie.png';
          link.click();
          // const image = new Image();
          // image.src = imageData;
          // // Now you can use the image as needed
          // // For example, you can append it to the page
          // document.body.appendChild(image);
      });