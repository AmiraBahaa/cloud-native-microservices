.PHONY: up down build logs clean restart ps tf-init tf-plan tf-apply tf-destroy

up:
	JWT_SECRET=dev-secret docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

restart:
	docker compose restart

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans
	docker system prune -f

tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan -var-file=terraform.tfvars

tf-apply:
	cd terraform && terraform apply -var-file=terraform.tfvars

tf-destroy:
	cd terraform && terraform destroy -var-file=terraform.tfvars
