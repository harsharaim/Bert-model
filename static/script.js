let backendValue = '';
window.onload = function() {
  const fileElements = document.getElementById('file-info');
  const proceedbtn = document.getElementById('process');
  const outputWindow = document.getElementById('output');
  fileElements.style.display = 'none';
  proceedbtn.style.display = 'none';
  outputWindow.style.display = 'none';
};



const processVideo = async () => {
  const progressBar = document.getElementById('progress-bar');
  const progress = document.getElementById('progress');
  const outputWindow = document.getElementById('output');
  const videoFile = document.getElementById("file-input").files[0];
  const formData = new FormData();
  progressBar.style.display = 'block';
  outputWindow.style.display = 'none';

  formData.append("video", videoFile);

  const simulateBackendResponse = async () => {
    let width = 0;
    const delay = 500; // Adjust the delay time (in milliseconds) to control the speed of progress

    while (width < 100) {
      await new Promise(resolve => setTimeout(resolve, delay));

      if (width >= 50) {
        try {
          const response = await fetch("http://127.0.0.1:5002/process_video", {
            method: "POST",
            body: formData,
          });

          const data = await response.json();
          backendValue = data.text;

          if (backendValue !== '') {
            for(let i=0;i<50;i++){
              width+=1;
            }
          } else {
            width += 1;
          }
        } catch (error) {
          // Handle errors from fetch
          console.error("Error fetching data:", error);
        }
      } else {
        width += 1;
      }

      progress.style.width = width + '%';
    }

    // Hide the progress bar once the data is received
    // progressBar.style.display = 'none';
    // Show the output window after processing
    outputWindow.style.display = 'block';
  };

  try {
    await simulateBackendResponse();
    document.getElementById('output_content').innerText = backendValue;
  } catch (error) {
    console.error("Error:", error);
  }
};







const browseFile = () =>{
  document.getElementById('file-input').click();
}

const copy = () => {
  const contentElement = document.getElementById('output');
  const contentToCopy = contentElement.textContent;
  const textarea = document.createElement('textarea');
  textarea.value = contentToCopy;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  alert('Content copied to clipboard!');
}

const handleFiles = (file)=>{
  const progress = document.getElementById('progress');
  const fileContainer = document.querySelector('#file_process_container');
  const progressBar = document.getElementById('progress-bar');
  const fileName = document.getElementById('filename-span');
  const fileElements = document.getElementById('file-info');
  const proceedbtn = document.getElementById('process');
  Name = file[0].name;
  if(Name.length > 100){
    Name = Name.slice(0,100);
    Name+='......';
  }
  fileName.innerText = Name;
  fileElements.style.display = '';
  proceedbtn.style.display = '';
  progressBar.style.display = 'none';
  fileContainer.style.background = 'none';
  progress.style.width = '0%';
}
const cancel = ()=>{
  
  const fileElements = document.getElementById('file-info');
  const proceedbtn = document.getElementById('process');
  const outputWindow = document.getElementById('output');
  fileElements.style.display = 'none';
  proceedbtn.style.display = 'none';
  
}