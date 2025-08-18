#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theme Manager per Gestionale Gitemania (Versione Finale Stabile)
Sviluppato da TechExpresso
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageTk

class GiteManiTheme:
    """Tema professionale Gitemania con colore primario personalizzato"""
    
    # Palette colori con il rosso #FF0000 come primario
    COLORS = {
        'primary': '#FF0000',      # Rosso puro come richiesto
        'primary_light': '#FF4D4D', # Tonalità più chiara per effetti hover
        'primary_dark': '#B30000',  # Tonalità più scura per effetti click
        'secondary': '#475569',     # Grigio-Blu scuro per contrasti
        'accent': '#60A5FA',       # Azzurro per accenti
        'success': '#10B981',      # Verde
        'info': '#0EA5E9',         # Ciano
        'warning': '#F59E0B',      # Arancio
        'danger': '#D90429',       # Un rosso leggermente diverso per i messaggi di pericolo
        'surface': '#F8FAFC',      # Sfondo leggermente grigio
        'background': '#FFFFFF',   # Bianco puro
        'card': '#FFFFFF',         # Sfondo delle card
        'border': '#E2E8F0',      # Grigio per bordi
        'text': '#1E293B',        # Testo scuro (quasi nero)
        'text_secondary': '#64748B', # Testo secondario grigio
        'text_muted': '#94A3B8',   # Testo attenuato
    }
    
    FONTS = {
        'default': ('Segoe UI', 9), 'heading': ('Segoe UI', 14, 'bold'),
        'subheading': ('Segoe UI', 10, 'bold'), 'large_value': ('Segoe UI', 24, 'bold'),
    }
    
    @classmethod
    def apply_to_root(cls, root: tk.Tk):
        """Applica il tema e gli stili alla finestra principale"""
        style = tb.Style(theme='flatly')
        style.configure('TFrame', background=cls.COLORS['surface'])
        style.configure('Card.TFrame', background=cls.COLORS['card'], bordercolor=cls.COLORS['border'], borderwidth=1, relief='solid')
        style.configure('Card.TLabel', background=cls.COLORS['card'], foreground=cls.COLORS['text'])
        style.configure('Header.TFrame', background=cls.COLORS['primary'])
        style.configure('Header.TLabel', background=cls.COLORS['primary'], foreground='white', font=cls.FONTS['heading'])
        style.configure('Brand.TLabel', background=cls.COLORS['primary'], foreground='#FFFFFF', font=('Segoe UI', 10, 'italic'))
        style.configure('TNotebook.Tab', font=cls.FONTS['subheading'], padding=[15, 8])
        style.map('TNotebook.Tab', foreground=[('selected', cls.COLORS['primary'])])
        for color in ['primary', 'success', 'warning', 'danger', 'info']:
            style.configure(f'{color.capitalize()}.TButton', background=cls.COLORS[color], foreground='white', padding=(10,5))
        return style

    @classmethod
    def setup_matplotlib(cls):
        colors = [cls.COLORS[c] for c in ['primary', 'success', 'warning', 'info', 'danger']]
        plt.rcParams.update({
            'figure.facecolor': cls.COLORS['card'], 'axes.facecolor': cls.COLORS['card'],
            'axes.edgecolor': cls.COLORS['border'], 'grid.color': cls.COLORS['border'],
            'text.color': cls.COLORS['text'], 'axes.labelcolor': cls.COLORS['text_secondary'],
            'xtick.color': cls.COLORS['text_secondary'], 'ytick.color': cls.COLORS['text_secondary'],
            'axes.prop_cycle': plt.cycler('color', colors)
        })
        return colors

    @classmethod
    def get_status_icon(cls, status: str) -> str:
        """Restituisce icona per stato ordine"""
        return {'completed': '✅', 'processing': '🔄', 'pending': '⏳', 'on-hold': '⏸️',
                'cancelled': '❌', 'refunded': '💰', 'failed': '⚠️'}.get(status.lower(), '📋')

class ModernUIHelper:
    @staticmethod
    def create_header_frame(parent, title: str):
        frame = ttk.Frame(parent, style='Header.TFrame')
        ttk.Label(frame, text="📊", font=('Segoe UI', 16), style='Header.TLabel').pack(side='left', padx=(10, 5))
        ttk.Label(frame, text=title, style='Header.TLabel').pack(side='left', padx=5, pady=10)
        ttk.Label(frame, text="TechExpresso", style='Brand.TLabel').pack(side='right', padx=10)
        return frame
