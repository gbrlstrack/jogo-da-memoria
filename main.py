import random
import time
import cv2
import pygame
import sys
import mediapipe as mp
import numpy as np
import os

# Inicializa MediaPipe
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils
vetores_preparados = False


# Função para extrair os landmarks de um frame
def extrair_landmarks(frame_video):
    frame_rgb = cv2.cvtColor(frame_video, cv2.COLOR_BGR2RGB)
    result = hands_detector.process(frame_rgb)

    if result.multi_hand_landmarks:
        landmarks = []
        for lm in result.multi_hand_landmarks[0].landmark:
            landmarks.append([lm.x, lm.y, lm.z])
        return np.array(landmarks).flatten()
    return None


def preparar_vetores_gestos(pasta_videos="assets", pasta_resultados="results"):
    print("📁 Processando vídeos para gerar vetores de gestos...")
    os.makedirs(pasta_resultados, exist_ok=True)

    for arquivo in os.listdir(pasta_videos):
        if arquivo.endswith(".mp4"):
            caminho_video = os.path.join(pasta_videos, arquivo)
            nome_gesto = os.path.splitext(arquivo)[0]
            print(f"🎥 Processando gesto: {nome_gesto}")

            video = cv2.VideoCapture(caminho_video)
            dados = []

            while True:
                success, frame = video.read()
                if not success:
                    break

                vetor = extrair_landmarks(frame)
                if vetor is not None:
                    dados.append(vetor)

            video.release()

            if dados:
                vetor_representativo = np.mean(dados, axis=0)
                np.save(os.path.join(pasta_resultados, f"{nome_gesto}.npy"), vetor_representativo)
                print(f"✅ Vetor de '{nome_gesto}' salvo com sucesso!")
            else:
                print(f"⚠️ Nenhum gesto detectado no vídeo '{nome_gesto}'. Vetor não salvo.")

    print("✅ Todos os vetores foram preparados.")


preparar_vetores_gestos()
vetores_preparados = True
pygame.init()
largura = 1280
altura = 720
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Hello World!")

isOpenWindow = True

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
fonte = pygame.font.SysFont(None, 60)


def desenhar_texto(texto, font, cor, surface, x, y):
    textoobj = font.render(texto, True, cor)
    textorect = textoobj.get_rect(center=(x, y))
    surface.blit(textoobj, textorect)


def menu_selecao_palavras():
    selecionado = None
    botoes = []

    for i in range(1, 7):
        botao = pygame.Rect(largura // 2 - 100, altura // 2 - 50 + (i - 1) * 120, 200, 100)
        botoes.append((i, botao))

    while selecionado is None:
        tela.fill(BRANCO)
        desenhar_texto("Escolha o número de palavras", fonte, PRETO, tela, largura // 2, altura // 4)

        for i, botao in botoes:
            pygame.draw.rect(tela, CINZA, botao)
            desenhar_texto(str(i), fonte, PRETO, tela, botao.centerx, botao.centery)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, botao in botoes:
                    if botao.collidepoint(evento.pos):
                        selecionado = i
                        print(f"Palavras selecionadas: {selecionado}")
                        return selecionado

        pygame.display.update()
    return None


def menu():
    global vetores_preparados
    if not vetores_preparados:
        tela.fill(BRANCO)
        desenhar_texto("Preparando vetores...", fonte, PRETO, tela, largura // 2, altura // 2)
        pygame.display.update()
        preparar_vetores_gestos()
        vetores_preparados = True

    while True:
        tela.fill(BRANCO)

        # Desenha o botão
        botao_jogar = pygame.Rect(largura // 2 - 100, altura // 2 - 50, 200, 100)
        pygame.draw.rect(tela, CINZA, botao_jogar)
        desenhar_texto("Jogar", fonte, PRETO, tela, largura // 2, altura // 2)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(evento.pos):
                    num_palavras = menu_selecao_palavras()
                    jogo(num_palavras)

        pygame.display.update()


def reproduzir_video_cv2(caminho):
    cap = cv2.VideoCapture(caminho)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Vídeo", frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def jogo(num_palavras):
    rodando = True
    hasVideosSelected = False
    index_video = 0
    cap = None
    mostrar_proximo_em = 0
    esperando_proximo = False

    while rodando:
        tela.fill((100, 150, 250))

        if not hasVideosSelected:
            videos = sorted(
                [f for f in os.listdir('assets') if f.endswith('.mp4')])  # Lista os vídeos da pasta 'assets'
            # Garantir que não ultrapasse o número de vídeos disponíveis
            videos = videos[:num_palavras]
            # Embaralha os vídeos para seleção aleatória
            random.shuffle(videos)

        if index_video < len(videos):
            if not cap:
                video_atual_nome = videos[index_video]
                video_path = os.path.join("assets", video_atual_nome)
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print(f"❌ Erro ao abrir vídeo: {video_path}")
                    index_video += 1
                    continue
                print(f"▶️ Reproduzindo: {video_atual_nome}")

            ret, frame = cap.read()
            if not ret:  # Se o vídeo terminou
                cap.release()  # Libera o vídeo
                cap = None
                index_video += 1  # Avança para o próximo vídeo
                continue  # Vai para o próximo loop

            # Reduz o tamanho do vídeo
            video_largura = 640
            video_altura = 360
            frame = cv2.resize(frame, (video_largura, video_altura))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Cria a superfície do frame do vídeo
            surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))

            # Calcula posição central para o vídeo
            pos_x = (largura - video_largura) // 2
            pos_y = (altura - video_altura) // 2

            tela.fill(BRANCO)
            nome_palavra = os.path.splitext(video_atual_nome)[0]
            desenhar_texto(nome_palavra.capitalize(), fonte, PRETO, tela, largura // 2, pos_y - 40)
            tela.blit(surface, (pos_x, pos_y))

            # Espera conforme FPS do vídeo
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / video_fps) if video_fps > 0 else 33
            pygame.time.delay(delay)

        else:
            desenhar_texto("✅ Fim dos vídeos!", fonte, PRETO, tela, largura // 2, altura // 2)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False  # Volta ao menu

        pygame.display.update()


# Executa o menu
menu()

# -- coding: utf-8 --
# import cv2
# import mediapipe as mp
# import numpy as np

# vetor_referencia = np.load("results/arroz.npy")
# # Inicializar MediaPipe para detecção de mãos
# mp_hands = mp.solutions.hands
# hands_detector = mp_hands.Hands(max_num_hands=1)
# mpDraw = mp.solutions.drawing_utils

# # Função para aplicar o efeito de visão noturna (opcional)
# def process_frame(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     median_filtered = cv2.medianBlur(gray, 5)
#     equalized = cv2.equalizeHist(median_filtered)
#     return equalized


# # Abrir o vídeo com gesto correto
# video = cv2.VideoCapture("assets/arroz.mp4")
# dados = []

# while True:
#     success, frame = video.read()
#     if not success:
#         break

#     vetor = extrair_landmarks(frame)
#     if vetor is not None:
#         dados.append(vetor)

# video.release()

# # Calcular vetor representativo do gesto
# if dados:
#     vetor_representativo = np.mean(dados, axis=0)
#     np.save("results/arroz.npy", vetor_representativo)
#     print("Vetor salvo com sucesso em 'results/arroz.npy'")
# else:
#     print("Nenhum gesto detectado no vídeo.")

# # === 4. Função para comparar gestos ===
# def comparar_gestos(vetor1, vetor2):
#     return np.linalg.norm(vetor1 - vetor2)

# # === 5. Captura da webcam ===
# video = cv2.VideoCapture(0)

# reconhecido = False

# while True:
#     success, frame = video.read()
#     if not success:
#         break

#     if not reconhecido:
#         vetor_usuario = extrair_landmarks(frame)

#         if vetor_usuario is not None:
#             distancia = comparar_gestos(vetor_usuario, vetor_referencia)

#             limiar = 0.4
#             if distancia < limiar:
#                 reconhecido = True
#                 texto = "✅ Gesto reconhecido com sucesso!"
#                 cor = (0, 255, 0)
#             else:
#                 texto = f"Gesto incorreto (distância={distancia:.3f})"
#                 cor = (0, 0, 255)
#         else:
#             texto = "Mão não detectada"
#             cor = (0, 255, 255)
#     else:
#         texto = "✅ Gesto já reconhecido!"
#         cor = (0, 255, 0)

#     cv2.putText(frame, texto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)
#     cv2.imshow("Reconhecimento de Gesto", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# video.release()
# cv2.destroyAllWindows()
