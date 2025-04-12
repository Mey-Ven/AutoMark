from src.face_recognition_module import FaceRecognitionModule

# Initialiser le module
print("Initialisation du module...")
module = FaceRecognitionModule('./data')
print("Module initialisé avec succès")

# Vérifier les attributs critiques
print("face_detection_model:", getattr(module, 'face_detection_model', 'Non défini'))
print("recognition_tolerance:", getattr(module, 'recognition_tolerance', 'Non défini'))
print("liveness_enabled:", getattr(module, 'liveness_enabled', 'Non défini'))
print("blink_detection_enabled:", getattr(module, 'blink_detection_enabled', 'Non défini'))
print("movement_detection_enabled:", getattr(module, 'movement_detection_enabled', 'Non défini'))
print("texture_analysis_enabled:", getattr(module, 'texture_analysis_enabled', 'Non défini'))
