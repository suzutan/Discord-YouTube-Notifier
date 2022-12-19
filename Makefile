.PHONY: all


build:
	docker build -t dyn:dev .

run: build
	docker run -v $(shell pwd)/config-d.yml:/config.yaml --env-file=.envrc.debug --rm -it dyn:dev python3 main.py /config.yaml
