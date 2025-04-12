import os
import pandas as pd
import hashlib
import datetime
from typing import Dict, Optional, List, Tuple

class AuthManager:
    """
    Gestionnaire d'authentification pour AutoMark.
    Gère les utilisateurs, les rôles et les sessions.
    """

    def __init__(self, data_dir: str):
        """
        Initialise le gestionnaire d'authentification.

        Args:
            data_dir: Répertoire contenant les données utilisateur
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.csv')
        self.roles_file = os.path.join(data_dir, 'user_roles.csv')
        self.mappings_file = os.path.join(data_dir, 'user_mappings.csv')

        # Charger les données
        self.reload_data()

    def reload_data(self) -> None:
        """Recharge les données utilisateur depuis les fichiers."""
        if os.path.exists(self.users_file):
            self.users_df = pd.read_csv(self.users_file)
        else:
            self.users_df = pd.DataFrame(columns=['UserID', 'Username', 'PasswordHash', 'Role',
                                                 'FirstName', 'LastName', 'Email', 'LastLogin',
                                                 'FailedAttempts', 'LockedUntil', 'AccountStatus'])

        if os.path.exists(self.roles_file):
            self.roles_df = pd.read_csv(self.roles_file)
        else:
            self.roles_df = pd.DataFrame(columns=['Role', 'Description', 'Permissions'])

        if os.path.exists(self.mappings_file):
            self.mappings_df = pd.read_csv(self.mappings_file)
        else:
            self.mappings_df = pd.DataFrame(columns=['UserID', 'EntityID', 'EntityType'])

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Authentifie un utilisateur.

        Args:
            username: Nom d'utilisateur
            password: Mot de passe (en clair)

        Returns:
            Tuple (succès, informations utilisateur)
        """
        # Vérifier si l'utilisateur existe
        user = self.users_df[self.users_df['Username'] == username]
        if len(user) == 0:
            return False, None

        user_id = user.iloc[0]['UserID']
        idx = user.index[0]

        # Vérifier si le compte est verrouillé
        if 'LockedUntil' in user.iloc[0] and 'AccountStatus' in user.iloc[0]:
            locked_until = user.iloc[0].get('LockedUntil')
            account_status = user.iloc[0].get('AccountStatus')

            if account_status == 'locked' and locked_until:
                try:
                    locked_until_dt = datetime.datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S")
                    if locked_until_dt > datetime.datetime.now():
                        return False, {"error": "Account locked", "locked_until": locked_until}
                    else:
                        # Réinitialiser le verrouillage si la période est terminée
                        self.users_df.at[idx, 'FailedAttempts'] = 0
                        self.users_df.at[idx, 'AccountStatus'] = 'active'
                        self.users_df.at[idx, 'LockedUntil'] = None
                        self.users_df.to_csv(self.users_file, index=False)
                except (ValueError, TypeError):
                    pass

        # Récupérer le hash stocké
        stored_hash = user.iloc[0]['PasswordHash']

        # Vérifier le mot de passe avec SHA-256
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        auth_success = stored_hash == password_hash

        if not auth_success:
            # Incrémenter le compteur d'échecs et vérifier le verrouillage
            failed_attempts = user.iloc[0].get('FailedAttempts', 0)
            if pd.isna(failed_attempts):
                failed_attempts = 0

            failed_attempts += 1
            self.users_df.at[idx, 'FailedAttempts'] = failed_attempts

            # Verrouiller le compte après 5 tentatives échouées
            if failed_attempts >= 5:
                locked_until = (datetime.datetime.now() + datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
                self.users_df.at[idx, 'LockedUntil'] = locked_until
                self.users_df.at[idx, 'AccountStatus'] = 'locked'
                self.users_df.to_csv(self.users_file, index=False)
                return False, {"error": "Account locked", "locked_until": locked_until}

            self.users_df.to_csv(self.users_file, index=False)
            return False, None

        # Réinitialiser le compteur d'échecs en cas de succès
        self.users_df.at[idx, 'FailedAttempts'] = 0
        if 'AccountStatus' in self.users_df.columns:
            self.users_df.at[idx, 'AccountStatus'] = 'active'

        # Mettre à jour la date de dernière connexion
        self._update_last_login(user_id)

        # Récupérer les informations utilisateur
        user_info = self._get_user_info(user_id)

        return True, user_info

    def _update_last_login(self, user_id: str) -> None:
        """
        Met à jour la date de dernière connexion d'un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        idx = self.users_df[self.users_df['UserID'] == user_id].index[0]
        self.users_df.at[idx, 'LastLogin'] = now
        self.users_df.to_csv(self.users_file, index=False)

    def _get_user_info(self, user_id: str) -> Dict:
        """
        Récupère les informations complètes d'un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur

        Returns:
            Dictionnaire contenant les informations utilisateur
        """
        user = self.users_df[self.users_df['UserID'] == user_id].iloc[0]
        role = user['Role']

        # Récupérer les permissions du rôle
        role_info = self.roles_df[self.roles_df['Role'] == role].iloc[0]
        permissions = role_info['Permissions'].split(',')

        # Récupérer les entités associées à l'utilisateur
        mappings = self.mappings_df[self.mappings_df['UserID'] == user_id]
        entities = {}

        for _, mapping in mappings.iterrows():
            entity_type = mapping['EntityType']
            entity_id = mapping['EntityID']

            if entity_type not in entities:
                entities[entity_type] = []

            entities[entity_type].append(entity_id)

        # Construire le dictionnaire d'informations utilisateur
        user_info = {
            'user_id': user_id,
            'username': user['Username'],
            'role': role,
            'first_name': user['FirstName'],
            'last_name': user['LastName'],
            'email': user['Email'],
            'permissions': permissions,
            'entities': entities,
            'last_login': user['LastLogin']
        }

        return user_info

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Récupère les informations d'un utilisateur par son ID.

        Args:
            user_id: Identifiant de l'utilisateur

        Returns:
            Dictionnaire contenant les informations utilisateur ou None si non trouvé
        """
        user = self.users_df[self.users_df['UserID'] == user_id]
        if len(user) == 0:
            return None

        return self._get_user_info(user_id)

    def get_users_by_role(self, role: str) -> List[Dict]:
        """
        Récupère tous les utilisateurs ayant un rôle spécifique.

        Args:
            role: Rôle à rechercher

        Returns:
            Liste de dictionnaires contenant les informations utilisateur
        """
        users = self.users_df[self.users_df['Role'] == role]
        return [self._get_user_info(user_id) for user_id in users['UserID']]

    def create_user(self, username: str, password: str, role: str,
                   first_name: str, last_name: str, email: str) -> Tuple[bool, str]:
        """
        Crée un nouvel utilisateur.

        Args:
            username: Nom d'utilisateur
            password: Mot de passe (en clair)
            role: Rôle de l'utilisateur
            first_name: Prénom
            last_name: Nom
            email: Adresse email

        Returns:
            Tuple (succès, message ou ID utilisateur)
        """
        # Vérifier si le nom d'utilisateur existe déjà
        if len(self.users_df[self.users_df['Username'] == username]) > 0:
            return False, "Ce nom d'utilisateur existe déjà."

        # Vérifier si le rôle existe
        if len(self.roles_df[self.roles_df['Role'] == role]) == 0:
            return False, f"Le rôle '{role}' n'existe pas."

        # Générer un nouvel ID utilisateur
        user_id = self._generate_user_id()

        # Hacher le mot de passe avec SHA-256
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Créer le nouvel utilisateur
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_user = pd.DataFrame({
            'UserID': [user_id],
            'Username': [username],
            'PasswordHash': [password_hash],
            'Role': [role],
            'FirstName': [first_name],
            'LastName': [last_name],
            'Email': [email],
            'LastLogin': [now],
            'FailedAttempts': [0],
            'LockedUntil': [None],
            'AccountStatus': ['active']
        })

        # Ajouter l'utilisateur à la base de données
        self.users_df = pd.concat([self.users_df, new_user], ignore_index=True)
        self.users_df.to_csv(self.users_file, index=False)

        return True, user_id

    def update_user(self, user_id: str, **kwargs) -> Tuple[bool, str]:
        """
        Met à jour les informations d'un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur
            **kwargs: Champs à mettre à jour (username, role, first_name, last_name, email, password)

        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'utilisateur existe
        user_idx = self.users_df[self.users_df['UserID'] == user_id].index
        if len(user_idx) == 0:
            return False, "Utilisateur non trouvé."

        idx = user_idx[0]

        # Mettre à jour les champs spécifiés
        for field, value in kwargs.items():
            if field == 'password':
                # Hacher le nouveau mot de passe
                password_hash = hashlib.sha256(value.encode()).hexdigest()
                self.users_df.at[idx, 'PasswordHash'] = password_hash
            elif field in ['username', 'role', 'first_name', 'last_name', 'email']:
                # Convertir le nom du champ en format camelCase pour correspondre aux colonnes
                column = field[0].upper() + field[1:] if field != 'username' else 'Username'
                self.users_df.at[idx, column] = value

        # Sauvegarder les modifications
        self.users_df.to_csv(self.users_file, index=False)

        return True, "Utilisateur mis à jour avec succès."

    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """
        Supprime un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur

        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'utilisateur existe
        user_idx = self.users_df[self.users_df['UserID'] == user_id].index
        if len(user_idx) == 0:
            return False, "Utilisateur non trouvé."

        # Supprimer l'utilisateur
        self.users_df = self.users_df[self.users_df['UserID'] != user_id]
        self.users_df.to_csv(self.users_file, index=False)

        # Supprimer les mappings associés
        self.mappings_df = self.mappings_df[self.mappings_df['UserID'] != user_id]
        self.mappings_df.to_csv(self.mappings_file, index=False)

        return True, "Utilisateur supprimé avec succès."

    def add_entity_mapping(self, user_id: str, entity_id: str, entity_type: str) -> Tuple[bool, str]:
        """
        Ajoute une association entre un utilisateur et une entité.

        Args:
            user_id: Identifiant de l'utilisateur
            entity_id: Identifiant de l'entité (cours, étudiant, etc.)
            entity_type: Type d'entité ('course', 'student', etc.)

        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'utilisateur existe
        if len(self.users_df[self.users_df['UserID'] == user_id]) == 0:
            return False, "Utilisateur non trouvé."

        # Vérifier si le mapping existe déjà
        existing = self.mappings_df[
            (self.mappings_df['UserID'] == user_id) &
            (self.mappings_df['EntityID'] == entity_id) &
            (self.mappings_df['EntityType'] == entity_type)
        ]

        if len(existing) > 0:
            return False, "Cette association existe déjà."

        # Ajouter le nouveau mapping
        new_mapping = pd.DataFrame({
            'UserID': [user_id],
            'EntityID': [entity_id],
            'EntityType': [entity_type]
        })

        self.mappings_df = pd.concat([self.mappings_df, new_mapping], ignore_index=True)
        self.mappings_df.to_csv(self.mappings_file, index=False)

        return True, "Association ajoutée avec succès."

    def remove_entity_mapping(self, user_id: str, entity_id: str, entity_type: str) -> Tuple[bool, str]:
        """
        Supprime une association entre un utilisateur et une entité.

        Args:
            user_id: Identifiant de l'utilisateur
            entity_id: Identifiant de l'entité
            entity_type: Type d'entité

        Returns:
            Tuple (succès, message)
        """
        # Vérifier si le mapping existe
        existing = self.mappings_df[
            (self.mappings_df['UserID'] == user_id) &
            (self.mappings_df['EntityID'] == entity_id) &
            (self.mappings_df['EntityType'] == entity_type)
        ]

        if len(existing) == 0:
            return False, "Cette association n'existe pas."

        # Supprimer le mapping
        self.mappings_df = self.mappings_df[
            ~((self.mappings_df['UserID'] == user_id) &
              (self.mappings_df['EntityID'] == entity_id) &
              (self.mappings_df['EntityType'] == entity_type))
        ]

        self.mappings_df.to_csv(self.mappings_file, index=False)

        return True, "Association supprimée avec succès."

    def _generate_user_id(self) -> str:
        """
        Génère un nouvel identifiant utilisateur unique.

        Returns:
            Nouvel identifiant utilisateur
        """
        if len(self.users_df) == 0:
            return "U001"

        # Récupérer le dernier ID et incrémenter
        last_id = self.users_df['UserID'].max()
        num = int(last_id[1:]) + 1
        return f"U{num:03d}"

    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique.

        Args:
            user_id: Identifiant de l'utilisateur
            permission: Permission à vérifier

        Returns:
            True si l'utilisateur a la permission, False sinon
        """
        user_info = self.get_user_by_id(user_id)
        if not user_info:
            return False

        return permission in user_info['permissions']

    def get_user_entities(self, user_id: str, entity_type: str) -> List[str]:
        """
        Récupère toutes les entités d'un type spécifique associées à un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur
            entity_type: Type d'entité ('course', 'student', etc.)

        Returns:
            Liste des identifiants d'entités
        """
        user_info = self.get_user_by_id(user_id)
        if not user_info or 'entities' not in user_info:
            return []

        return user_info['entities'].get(entity_type, [])
