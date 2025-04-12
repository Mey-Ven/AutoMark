from src.face_recognition_module import FaceRecognitionModule

# Initialiser le module
print("Initialisation du module...")
module = FaceRecognitionModule('./data')
print("Module initialisé avec succès")

# Vérifier si le module utilise notre solution simplifiée
print("Mode simplifié:", getattr(module, 'simple_mode', False))

# Vérifier si le module est prêt pour l'entraînement
print("Modèle entraîné:", getattr(module, 'model_trained', False))

# Afficher les attributs du module
print("Attributs du module:", [attr for attr in dir(module) if not attr.startswith('__')])
