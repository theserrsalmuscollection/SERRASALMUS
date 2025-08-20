#!/bin/bash

# SERRA ORGIN Installation Script
# Automated setup for the complete SERRA ORGIN framework

set -e

echo "🌊 Welcome to SERRA ORGIN Installation"
echo "=====================================\n"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS detected"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        print_success "Windows detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if Python version is 3.11+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.11 or higher is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        print_status "Please install Python 3.11+ from https://python.org/"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
        
        # Check if Node version is 18+
        if node -p "process.version.split('.')[0].substring(1) >= 18"; then
            print_success "Node.js version is compatible"
        else
            print_warning "Node.js 18+ is recommended. Found: $NODE_VERSION"
        fi
    else
        print_error "Node.js is not installed"
        print_status "Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is not installed"
        exit 1
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "$GIT_VERSION found"
    else
        print_error "Git is not installed"
        print_status "Please install Git from https://git-scm.com/"
        exit 1
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_success "$DOCKER_VERSION found"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker is not installed (optional but recommended)"
        print_status "Install Docker from https://docker.com/ for enhanced features"
        DOCKER_AVAILABLE=false
    fi
}

# Create virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install the package in development mode
    pip install -e .
    
    print_success "Python dependencies installed"
}

# Setup Node.js dependencies
setup_node_env() {
    print_status "Installing Node.js dependencies..."
    
    # Install root dependencies
    npm install
    
    print_success "Node.js dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/vectordb
    mkdir -p logs
    mkdir -p temp
    mkdir -p uploads
    mkdir -p models
    mkdir -p web_ui/dist
    
    print_success "Directories created"
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Configuration file created from template"
        print_warning "Please edit .env file with your specific settings"
    else
        print_status "Configuration file already exists"
    fi
}

# Download models (optional)
download_models() {
    print_status "Checking for local AI models..."
    
    if [ "$1" = "--download-models" ]; then
        print_status "Downloading local AI models (this may take a while)..."
        
        # Create models directory
        mkdir -p models/embeddings
        
        # Download embedding model (this is a placeholder - actual implementation would download models)
        print_status "Downloading embedding models..."
        # python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('./models/embeddings/all-MiniLM-L6-v2')"
        
        print_success "Models downloaded (placeholder)"
    else
        print_warning "Skipping model download. Use --download-models flag to download."
        print_status "Models will be downloaded automatically on first use."
    fi
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Run database migrations (if any)
    if [ -f "alembic.ini" ]; then
        print_status "Running database migrations..."
        source venv/bin/activate
        alembic upgrade head
        print_success "Database migrations completed"
    else
        print_status "No migrations found, database will be created on first run"
    fi
}

# Run tests
run_tests() {
    if [ "$1" = "--run-tests" ]; then
        print_status "Running tests..."
        
        source venv/bin/activate
        
        # Run Python tests
        if [ -d "tests" ]; then
            python -m pytest tests/ -v
            print_success "Python tests completed"
        else
            print_warning "No Python tests found"
        fi
        
        # Run Node.js tests
        if [ -f "package.json" ] && npm run test &> /dev/null; then
            npm test
            print_success "Node.js tests completed"
        else
            print_warning "No Node.js tests found or npm test script not available"
        fi
    else
        print_status "Skipping tests. Use --run-tests flag to run tests."
    fi
}

# Setup Docker (optional)
setup_docker() {
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$1" = "--docker" ]; then
        print_status "Setting up Docker environment..."
        
        # Build Docker images
        docker-compose build
        
        print_success "Docker environment setup complete"
        print_status "You can now run: docker-compose up -d"
    else
        if [ "$1" = "--docker" ] && [ "$DOCKER_AVAILABLE" = false ]; then
            print_error "Docker is not available but --docker flag was specified"
            exit 1
        fi
        print_status "Skipping Docker setup. Use --docker flag if you want Docker support."
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if Python package is installed
    source venv/bin/activate
    if python -c "import serra_orgin" &> /dev/null; then
        print_success "SERRA ORGIN Python package is installed"
    else
        print_error "SERRA ORGIN Python package installation failed"
        exit 1
    fi
    
    # Check if CLI is available
    if command -v serra &> /dev/null; then
        print_success "SERRA ORGIN CLI is available"
    else
        print_warning "SERRA ORGIN CLI not found in PATH"
        print_status "You may need to activate the virtual environment first"
    fi
}

# Print completion message
print_completion() {
    echo ""
    echo "🎉 SERRA ORGIN Installation Complete!"
    echo "====================================="
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit the .env file with your specific configuration"
    echo "2. Activate the virtual environment: source venv/bin/activate"
    echo "3. Start SERRA ORGIN: serra start"
    echo "4. Open your browser to http://localhost:3000"
    echo ""
    echo "Documentation: https://docs.serra-orgin.dev"
    echo "Support: polerbear1973@gmail.com"
    echo ""
    print_status "Happy coding with SERRA ORGIN! 🌊"
}

# Main installation flow
main() {
    check_os
    check_prerequisites
    create_directories
    setup_config
    setup_python_env
    setup_node_env
    download_models "$@"
    setup_database
    setup_docker "$@"
    run_tests "$@"
    verify_installation
    print_completion
}

# Parse command line arguments
DOWNLOAD_MODELS=false
RUN_TESTS=false
DOCKER_SETUP=false

for arg in "$@"; do
    case $arg in
        --download-models)
            DOWNLOAD_MODELS=true
            shift
            ;;
        --run-tests)
            RUN_TESTS=true
            shift
            ;;
        --docker)
            DOCKER_SETUP=true
            shift
            ;;
        --help|-h)
            echo "SERRA ORGIN Installation Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --download-models    Download local AI models"
            echo "  --run-tests         Run tests after installation"
            echo "  --docker           Setup Docker environment"
            echo "  --help, -h         Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_warning "Unknown option: $arg"
            ;;
    esac
done

# Run main installation
main "$@"
