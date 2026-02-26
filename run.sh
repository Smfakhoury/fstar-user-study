#!/bin/bash
# F* Proof Agent Runner

set -e

DOCKER="/Applications/Docker.app/Contents/Resources/bin/docker"
IMAGE_NAME="fstar-proof-agent"
CONTAINER_NAME="fstar-agent"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[*]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[X]${NC} $1"
}

# Check if Docker is running
if ! $DOCKER info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

case "${1:-help}" in
    build)
        print_status "Building F* Proof Agent Docker image..."
        $DOCKER build -t $IMAGE_NAME .
        print_status "Build complete!"
        ;;

    run)
        if [ -z "$2" ]; then
            print_warning "Usage: ./run.sh run <task_description>"
            print_warning "Example: ./run.sh run 'Implement binary search'"
            exit 1
        fi
        print_status "Running proof agent..."
        $DOCKER run --rm -it \
            -v "$(pwd)/output:/workspace/output" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            $IMAGE_NAME \
            python3 agent.py --task "$2" --output output/solution.fst
        ;;

    demo)
        print_status "Running demo tasks from the paper..."
        $DOCKER run --rm -it \
            -v "$(pwd)/output:/workspace/output" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            $IMAGE_NAME \
            python3 agent.py --demo
        ;;

    shell)
        print_status "Starting interactive shell in container..."
        $DOCKER run --rm -it \
            -v "$(pwd):/workspace" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            $IMAGE_NAME \
            /bin/bash
        ;;

    verify)
        if [ -z "$2" ]; then
            print_warning "Usage: ./run.sh verify <file.fst>"
            exit 1
        fi
        print_status "Verifying $2..."
        $DOCKER run --rm \
            -v "$(pwd):/workspace" \
            $IMAGE_NAME \
            fstar.exe "$2"
        ;;

    interactive)
        print_status "Starting interactive proof agent..."
        $DOCKER run --rm -it \
            -v "$(pwd)/output:/workspace/output" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            $IMAGE_NAME \
            python3 agent.py
        ;;

    test-fstar)
        print_status "Testing F* installation..."
        $DOCKER run --rm $IMAGE_NAME fstar.exe --version
        print_status "Running simple verification test..."
        echo 'module Test
let x : int = 42' | $DOCKER run --rm -i $IMAGE_NAME sh -c 'cat > /tmp/test.fst && fstar.exe /tmp/test.fst'
        print_status "F* is working correctly!"
        ;;

    help|*)
        echo "F* Proof Agent"
        echo ""
        echo "Usage: ./run.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  build           Build the Docker image"
        echo "  run <task>      Run agent on a task"
        echo "  demo            Run demo tasks from the paper"
        echo "  shell           Start interactive shell"
        echo "  verify <file>   Verify an F* file"
        echo "  interactive     Start interactive agent mode"
        echo "  test-fstar      Test F* installation"
        echo "  help            Show this help"
        echo ""
        echo "Environment:"
        echo "  ANTHROPIC_API_KEY   API key for Claude (optional)"
        echo ""
        echo "Examples:"
        echo "  ./run.sh build"
        echo "  ./run.sh run 'Implement binary search with verification'"
        echo "  ./run.sh verify output/solution.fst"
        ;;
esac
