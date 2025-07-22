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


def comparar_gestos(vetor1, vetor2):
    if vetor1 is None or vetor2 is None:
        return float('inf')
    return np.linalg.norm(vetor1 - vetor2)


def extrair_landmarks(frame_video):
    frame_rgb = cv2.cvtColor(frame_video, cv2.COLOR_BGR2RGB)
    result = hands_detector.process(frame_rgb)

    if result.multi_hand_landmarks:
        landmarks = []
        for lm in result.multi_hand_landmarks[0].landmark:
            landmarks.append([lm.x, lm.y, lm.z])

        landmarks = np.array(landmarks)
        landmarks -= landmarks[0]  # Normaliza para o pulso (landmark 0)
        return landmarks.flatten()
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

    # Configura grid
    linhas = 3
    colunas = 2
    espaco_x = 250
    espaco_y = 150
    largura_botao = 200
    altura_botao = 100
    start_x = (largura - (colunas * largura_botao + (colunas - 1) * (espaco_x - largura_botao))) // 2
    start_y = 200  # espaço para o título acima

    num_botao = 1
    for linha in range(linhas):
        for coluna in range(colunas):
            x = start_x + coluna * espaco_x
            y = start_y + linha * espaco_y
            botoes.append((num_botao, pygame.Rect(x, y, largura_botao, altura_botao)))
            num_botao += 1

    while selecionado is None:
        tela.fill(BRANCO)
        desenhar_texto("Escolha o número de palavras", fonte, PRETO, tela, largura // 2, 100)

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


def jogo(num_palavras):
    videos = sorted([f for f in os.listdir('assets') if f.endswith('.mp4')])
    videos = videos[:num_palavras]
    random.shuffle(videos)

    for video_nome in videos:
        video_path = os.path.join("assets", video_nome)
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))

            tela.fill(BRANCO)
            nome_palavra = os.path.splitext(video_nome)[0]
            desenhar_texto(nome_palavra.capitalize(), fonte, PRETO, tela, largura // 2, 150)
            tela.blit(surface, (largura // 2 - 320, altura // 2 - 180))

            pygame.display.update()
            pygame.time.delay(int(1000 / cap.get(cv2.CAP_PROP_FPS)))

        cap.release()

    webcam = cv2.VideoCapture(1)  # Troque para o índice da sua câmera USB se necessário
    current_gesture_index = 0
    gesto_reconhecido = False

    while current_gesture_index < len(videos):
        tela.fill(BRANCO)

        nome_palavra = os.path.splitext(videos[current_gesture_index])[0]
        desenhar_texto(f"Faça o gesto para:", fonte, PRETO, tela, largura // 2, 100)
        desenhar_texto(nome_palavra.capitalize(), fonte, (0, 0, 255), tela, largura // 2, 180)

        ret, frame = webcam.read()
        if ret:
            vetor_usuario = extrair_landmarks(frame)
            caminho_vetor = os.path.join("results", f"{nome_palavra}.npy")

            if os.path.exists(caminho_vetor):
                vetor_referencia = np.load(caminho_vetor)
                distancia = comparar_gestos(vetor_usuario, vetor_referencia)
                semelhanca = max(0, 1 - distancia)
                desenhar_texto(f"Semelhança: {semelhanca:.2f}", fonte, PRETO, tela, largura // 2, 350)

                if distancia < 0.5:
                    gesto_reconhecido = True
                    status_text = "✅ Gesto reconhecido!"
                    status_color = (0, 180, 0)
                else:
                    status_text = "✋ Tente imitar melhor o gesto!"
                    status_color = (200, 0, 0)
            else:
                status_text = "⚠️ Vetor de referência não encontrado"
                status_color = (255, 165, 0)

            desenhar_texto(status_text, fonte, status_color, tela, largura // 2, 420)

            frame = cv2.resize(frame, (320, 240))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))
            tela.blit(surface, (largura // 2 - 160, 470))

        if gesto_reconhecido:
            pygame.time.delay(1000)
            current_gesture_index += 1
            gesto_reconhecido = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                webcam.release()
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    webcam.release()
                    return

        pygame.display.update()
        pygame.time.delay(30)

    webcam.release()
    tela.fill(BRANCO)
    desenhar_texto("🎉 Parabéns! Você completou todos os gestos!", fonte, PRETO, tela, largura // 2, altura // 2)
    pygame.display.update()
    pygame.time.delay(3000)


# Executa o menu
menu()
