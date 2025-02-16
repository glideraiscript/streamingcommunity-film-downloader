# NOME SCRIPT: StreamingCommunity Film Downloader
# VERSIONE: 1.0
# DATA: 15 febbraio 2025
# AUTORI: *Glider con la preziosa collaborazione dell'intelligenza artificiale (ChatGPT)

# DESCRIZIONE:
# Questo script permette di cercare e scaricare episodi da StreamingCommunity utilizzando 
# l'API di "streamingcommunity" e yt-dlp per il download del contenuto. 
# 

# ATTENZIONE
# Modifica il percorso in cui salvare il file ad es. c:\film nella var download_directory

# LICENSE:
# Questo script è liberamente utilizzabile, con la seguente condizione:
# Se desideri utilizzare e modificare lo script, ti chiedo gentilmente di fare una donazione 
# a tua discrezione, in modo che io possa continuare a migliorare questo e altri script.
# Puoi fare una donazione in criptovalute come Bitcoin, Dogecoin, o Ethereum.
# 
# Se sei interessato a fare una donazione, puoi utilizzare i seguenti indirizzi:
# Bitcoin: 1GMukowiQJYTjAY2cYStDJFxiDZ9FsbA23
# Dogecoin: DR2cEpXFahfQHKS8GU8gpfajBGDVEcqNaZ
# Ethereum: 0xF1BdF4eFD3Dd69696874B898491B8D6FcC5a60eD
# Solana: nRfEP8pWnA12DwEiTpWZrnsYRxLapG7fAQZYJyojjNT
# Aleo: aleo18mfh9vaxskpgf5e3a4vfw4ts5vd79as32a284ejaaxttdyusa5rqgg0qr9
# Dimo: 0xd7EFE727Bd1D7B2BCeA604100Fe3d83CcE45F3a3
# Near: 7fe5e7ca0e0efac6379c6896091d4f636def90c593f4930af4de8bf0b260fbea
# Floky: 0x0099dB0556fa8D3910fA27Dde5dcC10Db898111c
#
# Grazie per il tuo supporto!

# Nota: Questo script è stato sviluppato a scopo personale e non è destinato alla distribuzione commerciale.
# Buon download!

import sys
import requests
import os
import re
import subprocess
import yt_dlp
import webbrowser
import json
import html
from urllib.parse import urlparse

from concurrent.futures import ThreadPoolExecutor

# Memorizza il dominio di default
default_domain = "https://streamingcommunity.paris"
current_domain = default_domain

from scuapi import API
sc = API('streamingcommunity.paris')

def download_movie(m3u_playlist_url, download_directory,movie_name):
    # Cambia la directory di lavoro prima di eseguire il download
    os.chdir(download_directory)
    
     # Opzioni di configurazione per yt-dlp
    ydl_opts = {
        'outtmpl': f'{movie_name}.%(ext)s',
        'verbose': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 10,
        'retries': 5,
    }

    # Avvia yt-dlp per ottenere i formati disponibili
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Ottieni le informazioni del video
        info_dict = ydl.extract_info(m3u_playlist_url, download=False)

        # Lista dei formati disponibili
        formati = info_dict.get('formats', [])
        
        # Cerca un formato combinato (audio e video)
        formato_combinato = None
        for formato in formati:
            if formato.get('vcodec') and formato.get('acodec'):  # Deve avere sia audio che video
                if formato_combinato is None or formato['height'] > formato_combinato['height']:
                    formato_combinato = formato
        
        if formato_combinato:
            # Se un formato combinato è disponibile, seleziona il miglior formato
            formato_id = formato_combinato['format_id']
            ydl_opts['format'] = formato_id
            print(f"Scarico il formato combinato: {formato_id}")
        else:
            # Se il formato combinato non è disponibile, scegli separatamente video e audio
            video_format = None
            audio_format = None
            for formato in formati:
                if formato.get('vcodec') and (not video_format or formato['height'] > video_format['height']):
                    video_format = formato
                if formato.get('acodec') and formato['acodec'] == 'mp4a.40.2' and formato.get('language') == 'ita':
                    audio_format = formato  # Seleziona l'audio in italiano

            if video_format and audio_format:
                # Usa l'ID dei formati video e audio per scaricare separatamente
                ydl_opts['format'] = f"{video_format['format_id']}+{audio_format['format_id']}"
                print(f"Scarico separatamente il video: {video_format['format_id']} e l'audio italiano: {audio_format['format_id']}")
            else:
                print("Non è stato possibile trovare i formati desiderati.")

        # Esegui il download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m3u_playlist_url])
            
def menu():
    print("Seleziona un'opzione:")
    print("1) Download")
    print("2) Guarda video")
    print("3) Esci")

def operazione_principale(iframe,m3u_playlist_url, download_directory,title):
    while True:
        menu()
        scelta = input("Inserisci la tua scelta (1/2/3): ")

        if scelta == "1":
            print("Inizio download...")
            download_movie(m3u_playlist_url, download_directory,title)
        elif scelta == "2":
            webbrowser.open(iframe)
        elif scelta == "3":
            print("Uscita dal programma.")
            break
        else:
            print("Scelta non valida, riprova.")
            
# Funzione per eseguire la ricerca e scaricare i file
def search_and_download(search_term, download_directory):
    sc = API('streamingcommunity.paris')
    result = sc.search(search_term)
    #print(f"RES {result}")
    for title, details in result.items():
        if search_term.lower() in title.lower():  # Confronto case-insensitive
            id = details.get('id')
            slug = details.get('slug')
            print(f"Film trovato '{title}'")
            web = current_domain + "/iframe/" + str(id)
            iframe, m3u_playlist_url = sc.get_links(id)
            operazione_principale(web,m3u_playlist_url, download_directory,title)            
            break
            #print(f"iFrame per '{title}': {iframe}")
            #print(f"URL M3U Playlist per '{title}': {m3u_playlist_url}")
            #print(f"Url '{m3u_playlist_url}")

            # Avvia il download del film
            #download_movie(m3u_playlist_url, download_directory,title)

# Esegui la ricerca e il download per il termine inserito
# Modifica il percorso in cui salvare il file ad es. c:\Film
download_directory = r"c:\film"
search_term = input("Inserisci il titolo da cercare: ")
search_and_download(search_term, download_directory)
