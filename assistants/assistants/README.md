### Assistants
- Benötigt einen OPENAI API Key!

Ausführung:
```shell
docker build -t assistants_img .
```
```shell
docker run -it --rm --env OPENAPI_KEY=your_api_key assistants_img
```

Pro:
- Sehr leicht zu implementieren
- Liefert in kurzer Zeit die besten Ergebnisse

Con:
- Kostenpflichtig (d.h. problematisch in der Skalierung)
