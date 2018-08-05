init_test_env:
	@docker-compose up -d --force-recreate --build

test:
	@./run_docker_tests.sh

clean:
	@docker-compose down