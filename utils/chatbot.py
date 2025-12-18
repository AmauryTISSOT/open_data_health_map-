"""
HealthMap Chatbot - Assistant intelligent d'orientation médicale
Utilise Ollama Mistral pour analyser les symptômes et recommander des professionnels
"""

import requests
from typing import Optional
import pandas as pd
from utils.data import load_data
from utils.metrics import professionals_by_departement


class HealthMapChatbot:
    """Assistant IA pour l'orientation vers les professionnels de santé"""

    # Mapping symptômes → spécialités
    SYMPTOMS_TO_SPECIALTIES = {
        "mal de tête": ["généraliste", "cardiologue", "neurologue"],
        "migraines": ["neurologue", "généraliste"],
        "mal de dents": ["dentiste"],
        "mal au ventre": ["généraliste", "gastro-entérologue"],
        "douleur": ["généraliste", "rhumatologue", "kinésithérapeute"],
        "grippe": ["généraliste"],
        "rhume": ["généraliste"],
        "toux": ["généraliste", "pneumologue"],
        "fièvre": ["généraliste"],
        "cœur": ["cardiologue", "généraliste"],
        "tensio": ["cardiologue", "généraliste"],
        "diabète": ["endocrinologue", "généraliste"],
        "peau": ["dermatologue", "généraliste"],
        "yeux": ["ophtalmologue"],
        "oreilles": ["oto-rhino", "généraliste"],
        "articulation": ["rhumatologue", "kinésithérapeute"],
        "dos": ["rhumatologue", "kinésithérapeute", "généraliste"],
        "jambes": ["angiologue", "phlébologue", "kinésithérapeute"],
        "stress": ["psychiatre", "généraliste", "psychologue"],
        "dépression": ["psychiatre", "psychologue", "généraliste"],
        "anxiété": ["psychiatre", "psychologue", "généraliste"],
        "allergie": ["allergie", "généraliste"],
        "grossesse": ["gynécologue", "généraliste"],
        "gynéco": ["gynécologue"],
    }

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialise le chatbot

        Args:
            ollama_url: URL du serveur Ollama
        """
        self.ollama_url = ollama_url
        self.model = "mistral"
        self.df_professionals = None
        self.df_by_dept = None
        self._load_data()

    def _load_data(self):
        """Charge les données des professionnels de santé"""
        try:
            self.df_professionals = load_data()
            self.df_by_dept = professionals_by_departement(self.df_professionals)
        except Exception as e:
            print(f"Erreur chargement données: {e}")

    def _query_ollama(self, prompt: str) -> str:
        """
        Envoie une requête au serveur Ollama

        Args:
            prompt: Le texte à traiter

        Returns:
            Réponse du modèle
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except requests.ConnectionError:
            return (
                "❌ Erreur: Serveur Ollama non accessible. "
                f"Vérifiez que Ollama est lancé sur {self.ollama_url}"
            )
        except Exception as e:
            return f"❌ Erreur Ollama: {str(e)}"

    def extract_symptoms(self, user_input: str) -> list[str]:
        """
        Extrait les symptômes du message utilisateur

        Args:
            user_input: Message de l'utilisateur

        Returns:
            Liste des symptômes détectés
        """
        detected = []
        user_lower = user_input.lower()

        for symptom in self.SYMPTOMS_TO_SPECIALTIES.keys():
            if symptom in user_lower:
                detected.append(symptom)

        return detected

    def get_recommended_specialties(self, symptoms: list[str]) -> list[str]:
        """
        Recommande des spécialités basées sur les symptômes

        Args:
            symptoms: Liste des symptômes

        Returns:
            Liste des spécialités recommandées
        """
        specialties_set = set()

        for symptom in symptoms:
            if symptom in self.SYMPTOMS_TO_SPECIALTIES:
                specialties_set.update(self.SYMPTOMS_TO_SPECIALTIES[symptom])

        return sorted(list(specialties_set))

    def analyze_region_coverage(self, departement: str) -> dict:
        """
        Analyse la couverture médicale d'une région

        Args:
            departement: Code du département

        Returns:
            Analyse de la couverture
        """
        if self.df_professionals is None:
            return {"erreur": "Données indisponibles"}

        dept_data = self.df_professionals[
            self.df_professionals["departement"] == departement
        ]

        if dept_data.empty:
            return {"erreur": f"Aucune donnée pour {departement}"}

        total_professionals = len(dept_data)
        avg_professionals = self.df_by_dept["nb_professionnels"].mean()

        coverage_level = "✅ Bien couvert"
        if total_professionals < avg_professionals * 0.7:
            coverage_level = "⚠️ Sous-doté"
        elif total_professionals < avg_professionals * 0.9:
            coverage_level = "⚠️ Partiellement couvert"

        return {
            "departement": departement,
            "nb_professionnels": total_professionals,
            "moyenne_nationale": round(avg_professionals, 1),
            "statut": coverage_level,
            "pourcentage_moyenne": round(
                (total_professionals / avg_professionals) * 100, 1
            ),
        }

    def generate_response(
        self, user_message: str, departement: Optional[str] = None
    ) -> dict:
        """
        Génère une réponse personnalisée du chatbot

        Args:
            user_message: Message de l'utilisateur
            departement: Département de l'utilisateur (optionnel)

        Returns:
            Réponse structurée avec recommandations
        """
        symptoms = self.extract_symptoms(user_message)
        specialties = self.get_recommended_specialties(symptoms)

        # Analyse IA via Ollama
        aia_prompt = f"""Tu es un assistant santé expert en orientation médicale en France.
L'utilisateur dit: "{user_message}"

Symptômes détectés: {', '.join(symptoms) if symptoms else 'aucun symptôme spécifique'}
Spécialités recommandées: {', '.join(specialties) if specialties else 'généraliste'}

Fournis:
1. Un diagnostic préliminaire (rappelle que ce n'est pas un avis médical)
2. Les raisons des spécialités recommandées
3. Des conseils immédiats simples
4. L'urgence (normal/modéré/urgent -> appeler le 15)

Sois concis, empathique et clair."""

        ia_analysis = self._query_ollama(aia_prompt)

        # Analyse de couverture locale
        coverage_info = None
        if departement:
            coverage_info = self.analyze_region_coverage(departement)

        return {
            "symptoms_detected": symptoms,
            "recommended_specialties": specialties,
            "ia_analysis": ia_analysis,
            "coverage_analysis": coverage_info,
        }

    def get_emergency_help(self) -> dict:
        """Retourne les informations d'urgence"""
        return {
            "urgence": "OUI",
            "action": "Appelez le 15 (SAMU) immédiatement",
            "info": "Les symptômes graves doivent être traités aux urgences",
            "alternatives": ["Appel 112", "Aller aux urgences de l'hôpital le plus proche"],
        }


def create_chatbot_interface():
    """Factory pour créer et configurer le chatbot dans Streamlit"""
    return HealthMapChatbot()

