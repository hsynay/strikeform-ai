import cv2
import mediapipe as mp
import numpy as np
import math

# açı hesaplama kısmı kosinüs teoremiyle 3d uzayda yaptım çünkü mediapipe 3d koordinatlar veriyor
def calculate_angle_3d(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

# mediapipe ayarları
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# ekranı 1920x1080 olarak ayarladım arayüz kaymasın diye
TARGET_W, TARGET_H = 1920, 1080

# Test videosu
video_path = 'Videos/Messi_training.mp4' 
# video_path = 'Videos/Messi_Knuckleball.mp4'
# video_path = 'Videos/CR7_Knuckleball.mp4'
# video_path = 'Videos/Freekick_training.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"HATA: {video_path} açılamadı")
    exit()

print("KONTROLLER: [SPACE] Oynat/Durdur | [ESC] Çıkış")
print("Fix your form. Maybe you can play for Barcelona!")

is_paused = False
resized_frame = None
x_offset = 0
y_offset = 0
new_w = 0
new_h = 0

# tam ekran pencere ayarı
cv2.namedWindow('SportForm AI', cv2.WINDOW_NORMAL)
cv2.resizeWindow('SportForm AI', TARGET_W, TARGET_H)

# video döngüsü başlıyor
while True:
    if not is_paused:
        # videoyu oynatıyoruz
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # video bitince başa sar
            continue
            
        # videonun en boy oranını bozmadan 1080pye sığdırıyorum
        frame_h, frame_w = frame.shape[:2]
        scale = min(TARGET_W / frame_w, TARGET_H / frame_h)
        new_w = int(frame_w * scale)
        new_h = int(frame_h * scale)
        
        # yeniden boyutlandırma
        resized_frame = cv2.resize(frame, (new_w, new_h))
        
        # arkaya siyah boş bir tuval açtım
        canvas = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.uint8)
        
        # videoyu tuvalin tam ortasına yerleştir
        x_offset = (TARGET_W - new_w) // 2
        y_offset = (TARGET_H - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_frame

        current_canvas = canvas.copy()

        # üstteki yönlendirme yazısı 
        cv2.rectangle(current_canvas, (0, 0), (TARGET_W, 80), (0, 0, 0), -1)
        cv2.putText(current_canvas, "PLAYING - Press [SPACE] to Pause & Analyze", (40, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        
        cv2.imshow('SportForm AI', current_canvas)

    # tuş kontrolleri
    delay = 0 if is_paused else 30
    key = cv2.waitKey(delay) & 0xFF

    if key == 27: # esc ile çıkış(ascıı kodu 27)
        break
        
    elif key == ord(' '): 
        # space ile videoyu durdurup başlatma
        is_paused = not is_paused
        
        if is_paused:
            # video durunca analiz kısmı başlıyor
            analyze_frame = resized_frame.copy()
            image_rgb = cv2.cvtColor(analyze_frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            posture_status = "ANALYSIS PENDING..."
            feedback_msg = "Could not detect player."
            ui_color = (0, 0, 255)
            
            # analiz için yeni tuval
            final_canvas = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.uint8)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                def get_coords(l_name): return [landmarks[l_name.value].x, landmarks[l_name.value].y, landmarks[l_name.value].z]
                
                # mediapipe kordinatlarını dev tuvale uyduran fonksiyon
                def get_2d(coords): return (int(coords[0] * new_w) + x_offset, int(coords[1] * new_h) + y_offset)

                l_shoulder, l_hip, l_knee, l_ankle = get_coords(mp_pose.PoseLandmark.LEFT_SHOULDER), get_coords(mp_pose.PoseLandmark.LEFT_HIP), get_coords(mp_pose.PoseLandmark.LEFT_KNEE), get_coords(mp_pose.PoseLandmark.LEFT_ANKLE)
                r_shoulder, r_hip, r_knee, r_ankle = get_coords(mp_pose.PoseLandmark.RIGHT_SHOULDER), get_coords(mp_pose.PoseLandmark.RIGHT_HIP), get_coords(mp_pose.PoseLandmark.RIGHT_KNEE), get_coords(mp_pose.PoseLandmark.RIGHT_ANKLE)

                # hangi ayağı kullanıyorsa onu destek ayağı seç
                if l_ankle[1] > r_ankle[1]:
                    shoulder, hip, knee, ankle = l_shoulder, l_hip, l_knee, l_ankle
                    active_leg = "LEFT"
                else:
                    shoulder, hip, knee, ankle = r_shoulder, r_hip, r_knee, r_ankle
                    active_leg = "RIGHT"

                body_angle = calculate_angle_3d(shoulder, hip, knee)
                leg_angle = calculate_angle_3d(hip, knee, ankle)
                
                h_2d, k_2d = get_2d(hip), get_2d(knee)

                # açı kuralları araştırmalara göre yazdım
                if leg_angle < 145:
                    posture_status = "FORM ERROR: KNEE COLLAPSE"
                    feedback_msg = f"Support leg ({active_leg}) bent too much. Straighten knee."
                    ui_color = (0, 0, 255)
                elif leg_angle > 175:
                    posture_status = "FORM ERROR: LOCKED KNEE" 
                    feedback_msg = f"Injury risk! Flex support knee ({active_leg}) slightly."
                    ui_color = (0, 0, 255)
                elif body_angle > 165: 
                    posture_status = "FORM ERROR: LEANING BACK"
                    feedback_msg = "Loss of balance. You will shoot the ball too high!"
                    ui_color = (0, 165, 255)
                elif body_angle < 135:
                    posture_status = "FORM ERROR: OVER-LEANING"
                    feedback_msg = "Leaning too far forward over the ball. Open your chest."
                    ui_color = (0, 165, 255)
                else:
                    posture_status = "PERFECT 3D STRIKE FORM"
                    feedback_msg = "Ideal biomechanical angles for maximum power transfer!"
                    ui_color = (0, 255, 0)

                # iskeleti sadece analizi yapılan videonun üzerine çiz
                mp_draw.draw_landmarks(analyze_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                       mp_draw.DrawingSpec(color=ui_color, thickness=4, circle_radius=5), 
                                       mp_draw.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2))

                # analiz bitince videoyu ortala
                final_canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = analyze_frame

                # açıları tam eklemlerin üstüne yazdır
                cv2.putText(final_canvas, f"Body: {int(body_angle)}", (h_2d[0]+15, h_2d[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(final_canvas, f"Knee: {int(leg_angle)}", (k_2d[0]+15, k_2d[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            
            else:
                # oyuncu yoksa normal videoyu bas
                final_canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = analyze_frame

            # arayüz kısmı
            cv2.rectangle(final_canvas, (0, 0), (TARGET_W, 160), (0, 0, 0), -1)
            
            # başlık
            cv2.putText(final_canvas, posture_status, (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, ui_color, 4, cv2.LINE_AA)
            # hata mesajı falan
            cv2.putText(final_canvas, feedback_msg, (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
            # sağ üstteki esc yazısı
            cv2.putText(final_canvas, "[SPACE] Resume | [ESC] Exit", (TARGET_W - 500, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2, cv2.LINE_AA)

            cv2.imshow('SportForm AI', final_canvas)

cap.release()
cv2.destroyAllWindows()