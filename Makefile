# 变量定义
APP_NAME := be-my-eyes-backend
BUILD_TIME := $(shell date "+%F %T")
COMMIT_SHA1 := $(shell git rev-parse HEAD)

# 默认环境为开发环境
CONFIG_FILE := deployment/config.yaml
DOCKER_TAG := latest
# 编译标志
LDFLAGS := -X 'main.BuildTime=$(BUILD_TIME)' \
           -X 'main.CommitID=$(COMMIT_SHA1)' \
           -w -s

.PHONY: all build clean test lint docker-build docker-push run stop restart logs help

# 默认目标
all: build

# 编译
build:
	@echo "Building for $(ENV) environment..."
	@go build -ldflags "$(LDFLAGS)" -o $(APP_NAME) .

# 清理
clean:
	@echo "Cleaning..."
	@rm -f $(APP_NAME)
	@go clean -cache
	@docker system prune -f

# 运行测试
test:
	@echo "Running tests..."
	@go test -v ./...

# 代码检查
lint:
	@echo "Running linter..."
	@golangci-lint run ./...

# 构建 Docker 镜像
docker-build:
	@echo "Building Docker image ..."
	@docker build -t $(APP_NAME):$(DOCKER_TAG) \
		--build-arg CONFIG_FILE=$(CONFIG_FILE) \
		-f deployment/dockerfile .

# 推送 Docker 镜像到仓库
docker-push:
	@echo "Pushing Docker image for $(ENV) environment..."
	@docker push $(APP_NAME):$(DOCKER_TAG)
remove:
	@docker rm -f $(APP_NAME)
	
deploy-cn:
	@echo "Deploying to production server..."
	ssh root@47.116.173.33 '\
		cd /root/deeper-newsletter && \
		git pull && \
		git checkout test && \
		make remove && \
		make docker-build && \
		make run'
	
# 重启服务
restart: stop run

# 开发环境相关命令
dev: export ENV=dev
dev: build run

# 测试环境相关命令
test: export ENV=test
test: build docker-build docker-push run

# 生产环境相关命令
prod: export ENV=prod
prod: test docker-build docker-push

run:
	@echo "Starting Docker container in $(ENV) environment..."
	@docker run -d \
		--name $(APP_NAME) \
		-v $(PWD)/deployment/logs:/app/deployment/logs \
		-p 8080:8000 \
		$(APP_NAME):$(DOCKER_TAG)

# 停止服务
stop:
	@echo "Stopping Docker container..."
	@docker stop $(APP_NAME)-$(ENV) || true
	@docker rm $(APP_NAME)-$(ENV) || true

# 查看日志
logs:
	@echo "Viewing logs for $(ENV) environment..."
	@docker logs -f $(APP_NAME)-$(ENV)

deploy:
	@echo "Deploying to production server..."
	ssh brizenchi@34.56.103.77 '\
		cd /home/brizenchi/be-my-eyes-backend && \
		git pull && \
		git checkout main && \
		sudo make docker-build && \
		sudo make remove && \
		sudo make run'
# 帮助信息
help:
	@echo "Available commands:"
	@echo "  make build          - Build the application"
	@echo "  make clean          - Clean build files"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linter"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-push    - Push Docker image"
	@echo "  make run            - Start services"
	@echo "  make stop           - Stop services"
	@echo "  make restart        - Restart services"
	@echo "  make logs           - View logs"
	@echo ""
	@echo "Environment variables:"
	@echo "  ENV                 - Environment (dev/test/prod)"

# 设置默认环境变量
export DB_USER ?= deep_reading
export DB_PASSWORD ?= your_password
export DB_NAME ?= deep_reading
