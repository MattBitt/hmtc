all: run

dev_db:
	docker-compose -f ./docker-compose.dev.yml up -d

dev_db_restart:
	docker-compose -f ./docker-compose.dev.yml down
	docker-compose -f ./docker-compose.dev.yml up -d

staging:
	docker-compose up --build

deploy:
	
	ruff check --config hmtc/config/ruff.toml --select I . --fix
	black .
	git add .
	@read -p "What is the Commit Message: " enter; \
    git commit -m "deploy: $$enter"
	git push
	ssh root@192.168.0.202 /mnt/user/data/appdata/hmtc_app_code/deploy.sh
	python hmtc/utils/version_manager.py

cleanup:
	ruff check --config hmtc/config/ruff.toml --select I . --fix
	black .
