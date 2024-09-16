const dropArea = document.getElementById('drop-area');
const inputFile = document.getElementById('input-file');
const uploadedFilesList = document.getElementById('uploaded-files-list');
const maxSize = 2 * 1024 * 1024; // changed to 2 MB in bytes
const uploadedFiles = []; // Declare a global array to store uploaded files

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

// Highlight drop area when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false);

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    dropArea.classList.add('dragover');
}

function unhighlight() {
    dropArea.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    handleFiles(files);
}

inputFile.addEventListener('change', (e) => {
    const files = e.target.files;
    handleFiles(files);
});

function handleFiles(files) {
    Array.from(files).forEach(file => {
        if (file.size > maxSize) {
            document.getElementById('fileSizeMessage').innerText = 'File size exceeds 2 MB. Please choose a smaller file.';
            return;
        }
        document.getElementById('fileSizeMessage').innerText = '';
        if (uploadedFiles.length < 3) { // Check if the user has already uploaded 3 files
            const fileInfo = {
                file: file,
                name: file.name,
                size: file.size,
                type: file.type,
                progress: 0 // Add a progress property to store the upload progress
            };
            uploadedFiles.push(fileInfo);
            previewFile(file);
        } else {
            alert('You have already uploaded 3 files. Please remove some files before uploading more.');
        }
        // previewFile(file);
    });
}

function nextStep() {
    const uploadedFilesList = document.getElementById('uploaded-files-list');
    const files = uploadedFilesList.querySelectorAll('li.in-prog');

    files.forEach(fileListItem => {
        const file = fileListItem.dataset.file; // Get the file object from the list item
        uploadedFiles.push(file); // Add the file to the uploadedFiles array
    });

    console.log(uploadedFiles); // Check the uploadedFiles array
}

// Add an event listener to the "Next Step" button
const nextStepButton = document.getElementById('next-step-button');
nextStepButton.addEventListener('click', nextStep);

function previewFile(file) {
    const listItem = document.createElement('li');
    listItem.className = 'in-prog';
    listItem.dataset.file = file; // Set the file object on the list item


    const fileIcon = document.createElement('div');
    fileIcon.className = 'col';

    // Check the file type and set the icon
    if (file.type.startsWith('image/')) {
        fileIcon.innerHTML = `<img src="images/image-icon.png" alt="Image">`;
    } else if (file.type === 'application/pdf') {
        fileIcon.innerHTML = `<img src="images/pdf-icon.png" alt="PDF">`;
    } else {
        fileIcon.innerHTML = `<img src="images/default-icon.png" alt="File">`;
    }

    const fileName = document.createElement('div');
    fileName.className = 'col';
    fileName.innerHTML = `
        <div class="file-name">
            <div class="name">${file.name}</div>
            <span>100%</span>
        </div>
        <div class="file-progress">
            <span></span>
        </div>
        <div class="file-size">${formatFileSize(file.size)}</div>
    `;

    const fileActions = document.createElement('div');
    fileActions.className = 'col';
    fileActions.innerHTML = `
        <!-- exit and right icon -->
        <p class="tick">&#10003;</p>
        <p class="cross">&#10005;</p>
    `;

    listItem.appendChild(fileIcon);
    listItem.appendChild(fileName);
    listItem.appendChild(fileActions);

    uploadedFilesList.appendChild(listItem);

    // Add an event listener to the cross icon
    const crossIcon = listItem.querySelector('.cross');
    crossIcon.addEventListener('click', () => {
        // Remove the list item from the uploaded files list
        uploadedFilesList.removeChild(listItem);
    });
}

// Helper function to format file size
function formatFileSize(size) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let index = 0;
    while (size > 1024) {
        size /= 1024;
        index++;
    }
    return `${size.toFixed(2)} ${units[index]}`;
}
// checking progress for uploaded files
const fileInput = document.getElementById('fileInput');
// const uploadedFilesList = document.getElementById('uploaded-files-list');

fileInput.addEventListener('change', (e) => {
const file = e.target.files[0];
const maxSize = 2 * 1024 * 1024; // changed to 2 MB in bytes

if (file.size > maxSize) {
    document.getElementById('fileSizeMessage').innerText = 'File size exceeds 2 MB. Please choose a smaller file.';
    fileInput.value = ''; // Clear the input
    return;
}

const formData = new FormData();
formData.append('file', file);

fetch('/upload', {
    method: 'POST',
    body: formData,
})
.then((response) => response.json())
.then((data) => {
    console.log(data);
})
.catch((error) => {
    console.error(error);
});

const xhr = new XMLHttpRequest();
xhr.upload.addEventListener('progress', (e) => {
    const progress = (e.loaded / e.total) * 100;
    const listItem = uploadedFilesList.querySelector(`li[data-file-name="${file.name}"]`);
    listItem.querySelector('.file-progress span').style.width = `${progress}%`;
    listItem.querySelector('.file-progress span').innerText = `${progress.toFixed(2)}%`;
});

xhr.upload.addEventListener('load', () => {
    const listItem = uploadedFilesList.querySelector(`li[data-file-name="${file.name}"]`);
    listItem.querySelector('.file-progress span').style.width = `100%`;
    listItem.querySelector('.file-progress span').innerText = `100%`;
});
});