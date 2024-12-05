# Serwer RPC - most do modułu ASR
## jsonrpc w wersji 2.0
- parametry - .env
- moduły - requirements.txt

## Udostępnione metody
- testowe: ping() i hello(str)
- użytkowe:
    - uploadFile(str) - przekazanie plików dźwiękowych do systemu ASR
    - doAsr() - uruchomienie transkrypcji, metoda zwraca plik json z transkrypcją

Na razie plik jest po prostu kopiowany, w przyszłości będzie przekazywany przez jakiś strumień, albo najpewniej przez MongoDB.