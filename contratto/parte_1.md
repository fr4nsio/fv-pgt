Semplice web app per gestione impianti fotovoltaici

- (1) l'applicazione sarà scritta in Python 3 Flask
- (2) è previsto un endpoint usato dai microcontrollori per caricare i dati in JSON (PUT /submit)
- (3) i dati inviati dai microcontrollori sono: identificativo microcontrollore, tensione, corrente. Questi possono essere soggetti a cambiamento a seconda delle esigenze
- (4) è previsto un sistema di notifiche nel caso i valori dei sensori siano fuori norma. Questo verrà implementato con la libreria Python apprise che permette di usare tutti i sistemi di messaggistica più conosciuti in un formato standardizzato
- (5) un secondo enpoint sarà usato per la visualizzazione dei dati con browser web (GET /show)
- (6) la visualizzazione dei dati sarà in HTML e JavaScript (se necessario) e si utilizzerà un semplice CSS per migliorarne l'aspetto
- (7) inizialmente la web app non salverà i dati dei sensori su database o memoria di massa per esigenze di sviluppo. Tutti i dati rimarranno disponibili nella memoria operativa finché l'app è in esecuzione. Questo potrà essere cambiato successivamente
