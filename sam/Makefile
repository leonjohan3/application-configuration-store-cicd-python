.PHONEY: build deploy clean delete lint
default: deploy

all_files = template.yaml Makefile
REGION=$(shell awk -F '=' '/^region/ {print $$2}' samconfig.toml)

.aws-sam/lint-result.txt: $(all_files)
	mkdir -p .aws-sam
	sam validate --lint > $@

build: .aws-sam/lint-result.txt
	sam build

deploy: build
	#aws s3 sync open-api/ s3://sam-cli-source-owner-managed/open-api/
	sam deploy

clean:
	- /bin/rm -rf .aws-sam

delete:
	sam delete

lint:
	make .aws-sam/lint-result.txt
