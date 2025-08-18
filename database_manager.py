#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager SQLite per Gestionale Gitemania PORTABLE (Versione con statistiche complete)
"""
import sqlite3, json, hashlib, os, threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from config import config

class DatabaseManager:
    def __init__(self):
        self.db_path = config.get_database_path()
        self.lock = threading.Lock()
        self._initialize_database()
        
    def _initialize_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, woo_id INTEGER UNIQUE NOT NULL, 
                        order_number TEXT, status TEXT, currency TEXT, total REAL, 
                        total_tax REAL, shipping_total REAL, customer_id INTEGER, 
                        customer_email TEXT, customer_name TEXT, billing_data TEXT, 
                        shipping_data TEXT, line_items TEXT, shipping_lines TEXT, 
                        payment_method TEXT, payment_method_title TEXT, date_created TEXT, 
                        date_modified TEXT, date_completed TEXT, raw_data TEXT, 
                        hash_signature TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"❌ Errore inizializzazione database: {e}")
            
    def sync_order(self, order_data: dict):
        self.sync_multiple_orders([order_data])

    def sync_multiple_orders(self, orders_data: List[dict]) -> Tuple[int, int]:
        with self.lock:
            to_insert, to_update = [], []
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT woo_id, hash_signature FROM orders')
                    existing_orders = {row[0]: row[1] for row in cursor.fetchall()}
                    for order in orders_data:
                        order_hash = self._calculate_order_hash(order)
                        order_tuple = tuple(self._extract_order_data(order, order_hash).values())
                        woo_id = order.get('id')
                        if woo_id not in existing_orders:
                            to_insert.append(order_tuple)
                        elif existing_orders[woo_id] != order_hash:
                            to_update.append(order_tuple[1:] + (order_tuple[0],))
                    if to_insert:
                        cursor.executemany('INSERT INTO orders (woo_id, order_number, status, currency, total, total_tax, shipping_total, customer_id, customer_email, customer_name, billing_data, shipping_data, line_items, shipping_lines, payment_method, payment_method_title, date_created, date_modified, date_completed, raw_data, hash_signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', to_insert)
                    if to_update:
                        cursor.executemany('UPDATE orders SET order_number=?, status=?, currency=?, total=?, total_tax=?, shipping_total=?, customer_id=?, customer_email=?, customer_name=?, billing_data=?, shipping_data=?, line_items=?, shipping_lines=?, payment_method=?, payment_method_title=?, date_created=?, date_modified=?, date_completed=?, raw_data=?, hash_signature=? WHERE woo_id = ?', to_update)
                    conn.commit()
                    return len(to_insert), len(to_update)
            except Exception as e:
                print(f"❌ Errore durante la sincronizzazione in blocco: {e}")
                return 0, 0
                
    def _calculate_order_hash(self, order_data: dict) -> str:
        fields = ['status', 'total', 'date_modified', 'line_items']
        data = {k: order_data.get(k) for k in fields}; return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

    def _extract_order_data(self, order_data: dict, hash_str: str) -> dict:
        billing = order_data.get('billing', {}) or {}; return {'woo_id': order_data.get('id'), 'order_number': order_data.get('number', ''), 'status': order_data.get('status', ''), 'currency': order_data.get('currency', 'EUR'), 'total': float(order_data.get('total', 0)), 'total_tax': float(order_data.get('total_tax', 0)), 'shipping_total': float(order_data.get('shipping_total', 0)), 'customer_id': order_data.get('customer_id'), 'customer_email': billing.get('email', ''), 'customer_name': f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip(), 'billing_data': json.dumps(billing), 'shipping_data': json.dumps(order_data.get('shipping', {}) or {}), 'line_items': json.dumps(order_data.get('line_items', [])), 'shipping_lines': json.dumps(order_data.get('shipping_lines', [])), 'payment_method': order_data.get('payment_method', ''), 'payment_method_title': order_data.get('payment_method_title', ''), 'date_created': order_data.get('date_created'), 'date_modified': order_data.get('date_modified'), 'date_completed': order_data.get('date_completed'), 'raw_data': json.dumps(order_data), 'hash_signature': hash_str}
        
    def get_orders(self, filters: dict = None) -> List[dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row; cursor = conn.cursor()
                query = "SELECT * FROM orders"; where_clauses = []; params = []
                if filters:
                    if filters.get('search_term'):
                        term = f"%{filters['search_term']}%"; where_clauses.append("(order_number LIKE ? OR customer_name LIKE ? OR customer_email LIKE ?)"); params.extend([term, term, term])
                    if filters.get('status'):
                        where_clauses.append("status = ?"); params.append(filters['status'])
                if where_clauses: query += " WHERE " + " AND ".join(where_clauses)
                query += " ORDER BY date_created DESC"
                if filters and filters.get('limit'): query += f" LIMIT {int(filters['limit'])}"
                
                rows = cursor.execute(query, tuple(params)).fetchall()
                orders = []
                for row in rows:
                    order = dict(row)
                    for field in ['billing_data', 'shipping_data', 'line_items', 'raw_data']:
                        if order.get(field):
                            try: 
                                order[field] = json.loads(order[field])
                            except (json.JSONDecodeError, TypeError):
                                print(f"⚠️ Warning: Impossibile decodificare il campo JSON '{field}' per l'ordine ID {order.get('woo_id')}")
                                order[field] = {} # In caso di errore, imposta un dizionario vuoto per evitare crash
                    orders.append(order)
                return orders
        except Exception as e:
            print(f"❌ Errore recupero ordini: {e}"); return []
            
    def get_order_stats(self, days: int = 0) -> dict:
        """ Se days è 0, calcola le statistiche su TUTTI gli ordini. """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT status, total, date_created, line_items FROM orders"
                params = []

                if days > 0:
                    date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S')
                    query += " WHERE date_created >= ?"
                    params.append(date_from)

                cursor.execute(query, tuple(params))
                orders = cursor.fetchall()

                if not orders:
                    return {'total_orders': 0, 'total_revenue': 0, 'by_status': {}, 'by_date': {}, 'top_products': {}}

                total_orders = len(orders)
                total_revenue = sum(o['total'] for o in orders if o['total'] is not None)
                by_status = defaultdict(int)
                by_date = defaultdict(int)
                top_products = defaultdict(int)

                for order in orders:
                    by_status[order['status']] += 1
                    if order['date_created']:
                        order_date = order['date_created'][:10]
                        by_date[order_date] += 1
                    try:
                        line_items = json.loads(order['line_items'])
                        for item in line_items:
                            top_products[item.get('name', 'Sconosciuto')] += item.get('quantity', 0)
                    except: pass
                
                sorted_products = sorted(top_products.items(), key=lambda item: item[1], reverse=True)[:5]
                
                return {
                    'total_orders': total_orders, 
                    'total_revenue': total_revenue, 
                    'by_status': dict(by_status), 
                    'by_date': dict(by_date), 
                    'top_products': dict(sorted_products)
                }

        except Exception as e:
            print(f"❌ Errore calcolo statistiche: {e}")
            return {}
