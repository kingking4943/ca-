#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di test per Gestionale Gitemania
Testa tutte le funzionalità principali
Sviluppato da TechExpresso
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Aggiungi path per import moduli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from woocommerce_api import WooCommerceManager
from supabase_manager import SupabaseManager
from export_manager import ExportManager

class TestConfig(unittest.TestCase):
    """Test configurazione applicazione"""
    
    def setUp(self):
        self.config = Config()
        
    def test_config_initialization(self):
        """Test inizializzazione configurazione"""
        self.assertIsInstance(self.config.config, dict)
        self.assertIn('woocommerce', self.config.config)
        self.assertIn('supabase', self.config.config)
        self.assertIn('app', self.config.config)
        
    def test_encryption_decryption(self):
        """Test crittografia/decrittografia"""
        test_value = "test_secret_key_123"
        encrypted = self.config.encrypt_value(test_value)
        decrypted = self.config.decrypt_value(encrypted)
        
        self.assertNotEqual(encrypted, test_value)
        self.assertEqual(decrypted, test_value)
        
    def test_get_set_values(self):
        """Test get/set valori configurazione"""
        test_section = "test_section"
        test_key = "test_key"
        test_value = "test_value"
        
        self.config.set(test_section, test_key, test_value)
        retrieved_value = self.config.get(test_section, test_key)
        
        self.assertEqual(retrieved_value, test_value)

class TestWooCommerceManager(unittest.TestCase):
    """Test WooCommerce API Manager"""
    
    def setUp(self):
        self.woo_manager = WooCommerceManager()
        
    @patch('woocommerce_api.API')
    def test_initialization_success(self, mock_api):
        """Test inizializzazione WooCommerce riuscita"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        
        mock_api_instance = Mock()
        mock_api_instance.get.return_value = mock_response
        mock_api.return_value = mock_api_instance
        
        result = self.woo_manager.initialize(
            "https://test.com",
            "ck_test",
            "cs_test"
        )
        
        self.assertTrue(result)
        self.assertIsNotNone(self.woo_manager.api)
        
    @patch('woocommerce_api.API')
    def test_get_orders(self, mock_api):
        """Test recupero ordini"""
        # Mock orders data
        mock_orders = [
            {"id": 1, "status": "completed", "total": "100.00"},
            {"id": 2, "status": "processing", "total": "50.00"}
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_orders
        
        mock_api_instance = Mock()
        mock_api_instance.get.return_value = mock_response
        mock_api.return_value = mock_api_instance
        
        self.woo_manager.api = mock_api_instance
        
        orders = self.woo_manager.get_orders()
        
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0]['id'], 1)
        self.assertEqual(orders[1]['status'], 'processing')
        
    def test_order_handler(self):
        """Test handler eventi ordini"""
        test_event = {
            'type': 'webhook',
            'event': 'order.created',
            'order': {'id': 123, 'status': 'pending'},
            'timestamp': datetime.now()
        }
        
        # Test che non sollevi eccezioni
        self.woo_manager._default_order_handler(test_event)
        
class TestSupabaseManager(unittest.TestCase):
    """Test Supabase Database Manager"""
    
    def setUp(self):
        self.supabase_manager = SupabaseManager()
        
    def test_order_hash_calculation(self):
        """Test calcolo hash ordine"""
        order_data = {
            'id': 123,
            'status': 'completed',
            'total': '100.00',
            'date_modified': '2025-01-01T12:00:00',
            'line_items': [{'name': 'Product 1'}]
        }
        
        hash1 = self.supabase_manager._calculate_order_hash(order_data)
        hash2 = self.supabase_manager._calculate_order_hash(order_data)
        
        # Stesso ordine = stesso hash
        self.assertEqual(hash1, hash2)
        
        # Modifica ordine = hash diverso
        order_data['status'] = 'processing'
        hash3 = self.supabase_manager._calculate_order_hash(order_data)
        
        self.assertNotEqual(hash1, hash3)
        
    def test_extract_order_data(self):
        """Test estrazione dati ordine"""
        order_data = {
            'id': 123,
            'number': 'ORD-123',
            'status': 'completed',
            'total': '100.00',
            'currency': 'EUR',
            'customer_id': 456,
            'billing': {
                'email': 'test@example.com',
                'first_name': 'Mario',
                'last_name': 'Rossi'
            },
            'line_items': [{'name': 'Product 1'}]
        }
        
        extracted = self.supabase_manager._extract_order_data(order_data, 'test_hash')
        
        self.assertEqual(extracted['woo_id'], 123)
        self.assertEqual(extracted['order_number'], 'ORD-123')
        self.assertEqual(extracted['customer_email'], 'test@example.com')
        self.assertEqual(extracted['customer_name'], 'Mario Rossi')
        self.assertEqual(extracted['hash_signature'], 'test_hash')
        
class TestExportManager(unittest.TestCase):
    """Test Export Manager"""
    
    def setUp(self):
        self.export_manager = ExportManager()
        
    def test_export_manager_initialization(self):
        """Test inizializzazione export manager"""
        self.assertIsNotNone(self.export_manager.export_path)
        self.assertFalse(self.export_manager.export_running)
        self.assertIsNotNone(self.export_manager.scheduler)
        
    def test_export_result_dataclass(self):
        """Test dataclass ExportResult"""
        from export_manager import ExportResult
        
        result = ExportResult(
            success=True,
            file_path="test.csv",
            total_records=100,
            export_type="csv",
            duration=5.2
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.file_path, "test.csv")
        self.assertEqual(result.total_records, 100)
        self.assertEqual(result.export_type, "csv")
        self.assertEqual(result.duration, 5.2)
        
class IntegrationTest(unittest.TestCase):
    """Test integrazione componenti"""
    
    def setUp(self):
        self.config = Config()
        self.woo_manager = WooCommerceManager()
        self.supabase_manager = SupabaseManager()
        self.export_manager = ExportManager(self.supabase_manager)
        
    def test_component_integration(self):
        """Test integrazione base componenti"""
        # Test che tutti i componenti siano inizializzati
        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.woo_manager)
        self.assertIsNotNone(self.supabase_manager)
        self.assertIsNotNone(self.export_manager)
        
    @patch('woocommerce_api.API')
    @patch('supabase.create_client')
    def test_end_to_end_simulation(self, mock_supabase, mock_woo_api):
        """Test simulazione end-to-end"""
        # Mock WooCommerce
        mock_woo_response = Mock()
        mock_woo_response.status_code = 200
        mock_woo_response.json.return_value = [
            {
                'id': 123,
                'status': 'completed',
                'total': '100.00',
                'customer_id': 456,
                'billing': {'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'},
                'line_items': [{'name': 'Test Product'}],
                'date_created': '2025-01-01T12:00:00',
                'date_modified': '2025-01-01T12:00:00'
            }
        ]
        
        mock_woo_instance = Mock()
        mock_woo_instance.get.return_value = mock_woo_response
        mock_woo_api.return_value = mock_woo_instance
        
        # Mock Supabase
        mock_supabase_client = Mock()
        mock_supabase_table = Mock()
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase_table.insert.return_value.execute.return_value.data = [{'id': 1}]
        mock_supabase_client.table.return_value = mock_supabase_table
        mock_supabase.return_value = mock_supabase_client
        
        # Test flusso completo
        woo_init = self.woo_manager.initialize("https://test.com", "ck_test", "cs_test")
        self.assertTrue(woo_init)
        
        supabase_init = self.supabase_manager.initialize("https://test.supabase.co", "test_key")
        # Note: Questo test potrebbe fallire senza una configurazione Supabase reale
        # ma serve per verificare che il codice non sollevi eccezioni
        
def run_tests():
    """Esegue tutti i test"""
    print("=" * 60)
    print("  TEST SUITE GESTIONALE GITEMANIA")
    print("  Sviluppato da TechExpresso")
    print("=" * 60)
    
    # Crea test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Aggiungi test cases
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestWooCommerceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSupabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestExportManager))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTest))
    
    # Esegui test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Risultati
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ TUTTI I TEST SUPERATI CON SUCCESSO!")
        print(f"Test eseguiti: {result.testsRun}")
    else:
        print("❌ ALCUNI TEST FALLITI")
        print(f"Test eseguiti: {result.testsRun}")
        print(f"Fallimenti: {len(result.failures)}")
        print(f"Errori: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
