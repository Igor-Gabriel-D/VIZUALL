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
      elementoAcesso.innerHTML = `<h3 id="acesso">Analisando<span class="dots"></span></h3>`
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
        // detectedFace = false;
        elementoAcesso.innerHTML = `<h3>${data.mensagem}</h3>`;
        if(data.mensagem == "Acesso liberado"){
            color = "green"
        } else {
            color = "red"
        }
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

    if(!predictions.length && elementoAcesso.innerHTML != `<h3 id="acesso">Esperando<span class="dots"></span></h3>`){
      detectedFace = false;
      elementoAcesso.innerHTML = `<h3 id="acesso">Esperando<span class="dots"></span></h3>`
      color = "yellow"
    }
    
    if(predictions.length && !detectedFace && !analysing){
        detectedFace = true;
        setTimeout(() => { enviarImagemCanvas() }, 5000);
    
    }

};

accessCamera();
video.addEventListener("loadeddata", async () => {
  model = await blazeface.load();
  // Calling the detectFaces every 40 millisecond
  setInterval(detectFaces, 100);
});
function carregarBlocos() {
    fetch('/salas')
    .then(response => response.json())
      .then(data => {
        const selectBloco = document.getElementById('select-bloco');
  
        // Preenche o select de blocos
        data.forEach(bloco => {
          const option = document.createElement('option');
          option.value = bloco._id; // Supondo que cada bloco tenha um campo "id"
          option.textContent = bloco.nome_bloco; // Supondo que cada bloco tenha um campo "nome"
          selectBloco.appendChild(option);
        });
      })
      .catch(error => console.error('Erro ao carregar blocos:', error));
}
  
function atualizarSalas() {
    const blocoId = document.getElementById('select-bloco').value;
    const selectSala = document.getElementById('select-sala');
  
    // Limpa o select de salas
    selectSala.innerHTML = '<option value="">Escolha uma sala</option>';
  
    if (blocoId) {
      fetch('/salas')
        .then(response => response.json())
        .then(data => {
          // Encontra o bloco selecionado
          console.log(data)
          const blocoSelecionado = data.find(bloco => bloco._id === blocoId);

          console.log(blocoId)

          console.log(blocoSelecionado)
          // Preenche o select de salas para o bloco selecionado
          if (blocoSelecionado && blocoSelecionado.bloco.salas) {
            console.log("aaaa")
            blocoSelecionado.bloco.salas.forEach(sala => {
              const option = document.createElement('option');
              option.value = sala.sala_id; // Supondo que cada sala tenha um campo "id"
              option.textContent = sala.nome_sala; // Supondo que cada sala tenha um campo "nome"
              selectSala.appendChild(option);
            });
          }
        })
        .catch(error => console.error('Erro ao carregar salas:', error));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    carregarBlocos();
});
      