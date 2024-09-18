<p align="center">
  <img src="docs/assets/logo-area.png" alt="Area logo" width="200"/>
</p>

# Nastro 🧬 
Pipeline developed for the analysis of long-reads data (in particular produced by ONT hardware) by Rodolfo Tolloi at Area Science Park

# Roadmap
- [ ] File di lista per le batch, fatto a mano come piace a me. Piccolo, da test, solo gli attributi che sono necessari.
- [ ] Adattamento la BC-pipeline per usare i file lista che fa le cose
	- [ ] Da aggiungere calcolo delle risorse
	- [ ] **Importante**: il doppio finale. 1) Lancio della AL, 2) Rilancio di se stessa con la prima libera della lista
	- [ ] Primo test che deve andare bene e che questo funzioni da cima a fondo senza problemi (senza align, ma che quindi abbiamo il "modulo" funzionante e indipendente)
- [ ] Nuovo file-lista per l'allineamento e adattamento della AL-pipeline
	- [ ] Anche qui, test indipendente dal basecalling con i 2 finali: aggiornamento base del foglio, se sono ultima run lancio dei report
	- [ ] **Nota**: prova a usare anche liste malformate per test
- [ ] Integrazione BC e AL, quindi partendo dalla lista di BC mi faccio tutto da cima a fondo con i report finali.
FASE 1 finita
- [ ] Crezione del launcher che farà lettura della directory e creazione della lista.
	- Creazione della lista vuol dire controllare se esiste già e nel caso ci sia, aggiornala. Quindi testa con cose fatto a mano
- [ ] Lancio della BC-pipeline e di conseguenza di tutto il "long-read-pipeline"
STRUTTURA FINITA
- [ ] Temporizzatore che fa toccare il launcher