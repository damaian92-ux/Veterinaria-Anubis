import webview
from app import app

if __name__ == '__main__':
    window = webview.create_window("Sistema Veterinaria - Anubis", app, width=1200, height=800)
    webview.start()