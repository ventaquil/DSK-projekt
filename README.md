# Projekt z przedmiotu _"DSK"_

## Cel

Przetestować wydajność różnych serwerów WWW działających na systemie Linux.

## Uruchomienie

Testy uruchamiane są za pomocą skryptu `launch.py`. W tym celu należy zadbać serwer zdalny wyposażony w odpowiednie oprogramowanie.

Zgodność oprogramowania lokalnego testować możemy za pomocą skryptu `local_system_check.sh`.

Zgodność oprogramowania zdalnego testujemy analogicznie za pomocą skryptu `remote_system_check.sh`.

W katalogach `public/static` oraz `public/scripts` należy umieścić odpowiednie pliki, dzięki którym będziemy mierzyć wydajność serwerów. Ich lista zostanie automatycznie pobrana przez oprogramowanie i wykorzystana w testach.

Uruchamianie testów należy wykonać za pomocą polecenia:

    python3 launch.py [nazwa serwera]

Dozwolone jest korzystanie z nazw skonfigurowanych w katalogu `~/.ssh/config` ponieważ komunikacja odbywa się przy wykorzystaniu poleceń `ssh` oraz `scp`.

## Zależności Python3

Aby pobrać niezbędne biblioteki należy wykonać:

    pip3 install -r requirements.txt

