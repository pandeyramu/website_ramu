function previewImage(event, imgId) {
    var reader = new FileReader();
    reader.onload = function() {
        var imgElement = document.getElementById(imgId);
        imgElement.src = reader.result;
    }
    reader.readAsDataURL(event.target.files[0]);
}

document.addEventListener('DOMContentLoaded', function() {
    const btn = document.querySelector('#btn');
    const cadinfo = document.querySelectorAll('#candi #img1 , #candi #img2');

    btn.addEventListener("click", function() {
        const alldata = []; // Initialize empty array for storing all data

        cadinfo.forEach(entry => {
            const name = entry.querySelector('.name').value;
            const age = entry.querySelector('.age').value;
            const party = entry.querySelector('.party').value;
            const imageFile = entry.querySelector('.cad').files;

            // Check if an image file was selected
            if (imageFile) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const imageSrc = event.target.result;

                    const data = {
                        name: name,
                        age: age,
                        party: party,
                        image: imageSrc  // Store image data URI
                    };

                    alldata.push(data);

                    // Check if all entries have been processed before logging
                    if (alldata.length === cadinfo.length) {
                        console.log('All form data:', alldata);
                        // Uncomment below if you want to navigate to another page after logging data
                        // window.location.href = 'user.html';
                    }
                };

                reader.readAsDataURL(imageFile); // Read the image file as data URL
            } else {
                // Handle case where no image was selected
                const data = {
                    name: name,
                    age: age,
                    party: party,
                    image: ''  // Empty string or null for image if needed
                };

                alldata.push(data);

                // Check if all entries have been processed before logging
               
            }
        }); 
        if (alldata.length === cadinfo.length) {
                    console.log('All form data:', alldata);
                    // Uncomment below if you want to navigate to another page after logging data
                    // window.location.href = 'user.html'
                }
    });
});
