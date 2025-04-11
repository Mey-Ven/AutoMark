import cv2
print('OpenCV version:', cv2.__version__)
print('cv2.face attributes:', dir(cv2.face))
try:
    face = cv2.face.LBPHFaceRecognizer_create()
    print('cv2.face.LBPHFaceRecognizer_create disponible')
except Exception as e:
    print('Erreur:', e)
