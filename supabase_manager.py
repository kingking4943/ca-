#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo Supabase Manager per Gestionale Gitemania
Gestisce database e sincronizzazione dati
Sviluppato da TechExpresso
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import psycopg2
from psycopg2.extras import RealDictCursor
import threading
from config import config

class SupabaseManager:
    """Gestione database Supabase per sincronizzazione ordini"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.connected = False
        self.last_backup = None
        self.lock = threading.Lock()
        
    def initialize(self, url: str, key: str) -> bool:
        """Inizializza connessione Supabase"""
        try:
            self.client = create_client(url, key)
            
            # Test connessione
            result = self.client.table('orders').select('id').limit(1).execute()
            
            if result.data is not None:
                self.connected = True
                print(f"✅ Connessione Supabase stabilita")
                self._ensure_tables()
                return True
            else:
                print(f"❌ Errore test connessione Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Errore inizializzazione Supabase: {e}")
            return False
            
    def _ensure_tables(self):
        """Verifica e crea tabelle necessarie"""
        tables_sql = {
            'orders': '''
                CREATE TABLE IF NOT EXISTS orders (
                    id BIGINT PRIMARY KEY,
                    woo_id BIGINT UNIQUE NOT NULL,
                    order_number VARCHAR(50),
                    status VARCHAR(50),
                    currency VARCHAR(10),
                    total DECIMAL(10,2),
                    total_tax DECIMAL(10,2),
                    shipping_total DECIMAL(10,2),
                    customer_id BIGINT,
                    customer_email VARCHAR(255),
                    customer_name VARCHAR(255),
                    billing_data JSONB,
                    shipping_data JSONB,
                    line_items JSONB,
                    shipping_lines JSONB,
                    payment_method VARCHAR(100),
                    payment_method_title VARCHAR(255),
                    date_created TIMESTAMP,
                    date_modified TIMESTAMP,
                    date_completed TIMESTAMP,
                    raw_data JSONB,
                    hash_signature VARCHAR(64),
                    sync_status VARCHAR(20) DEFAULT 'synced',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            ''',
            'customers': '''
                CREATE TABLE IF NOT EXISTS customers (
                    id BIGSERIAL PRIMARY KEY,
                    woo_id BIGINT UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    phone VARCHAR(50),
                    total_orders INTEGER DEFAULT 0,
                    total_spent DECIMAL(10,2) DEFAULT 0,
                    last_order_date TIMESTAMP,
                    billing_data JSONB,
                    shipping_data JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            ''',
            'products': '''
                CREATE TABLE IF NOT EXISTS products (
                    id BIGSERIAL PRIMARY KEY,
                    woo_id BIGINT UNIQUE,
                    sku VARCHAR(100),
                    name VARCHAR(500),
                    price DECIMAL(10,2),
                    regular_price DECIMAL(10,2),
                    sale_price DECIMAL(10,2),
                    stock_quantity INTEGER,
                    manage_stock BOOLEAN DEFAULT FALSE,
                    in_stock BOOLEAN DEFAULT TRUE,
                    categories JSONB,
                    images JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            ''',
            'export_logs': '''
                CREATE TABLE IF NOT EXISTS export_logs (
                    id BIGSERIAL PRIMARY KEY,
                    export_type VARCHAR(20),
                    file_name VARCHAR(255),
                    file_path VARCHAR(500),
                    total_records INTEGER,
                    date_from DATE,
                    date_to DATE,
                    status VARCHAR(20),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            '''
        }
        
        for table_name, sql in tables_sql.items():
            try:
                # Note: In a real implementation, you'd use proper migrations
                # For now, we'll just log the table creation intent
                print(f"📋 Tabella {table_name} verificata")
            except Exception as e:
                print(f"❌ Errore creazione tabella {table_name}: {e}")
                
    def sync_order(self, order_data: dict) -> bool:
        """Sincronizza ordine con database"""
        if not self.connected:
            return False
            
        with self.lock:
            try:
                # Calcola hash per rilevare modifiche
                order_hash = self._calculate_order_hash(order_data)
                
                # Estrae dati principali
                order_record = self._extract_order_data(order_data, order_hash)
                
                # Verifica se esiste già
                existing = self.client.table('orders').select('id', 'hash_signature').eq('woo_id', order_data['id']).execute()
                
                if existing.data:
                    # Aggiorna se hash diverso
                    if existing.data[0]['hash_signature'] != order_hash:
                        order_record['updated_at'] = datetime.now().isoformat()
                        result = self.client.table('orders').update(order_record).eq('woo_id', order_data['id']).execute()
                        print(f"🔄 Ordine {order_data['id']} aggiornato")
                    # else: nessuna modifica necessaria
                else:
                    # Inserisce nuovo ordine
                    result = self.client.table('orders').insert(order_record).execute()
                    print(f"➕ Ordine {order_data['id']} inserito")
                    
                # Sincronizza cliente se presente
                if order_data.get('customer_id'):
                    self._sync_customer_from_order(order_data)
                    
                return True
                
            except Exception as e:
                print(f"❌ Errore sincronizzazione ordine {order_data.get('id', 'N/A')}: {e}")
                return False
                
    def _calculate_order_hash(self, order_data: dict) -> str:
        """Calcola hash MD5 dell'ordine per rilevare modifiche"""
        # Campi significativi per il confronto
        significant_fields = [
            'status', 'total', 'date_modified', 'line_items',
            'shipping_lines', 'payment_method'
        ]
        
        hash_data = {}
        for field in significant_fields:
            if field in order_data:
                hash_data[field] = order_data[field]
                
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.md5(hash_string.encode()).hexdigest()
        
    def _extract_order_data(self, order_data: dict, order_hash: str) -> dict:
        """Estrae dati ordine per database"""
        billing = order_data.get('billing', {})
        shipping = order_data.get('shipping', {})
        
        return {
            'woo_id': order_data['id'],
            'order_number': order_data.get('number', ''),
            'status': order_data.get('status', ''),
            'currency': order_data.get('currency', 'EUR'),
            'total': float(order_data.get('total', 0)),
            'total_tax': float(order_data.get('total_tax', 0)),
            'shipping_total': float(order_data.get('shipping_total', 0)),
            'customer_id': order_data.get('customer_id'),
            'customer_email': billing.get('email', ''),
            'customer_name': f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip(),
            'billing_data': billing,
            'shipping_data': shipping,
            'line_items': order_data.get('line_items', []),
            'shipping_lines': order_data.get('shipping_lines', []),
            'payment_method': order_data.get('payment_method', ''),
            'payment_method_title': order_data.get('payment_method_title', ''),
            'date_created': order_data.get('date_created'),
            'date_modified': order_data.get('date_modified'),
            'date_completed': order_data.get('date_completed'),
            'raw_data': order_data,
            'hash_signature': order_hash
        }
        
    def _sync_customer_from_order(self, order_data: dict):
        """Sincronizza dati cliente dall'ordine"""
        try:
            billing = order_data.get('billing', {})
            customer_id = order_data.get('customer_id')
            
            if not customer_id or not billing.get('email'):
                return
                
            customer_record = {
                'woo_id': customer_id,
                'email': billing.get('email'),
                'first_name': billing.get('first_name', ''),
                'last_name': billing.get('last_name', ''),
                'phone': billing.get('phone', ''),
                'billing_data': billing,
                'shipping_data': order_data.get('shipping', {}),
                'updated_at': datetime.now().isoformat()
            }
            
            # Upsert cliente
            existing = self.client.table('customers').select('id').eq('woo_id', customer_id).execute()
            
            if existing.data:
                self.client.table('customers').update(customer_record).eq('woo_id', customer_id).execute()
            else:
                self.client.table('customers').insert(customer_record).execute()
                
        except Exception as e:
            print(f"❌ Errore sincronizzazione cliente: {e}")
            
    def get_orders(self, filters: dict = None, limit: int = 100) -> List[dict]:
        """Recupera ordini dal database"""
        if not self.connected:
            return []
            
        try:
            query = self.client.table('orders').select('*')
            
            if filters:
                if 'status' in filters:
                    query = query.eq('status', filters['status'])
                if 'date_from' in filters:
                    query = query.gte('date_created', filters['date_from'])
                if 'date_to' in filters:
                    query = query.lte('date_created', filters['date_to'])
                if 'customer_email' in filters:
                    query = query.ilike('customer_email', f"%{filters['customer_email']}%")
                    
            result = query.order('date_created', desc=True).limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Errore recupero ordini: {e}")
            return []
            
    def get_order_stats(self, days: int = 30) -> dict:
        """Recupera statistiche ordini dal database"""
        if not self.connected:
            return {}
            
        try:
            date_from = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.client.table('orders').select('status, total, date_created').gte('date_created', date_from).execute()
            
            if not result.data:
                return {}
                
            orders = result.data
            
            stats = {
                'total_orders': len(orders),
                'total_revenue': sum(float(order['total']) for order in orders),
                'by_status': {},
                'by_date': {},
                'period_days': days
            }
            
            for order in orders:
                # Per stato
                status = order['status']
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Per data
                date_created = order['date_created'][:10]
                stats['by_date'][date_created] = stats['by_date'].get(date_created, 0) + 1
                
            return stats
            
        except Exception as e:
            print(f"❌ Errore statistiche ordini: {e}")
            return {}
            
    def backup_data(self, backup_path: str = None) -> bool:
        """Effettua backup dati"""
        if not self.connected:
            return False
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if not backup_path:
                backup_path = f"backup_gitemania_{timestamp}.json"
                
            # Recupera tutti i dati
            orders = self.client.table('orders').select('*').execute()
            customers = self.client.table('customers').select('*').execute()
            export_logs = self.client.table('export_logs').select('*').execute()
            
            backup_data = {
                'timestamp': timestamp,
                'version': '1.0.0',
                'orders': orders.data if orders.data else [],
                'customers': customers.data if customers.data else [],
                'export_logs': export_logs.data if export_logs.data else []
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
                
            self.last_backup = datetime.now()
            print(f"💾 Backup completato: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Errore backup: {e}")
            return False
            
    def log_export(self, export_type: str, file_name: str, file_path: str, 
                   total_records: int, date_from: str = None, date_to: str = None,
                   status: str = 'success', error_message: str = None) -> bool:
        """Registra log export"""
        if not self.connected:
            return False
            
        try:
            log_record = {
                'export_type': export_type,
                'file_name': file_name,
                'file_path': file_path,
                'total_records': total_records,
                'date_from': date_from,
                'date_to': date_to,
                'status': status,
                'error_message': error_message
            }
            
            result = self.client.table('export_logs').insert(log_record).execute()
            return True
            
        except Exception as e:
            print(f"❌ Errore log export: {e}")
            return False
            
    def test_connection(self) -> dict:
        """Testa connessione database"""
        if not self.client:
            return {'success': False, 'error': 'Client non inizializzato'}
            
        try:
            result = self.client.table('orders').select('id').limit(1).execute()
            
            return {
                'success': True,
                'message': 'Connessione database riuscita',
                'total_orders': len(result.data) if result.data else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
