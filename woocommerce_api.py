#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo WooCommerce API per Gestionale Gitemania (Versione Finale con Paginazione Corretta)
"""
import threading, time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Callable
from woocommerce import API
from config import config

class WooCommerceManager:
    def __init__(self, on_order_update: Callable = None):
        self.api = None
        self.sync_running = False
        self.on_order_update = on_order_update or (lambda orders: None)
        self.last_sync = datetime.now(timezone.utc) - timedelta(days=1)
        
    def initialize(self, base_url: str, consumer_key: str, consumer_secret: str) -> bool:
        try:
            self.api = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret,
                           version="wc/v3", timeout=30, verify_ssl=True)
            response = self.api.get("system_status")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Errore inizializzazione WooCommerce: {e}")
            return False
            
    def start_sync(self):
        if self.sync_running: return
        self.sync_running = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        print("🔄 Sincronizzazione periodica avviata")
        
    def stop_sync(self):
        self.sync_running = False
        print("⏹️ Sincronizzazione periodica fermata")
        
    def _polling_loop(self):
        while self.sync_running:
            try:
                updated_orders = self.fetch_orders_since(self.last_sync)
                if updated_orders:
                    self.on_order_update(updated_orders)
                    self.last_sync = datetime.now(timezone.utc)
                time.sleep(config.get('app', 'sync_interval', 60))
            except Exception as e:
                print(f"❌ Errore polling: {e}")
                time.sleep(60)

    def fetch_orders_since(self, since_timestamp: datetime) -> Optional[List[dict]]:
        try:
            params = {'modified_after': (since_timestamp - timedelta(minutes=5)).isoformat()}
            return self.get_orders(params=params, paginate_all=False)
        except Exception as e:
            print(f"❌ Errore in fetch_orders_since: {e}")
            return None

    def fetch_last_day_orders(self) -> Optional[List[dict]]:
        try:
            since_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
            params = {'after': since_timestamp.isoformat()}
            return self.get_orders(params=params, paginate_all=True)
        except Exception as e:
            print(f"❌ Errore in fetch_last_day_orders: {e}")
            return None
            
    def get_orders(self, params: dict = None, paginate_all: bool = False) -> Optional[List[dict]]:
        if not self.api: return None
        
        all_orders = []
        page = 1
        per_page = config.get('app', 'per_page', 100)
        
        while True:
            try:
                current_params = {
                    'per_page': per_page,
                    'page': page,
                    'orderby': 'date',
                    'order': 'desc',
                    'status': 'any',
                }
                if params: current_params.update(params)
                
                if paginate_all:
                    print(f"📄 Download pagina {page} di ordini... (Trovati finora: {len(all_orders)})")
                
                response = self.api.get('orders', params=current_params)
                
                if response.status_code == 200:
                    orders_page = response.json()
                    
                    if not orders_page or not isinstance(orders_page, list):
                        # Se la pagina è vuota, abbiamo finito.
                        break
                    
                    all_orders.extend(orders_page)
                    
                    # Se non dobbiamo scaricare tutte le pagine, ci fermiamo dopo la prima.
                    if not paginate_all:
                        break
                    
                    # Se il numero di ordini scaricati è inferiore al massimo per pagina,
                    # significa che questa era l'ultima pagina.
                    if len(orders_page) < per_page:
                        break
                    
                    page += 1
                else:
                    print(f"❌ Errore API scaricando la pagina {page}: {response.status_code}")
                    break
            
            except Exception as e:
                print(f"❌ Eccezione in get_orders (pagina {page}): {e}")
                return None
        
        if paginate_all:
            print(f"✅ Download completato. Trovati {len(all_orders)} ordini in totale.")
            
        return all_orders
