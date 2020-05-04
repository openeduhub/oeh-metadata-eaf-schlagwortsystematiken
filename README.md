# OpenEduHub Vocabulary - Schlagwortsystematiken

This is a repository for vocabulary used in the OpenEduHub-Project.

Every time a push is made to the repository a GitHub-workflow-action is triggered to publish the most recent vocabulary to the `gh-pages`-branch, which is used by GitHub pages. It spins up a Docker-Container made out the [SkoHub-Vocabs](https://github.com/hbz/skohub-vocabs)-tool. You can have a look at the Dockerfile [at this fork of skohub-vocabs](https://github.com/sroertgen/skohub-vocabs/tree/docker).

## Schlagwortsystematiken

Die Systematiken basieren auf diesen rtf-files: http://agmud.de/fachsystematiken/ . 
Diese wurden zu txt-Dateien konvertiert und anschließend in SKOS umgewandelt.
Dies ist momentan noch als PoC anzusehen, die Rohdaten brauchen noch etwas Überarbeitung.

"Bildende Kunst" ist momentan noch zu korrupt und muss überarbeitet werden. Alle anderen Vokabulare werden bereits ohne Fehler geparst und in korrektes SKOS konvertiert.
