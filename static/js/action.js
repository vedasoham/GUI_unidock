function showLigUpload() {
    document.getElementById("receptor-upload").style.display = "none"
    document.getElementById("ligand-upload").style.display = "block"
    document.getElementById("upload-receptor").classList.remove(('active', 'btn-outline-primary'))
    document.getElementById("upload-receptor").classList.add('disabled')
    document.getElementById('upload-ligand').classList.add('active', 'btn-outline-primary')
    document.getElementById('upload-ligand').classList.remove('disabled')
}

function paramSetShow() {
    document.getElementById("ligand-upload").style.display = "none"
    document.getElementById("param-card").style.display = "block"
    document.getElementById("upload-ligand").classList.remove(('active', 'btn-outline-primary'))
    document.getElementById("upload-ligand").classList.add('disabled')
    document.getElementById('param').classList.add('active', 'btn-outline-primary')
    document.getElementById('param').classList.remove('disabled')
}

function runDockActive() {
    document.getElementById("param").classList.remove(('active', 'btn-outline-primary'))
    document.getElementById("param").classList.add('disabled')
    document.getElementById('run').classList.add('active', 'btn-outline-primary')
    document.getElementById('run').classList.remove('disabled')
}