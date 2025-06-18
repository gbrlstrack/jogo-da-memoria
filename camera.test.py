import cv2

print("🔍 Procurando câmeras disponíveis...")
for index in range(5):  # Testa os índices de 0 a 4
    cap = cv2.VideoCapture(index)
    if cap.read()[0]:
        print(f"✅ Câmera encontrada no índice {index}")
        cap.release()
    else:
        print(f"❌ Nenhuma câmera no índice {index}")