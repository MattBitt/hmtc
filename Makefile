all: run

dev_db:
	docker-compose -f ./docker-compose.dev.yml up -d

staging:
	docker-compose up --build

deploy:
	git add .
	@read -p "Enter : " enter; \
    git commit -m "deploy: $$enter"
	git push
	ssh root@192.168.0.202 /mnt/user/data/appdata/hmtc_app_code/deploy.sh

cleanup:
	ruff check --config hmtc/config/ruff.toml --select I . --fix
	black .

