# Kazaa (Directory Gerarchica)

L’approccio a directory gerarchica vede la combinazione dell’approccio directory distribuita su un sotto insieme dei peer denominati supernodi per effettuare la ricerca e dell’approccio directory centralizzata per popolare la conoscenza di ogni supernodo. Ogni peer è associato ad un supernodo, selezionato mediante una azione di ricerca di vicini, a cui rispondono solo i supernodi e su cui la selezione è effettuata a caso. La procedura di ricerca dei supernodi avviene come nel caso del sistema a directory distribuita dei peer, con l’eccezione che rispondono solo i supernodi mentre effettuano la ritrasmissione tutti i peer. Il peer procede poi ad utilizzare il supernodo come elemento di directory centralizzata, richiedendo al supernodo quali peer hanno la disponibilità di file relativi al parametro di ricerca. Il supernodo di riferimento del peer che effettua la ricerca utilizza un approccio di query a directory distribuita sulla rete dei soli supernodi, cercando quindi tra tutte le directory centralizzate tutte le occorrenze relative al parametro di ricerca, aggregando tutte le risposte pervenute dai vari supernodi e restituendo infine al peer interessato un singolo pacchetto con tutte le risposte. Sebbene ogni peer possa essere eletto a supernodo, in questo contesto si ipotizza che all’atto della accensione ogni nodo sia già definito come peer o come supernodo. In ogni caso un supernodo si comporta anche da peer, utilizzando se stesso come supernodo.


### Prerequisites

Nel file _config.py_ impostare proprio IPv4 e IPv6 e della directory a cui connettersi

### Running

Eseguire dal terminale:
```
 cd P2P/Kazaa
 python3 main.py
```


## Authors :trollface:

* **ArtPes** - (https://github.com/ArtPes)
* **lovalova91** - (https://github.com/lovalova1991)
* **padovanl** - (https://github.com/padovanl)

See also the list of [contributors](https://github.com/ArtPes/Kazaa/graphs/contributors) who participated in this project.
