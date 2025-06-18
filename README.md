
# LIBRASPlay 🎮🤟

É um jogo educacional interativo que ensina a Língua Brasileira de Sinais (LIBRAS) por meio de reconhecimento de gestos com visão computacional. O jogo apresenta vídeos com gestos e desafia o usuário a reproduzi-los corretamente usando a webcam.

---

## 🧠 Como Funciona

1. O jogo exibe um vídeo com um gesto em LIBRAS.
2. O usuário deve imitar o gesto usando a mão em frente à webcam.
3. O sistema analisa o gesto do usuário e compara com o gesto do vídeo.
4. Se o gesto for semelhante, o usuário avança de fase. Caso contrário, ele deve tentar novamente.

---

## 📁 Estrutura do Projeto

```
LIBRASPlay/
├── assets/           # Pasta com os vídeos dos gestos (formato .mp4)
├── results/          # Vetores .npy gerados automaticamente a partir dos vídeos
├── main.py           # Código principal do jogo
├── camera.test.py    # verifica qual câmera está disponível (em caso de notebook com uma web cam no USB)
└── README.md         # Este arquivo
```

---

## 📦 Instalação

### ✅ Pré-requisitos

- Python 3.8 ou superior
- Pip instalado
- Webcam (preferencialmente USB)

### 📥 Instalando as bibliotecas

Abra o terminal e execute os seguintes comandos:

```bash
pip install opencv-python
pip install numpy
pip install mediapipe
pip install pygame
```

Se preferir, você pode instalar tudo de uma vez com:

```bash
pip install opencv-python numpy mediapipe pygame
```

---

## ▶️ Como Executar o Jogo

1. Certifique-se de que os vídeos dos gestos estão dentro da pasta `assets/`.
2. Execute o script principal:

```bash
python main.py
```

3. Ao iniciar, o programa irá:

   - Processar todos os vídeos da pasta `assets/`
   - Gerar os vetores de referência para cada gesto e salvá-los na pasta `results/`

4. Em seguida, será exibido um menu com a opção "Jogar".
5. O usuário escolherá o número de palavras (gestos) que deseja treinar.
6. O jogo iniciará exibindo um vídeo com o gesto e, depois, a câmera será ativada para que o usuário tente reproduzi-lo.

---

## 📹 Sobre os Vídeos (Pasta `assets/`)

- Os arquivos de vídeo devem estar no formato `.mp4`.
- O nome do arquivo (sem a extensão) será usado como identificador do gesto.
- Exemplo:
  ```
  assets/
  ├── oi.mp4
  ├── obrigado.mp4
  ├── tchau.mp4
  ```

---

## 🧠 Sobre os Vetores (Pasta `results/`)

- A cada vídeo processado, será gerado um arquivo `.npy` contendo um vetor representativo do gesto.
- Esses vetores são usados para comparar os gestos feitos pelo usuário em tempo real.
- Exemplo:
  ```
  results/
  ├── oi.npy
  ├── obrigado.npy
  ├── tchau.npy
  ```

---

## 🛠️ Dicas e Observações

- Certifique-se de que sua mão esteja bem iluminada e visível para a câmera.
- O gesto deve ser feito com calma, preferencialmente no centro da imagem.
- O jogo pode ser adaptado para diferentes gestos e níveis de dificuldade, basta adicionar novos vídeos em `assets/`.

---

## 💡 Possíveis Melhorias Futuras

- Adicionar sons e efeitos para reforçar o feedback.
- Incluir um modo tutorial com explicações passo a passo dos gestos.
- Armazenar histórico de desempenho do usuário.
- Exportar o jogo para plataformas móveis.


## 👨‍🏫 Autor

Gustavo de Lima Bento  
Gabriel Strack
Projeto desenvolvido para disciplina de Processamento de Imagens - Engenharia de Software  

