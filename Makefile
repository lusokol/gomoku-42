# Le fichier principal de ton projet
MAIN = srcs/menu.py

# Commande pour exécuter ton projet
run:
	python3 $(MAIN)

# Commande pour formatter ton code avec black
format:
	black .

# Linter pour vérifier la qualité du code
norme:
	flake8 .

# Tests (si on veut faire des tests unitaire ?)
test:
	pytest

# Nettoyer les fichiers inutiles
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +

# Aide : affiche toutes les commandes disponibles
help:
	@echo "make run      - Lance le projet"
	@echo "make format   - Formatte le code avec Black"
	@echo "make norme     - Vérifie le code avec flake8"
	@echo "make test     - Lance les tests avec pytest"
	@echo "make clean    - Supprime les fichiers temporaires"
