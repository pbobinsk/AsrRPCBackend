# 1. Wybierz oficjalny obraz Pythona jako bazę
FROM python:3.13-slim

# 2. Ustaw zmienną środowiskową, aby logi Pythona pojawiały się od razu
ENV PYTHONUNBUFFERED=1

# 3. Ustaw katalog roboczy wewnątrz kontenera na /app
#    To jest nasz główny katalog projektu wewnątrz kontenera.
WORKDIR /app

# 4. Skopiuj plik z zależnościami i zainstaluj je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Skopiuj cały projekt (kod, moduły, pliki audio) do kontenera
#    Kropka na końcu oznacza, że kopiujemy do bieżącego katalogu roboczego (/app)
COPY . .

# 6. Wystaw port, na którym będzie działał serwer
EXPOSE 5666

# 7. ZDEFINIUJ DOMYŚLNĄ KOMENDĘ URUCHAMIAJĄCĄ SERWER JAKO MODUŁ
#    To jest jedyna zmiana, której potrzebujesz!
CMD ["python", "-m", "rpc_service.rpc_server"]