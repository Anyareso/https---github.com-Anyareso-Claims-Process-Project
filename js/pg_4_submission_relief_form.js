// JavaScript code
function storeInput() {
    // Initialize an empty array
    const inputArray = [];
    
    // Get all the input elements
    const inputs = document.querySelectorAll('input');

    // Loop through each input element and add its value to the array
    inputs.forEach(input => {
        inputArray.push(input.value);
    });

    localStorage.setItem('page4InputData', JSON.stringify(inputArray));

    // Print the array to the console
    console.log(inputArray);
  }