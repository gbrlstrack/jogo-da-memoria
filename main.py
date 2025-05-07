# import pygame
#
# pygame.init()
#
# janela = pygame.display.set_mode((1280, 720))
# pygame.display.set_caption("Hello World!")
#
# isOpenWindow = True
#
# while isOpenWindow:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             isOpenWindow = False
#
# pygame.quit()
# -- coding: utf-8 --
import cv2
import mediapipe as mp
import numpy as np

vetor_referencia = np.load("results/arroz.npy")
# Inicializar MediaPipe para detecção de mãos
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# Função para aplicar o efeito de visão noturna (opcional)
def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    median_filtered = cv2.medianBlur(gray, 5)
    equalized = cv2.equalizeHist(median_filtered)
    return equalized

# Função para extrair os landmarks de um frame
def extrair_landmarks(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands_detector.process(frame_rgb)
    
    if result.multi_hand_landmarks:
        landmarks = []
        for lm in result.multi_hand_landmarks[0].landmark:
            landmarks.append([lm.x, lm.y, lm.z])
        return np.array(landmarks).flatten()
    return None

# Abrir o vídeo com gesto correto
video = cv2.VideoCapture("assets/arroz.mp4")
dados = []

while True:
    success, frame = video.read()
    if not success:
        break

    vetor = extrair_landmarks(frame)
    if vetor is not None:
        dados.append(vetor)

video.release()

# Calcular vetor representativo do gesto
if dados:
    vetor_representativo = np.mean(dados, axis=0)
    np.save("results/arroz.npy", vetor_representativo)
    print("Vetor salvo com sucesso em 'results/arroz.npy'")
else:
    print("Nenhum gesto detectado no vídeo.")

# === 4. Função para comparar gestos ===
def comparar_gestos(vetor1, vetor2):
    return np.linalg.norm(vetor1 - vetor2)

# === 5. Captura da webcam ===
video = cv2.VideoCapture(0)

reconhecido = False

while True:
    success, frame = video.read()
    if not success:
        break

    if not reconhecido:
        vetor_usuario = extrair_landmarks(frame)
        
        if vetor_usuario is not None:
            distancia = comparar_gestos(vetor_usuario, vetor_referencia)

            limiar = 0.4
            if distancia < limiar:
                reconhecido = True
                texto = "✅ Gesto reconhecido com sucesso!"
                cor = (0, 255, 0)
            else:
                texto = f"Gesto incorreto (distância={distancia:.3f})"
                cor = (0, 0, 255)
        else:
            texto = "Mão não detectada"
            cor = (0, 255, 255)
    else:
        texto = "✅ Gesto já reconhecido!"
        cor = (0, 255, 0)

    cv2.putText(frame, texto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)
    cv2.imshow("Reconhecimento de Gesto", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()