# Verwende offiziellen NGINX Container als Basis
FROM nginx:alpine

# Lösche Standard NGINX HTML-Dateien
RUN rm -rf /usr/share/nginx/html/*

# Kopiere unsere eigene HTML-Datei ins Verzeichnis
COPY index.html /usr/share/nginx/html/

EXPOSE 80