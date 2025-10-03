import unittest
import pandas as pd
from datetime import datetime
from scripts.migrate_patients import clean_record, nettoyer_dataframe, transformer_records

class TestMigrationUnitaires(unittest.TestCase):

    def test_clean_record(self):
        """Test la fonction clean_record avec différents types de données"""
        record = {
            "nom": " alice ",
            "age": "28",
            "taille": "1.65",
            "date_naissance": "1995-01-15",
            "email": None,
            "commentaire": " bonjour "
        }
        cleaned = clean_record(record)
        self.assertEqual(cleaned["nom"], "Alice")
        self.assertEqual(cleaned["age"], 28)
        self.assertEqual(cleaned["taille"], 1.65)
        self.assertIsInstance(cleaned["date_naissance"], datetime)
        self.assertIsNone(cleaned["email"])
        self.assertEqual(cleaned["commentaire"], "Bonjour")

    def test_nettoyer_dataframe(self):
        """Test nettoyage doublons et NaN"""
        df = pd.DataFrame({"A": [1, 2, 2, None], "B": ["x", "y", "y", "z"]})
        df_cleaned = nettoyer_dataframe(df)
        self.assertEqual(df_cleaned.shape[0], 2)

    def test_nettoyer_dataframe_champ_vide(self):
        """Doit lever ValueError si champ vide"""
        df = pd.DataFrame({"A": [1, ""], "B": ["x", "y"]})
        with self.assertRaises(ValueError):
            nettoyer_dataframe(df)

    def test_transformer_records(self):
        """Test transformation DataFrame → liste de dicts"""
        df = pd.DataFrame({"nom": [" bob "], "age": ["30"], "taille": ["1.80"]})
        records = transformer_records(df)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["nom"], "Bob")
        self.assertEqual(records[0]["age"], 30)
        self.assertEqual(records[0]["taille"], 1.8)

if __name__ == "__main__":
    unittest.main()
