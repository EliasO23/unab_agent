const reglamentos = document.querySelectorAll(".reglamento");

function abrir(item){
    const body = item.querySelector(".reglamento-body");
    const icon = item.querySelector(".reglamento-icon");
    item.classList.add("active");
    body.style.maxHeight = body.scrollHeight + "px";
    icon.textContent = "×";
}

function cerrar(item){
    const body = item.querySelector(".reglamento-body");
    const icon = item.querySelector(".reglamento-icon");
    item.classList.remove("active");
    body.style.maxHeight = null;
    icon.textContent = "+";
}

window.addEventListener("load", () => {
    reglamentos.forEach(item => {
        if(item.classList.contains("active")){
            abrir(item);
        }
    });
});

reglamentos.forEach(item => {
    item.querySelector(".reglamento-header").addEventListener("click", () => {
        const abierto = item.classList.contains("active");
        reglamentos.forEach(cerrar);
        if(!abierto){
            abrir(item);
        }
    });
});