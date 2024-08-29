### Eigenes LLM
Achtung: Die Lösung ist leider **NICHT** fertig, sondern nur ein POC.
Das Modell kommt nicht mit den mitgesendeten Quellen klar.

```shell
docker-compose up -d --build
docker-compose run --rm python-app
```

Pro:
- Keine zusätzlichen Kosten pro API-Call.

Con:
- Muss eigentlich GPU-intensiv gehostet werden, was höhere Fixkosten bei niedrigeren variablen Kosten verursacht.
- Man benötigt das richtige Modell (ggf. mit viel Kontext & Finetuning), um gute Ergebnisse zu erzählen.
- DevOps.
- Schwieriger zu implementieren.
