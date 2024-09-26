import os
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
from rembg import remove

app = Flask(__name__)

# Configurações de pasta
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para uploads

# Certifique-se de que as pastas existam
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    imagem_processada = None  # Inicializa a variável para evitar erros se nenhuma imagem for processada

    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'imagem' not in request.files:
            print("Nenhuma imagem foi enviada.")
            return redirect(request.url)

        file = request.files['imagem']

        if file.filename == '':
            print("Nome de arquivo vazio.")
            return redirect(request.url)

        if file:
            try:
                print(f"Imagem enviada: {file.filename}")

                # Caminho para salvar a imagem original enviada
                caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(caminho_imagem)
                print(f"Imagem salva em: {caminho_imagem}")

                # Processa a imagem para remover o fundo
                imagem = Image.open(caminho_imagem)
                imagem_sem_fundo = remove(imagem)
                print(f"Fundo removido da imagem: {file.filename}")

                # Verifica se a imagem é RGBA e converte para RGB se necessário
                caminho_processado = os.path.join(app.config['PROCESSED_FOLDER'],
                                                  file.filename.rsplit('.', 1)[0] + '.png')
                if imagem.mode == 'RGBA':
                    imagem_sem_fundo = imagem_sem_fundo.convert('RGB')
                print(f"Imagem processada será salva em: {caminho_processado}")

                # Salva a imagem processada
                imagem_sem_fundo.save(caminho_processado, format='PNG')
                print(f"Imagem processada salva com sucesso em: {caminho_processado}")

                # Gera o caminho para exibir e baixar a imagem
                caminho_url = url_for('static', filename=f'processed/{file.filename.rsplit(".", 1)[0]}.png')
                return render_template('index.html', imagem_processada=caminho_url)

            except Exception as e:
                print(f"Erro ao processar a imagem: {e}")
                return redirect(request.url)

    return render_template('index.html', imagem_processada=imagem_processada)


if __name__ == '__main__':
    app.run(debug=True)
