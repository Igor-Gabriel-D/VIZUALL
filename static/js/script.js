let video = document.getElementById("video");
let model;

let elementoAcesso = document.getElementById('acesso');

let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");

canvas.width = 280
canvas.height = 320

let detectedFace = false;
let analysing = false;

color = "yellow"

const accessCamera = () => {
  navigator.mediaDevices
    .getUserMedia({
      video: { width: 280, height: 320},
      audio: false,
    })
    .then((stream) => {
      video.srcObject = stream;
    });
};

function enviarImagemCanvas() {
    canvas.toBlob(function(blob) {
      const formData = new FormData();
      formData.append('imagem', blob, 'canvas-image.png');
      analysing = true;  
      // Enviar a imagem via fetch
      fetch('https://8000-igorgabrield-vizuall-dv6v706z18w.ws-us116.gitpod.io/', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json()) // Agora esperamos um JSON
      .then(data => {
        console.log('Resposta do servidor:', data);
        // Exemplo de manipulação da resposta JSON
        analysing = false;
        detectedFace = false;
        elementoAcesso.innerHTML = `<p>${data.mensagem}</p>`;
      })
      .catch(error => console.error('Erro ao enviar a imagem:', error));

    }, 'image/png');
}
  

const detectFaces = async () => {
  const predictions = await model.estimateFaces(video, false);

  // Using canvas to draw the video first



  ctx.drawImage(video, 0, 0, 280, 320);

  predictions.forEach((prediction) => {

    // Drawing rectangle that'll detect the face
    ctx.beginPath();
    ctx.lineWidth = "4";
    ctx.strokeStyle = color;
    ctx.rect(
      prediction.topLeft[0],
      prediction.topLeft[1],
      prediction.bottomRight[0] - prediction.topLeft[0],
      prediction.bottomRight[1] - prediction.topLeft[1]
    );
    // The last two arguments denotes the width and height
    // but since the blazeface models only returns the coordinates  
    // so we have to subtract them in order to get the width and height
    ctx.stroke();
  });

  if(!detectedFace){
    detectedFace = false;
    console.log("aaaa")
  }
  if(predictions.length && !detectedFace && !analysing){
    
    console.log("bbbb")
    detectedFace = true;
    setTimeout(() => { enviarImagemCanvas() }, 5000);
    
  }

  console.log(predictions.length, !detectedFace, !analysing)
};

accessCamera();
video.addEventListener("loadeddata", async () => {
  model = await blazeface.load();
  // Calling the detectFaces every 40 millisecond
  setInterval(detectFaces, 100);
});