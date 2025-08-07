import random
import cv2
import pygame
import sys
import mediapipe as mp
import numpy as np
import os

# ===================== MEDIA PIPE =====================
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(max_num_hands=1)
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

# ===================== PYGAME CONFIG =====================
pygame.init()
largura = 1280
altura = 720
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Jogo de Gestos")

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
fonte = pygame.font.SysFont(None, 60)
fonte_grande = pygame.font.SysFont(None, 80)

def desenhar_texto(texto, font, cor, surface, x, y):
    textoobj = font.render(texto, True, cor)
    textorect = textoobj.get_rect(center=(x, y))
    surface.blit(textoobj, textorect)

def desenhar_gradiente(surface, cor_topo, cor_base):
    """Cria um fundo gradiente vertical."""
    for y in range(altura):
        cor = (
            cor_topo[0] + (cor_base[0] - cor_topo[0]) * y // altura,
            cor_topo[1] + (cor_base[1] - cor_topo[1]) * y // altura,
            cor_topo[2] + (cor_base[2] - cor_topo[2]) * y // altura
        )
        pygame.draw.line(surface, cor, (0, y), (largura, y))

def desenhar_botao(botao, texto, mouse_pos):
    """Desenha botão com efeito hover."""
    cor_normal = (180, 180, 180)
    cor_hover = (220, 220, 220)
    cor = cor_hover if botao.collidepoint(mouse_pos) else cor_normal
    pygame.draw.rect(tela, cor, botao, border_radius=15)
    pygame.draw.rect(tela, PRETO, botao, 3, border_radius=15)
    desenhar_texto(texto, fonte, PRETO, tela, botao.centerx, botao.centery)

def desenhar_barra_progresso(surface, x, y, largura, altura, progresso, cor_fundo=(200,200,200), cor_barra=(0,180,0)):
    """Desenha uma barra de progresso horizontal."""
    pygame.draw.rect(surface, cor_fundo, (x, y, largura, altura), border_radius=8)
    largura_preenchida = int(largura * max(0, min(1, progresso)))
    pygame.draw.rect(surface, cor_barra, (x, y, largura_preenchida, altura), border_radius=8)
    pygame.draw.rect(surface, PRETO, (x, y, largura, altura), 2, border_radius=8)

# ===================== MENUS =====================
def menu_selecao_palavras():
    selecionado = None
    botoes = []

    linhas, colunas = 3, 2
    largura_botao, altura_botao = 200, 100
    espaco_x, espaco_y = 250, 150
    start_x = (largura - (colunas * largura_botao + (colunas - 1) * (espaco_x - largura_botao))) // 2
    start_y = 200

    num_botao = 1
    for linha in range(linhas):
        for coluna in range(colunas):
            x = start_x + coluna * espaco_x
            y = start_y + linha * espaco_y
            botoes.append((num_botao, pygame.Rect(x, y, largura_botao, altura_botao)))
            num_botao += 1

    while selecionado is None:
        desenhar_gradiente(tela, (100, 150, 255), (180, 220, 255))
        desenhar_texto("Escolha o número de palavras", fonte_grande, PRETO, tela, largura // 2, 100)

        mouse_pos = pygame.mouse.get_pos()
        for i, botao in botoes:
            desenhar_botao(botao, str(i), mouse_pos)

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
        desenhar_gradiente(tela, (100, 150, 255), (180, 220, 255))
        desenhar_texto("Jogo de Gestos", fonte_grande, PRETO, tela, largura // 2, 150)

        botao_jogar = pygame.Rect(largura // 2 - 100, altura // 2 - 50, 200, 100)
        mouse_pos = pygame.mouse.get_pos()
        desenhar_botao(botao_jogar, "Jogar", mouse_pos)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.collidepoint(evento.pos):
                    num_palavras = menu_selecao_palavras()
                    jogo(num_palavras)

        pygame.display.update()

# ===================== GAMEPLAY =====================
def jogo(num_palavras):
    import time  # Importa apenas dentro da função

    videos = sorted([f for f in os.listdir('assets') if f.endswith('.mp4')])
    videos = videos[:num_palavras]
    random.shuffle(videos)

    score = 0  # Inicializa o score

    # Exibe vídeos das palavras
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

            desenhar_gradiente(tela, (240, 240, 255), (200, 220, 255))
            nome_palavra = os.path.splitext(video_nome)[0]
            desenhar_texto(f"Assista ao gesto para:", fonte, PRETO, tela, largura // 2, 80)
            desenhar_texto(nome_palavra.capitalize(), fonte, (0, 0, 150), tela, largura // 2, 150)
            tela.blit(surface, (largura // 2 - 320, altura // 2 - 180))

            pygame.display.update()
            pygame.time.delay(int(1000 / cap.get(cv2.CAP_PROP_FPS)))

        cap.release()

    webcam = cv2.VideoCapture(0)
    current_gesture_index = 0
    gesto_reconhecido = False

    while current_gesture_index < len(videos):
        nome_palavra = os.path.splitext(videos[current_gesture_index])[0]
        start_time = time.time()  # Início do tempo para o gesto

        reconhecido = False
        while not reconhecido:
            desenhar_gradiente(tela, (240, 240, 255), (200, 220, 255))

            desenhar_texto(f"Faça o gesto para:", fonte, PRETO, tela, largura // 2, 60)
            desenhar_texto(nome_palavra.capitalize(), fonte, (0, 0, 180), tela, largura // 2, 120)
            desenhar_texto(f"Score: {score}", fonte, (0, 100, 0), tela, largura // 2, 170)

            ret, frame = webcam.read()
            semelhanca = 0.0
            status_text = ""
            status_color = (200, 0, 0)

            if ret:
                vetor_usuario = extrair_landmarks(frame)
                caminho_vetor = os.path.join("results", f"{nome_palavra}.npy")

                if os.path.exists(caminho_vetor):
                    vetor_referencia = np.load(caminho_vetor)
                    distancia = comparar_gestos(vetor_usuario, vetor_referencia)
                    semelhanca = max(0, 1 - distancia)

                    if distancia < 0.5:
                        tempo_decorrido = time.time() - start_time
                        pontos = max(10, int(100 - tempo_decorrido * 20))  # penalização por tempo
                        score += pontos

                        status_text = f"✅ Gesto reconhecido! +{pontos} pontos"
                        status_color = (0, 180, 0)
                        reconhecido = True
                    else:
                        status_text = "✋ Continue tentando!"
                        status_color = (200, 0, 0)
                else:
                    status_text = "⚠️ Vetor de referência não encontrado"
                    status_color = (255, 165, 0)

                desenhar_barra_progresso(tela, largura//2 - 200, 200, 400, 25, semelhanca)
                pygame.draw.rect(tela, status_color, (largura//2 - 250, 240, 500, 50), border_radius=10)
                desenhar_texto(status_text, fonte, BRANCO, tela, largura // 2, 265)

                frame = cv2.resize(frame, (320, 240))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))
                pygame.draw.rect(tela, PRETO, (largura // 2 - 160, 320, 320, 240), 3, border_radius=12)
                tela.blit(surface, (largura // 2 - 160, 320))

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    webcam.release()
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    webcam.release()
                    return

            pygame.display.update()
            pygame.time.delay(30)

        pygame.time.delay(1000)
        current_gesture_index += 1

    webcam.release()
    desenhar_gradiente(tela, (240, 240, 255), (200, 220, 255))
    desenhar_texto("🎉 Parabéns! Você completou todos os gestos!", fonte, PRETO, tela, largura // 2, altura // 2 - 40)
    desenhar_texto(f"🏆 Score Final: {score}", fonte, (0, 120, 0), tela, largura // 2, altura // 2 + 40)
    pygame.display.update()
    pygame.time.delay(4000)

# ===================== EXECUÇÃO =====================
menu()
