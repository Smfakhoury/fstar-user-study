# F* Proof Agent Docker Environment
# Use x86_64 platform for F* binary compatibility
FROM --platform=linux/amd64 ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libgmp-dev \
    opam \
    python3 \
    python3-pip \
    z3 \
    && rm -rf /var/lib/cache/apt

# Install F* from binary release
WORKDIR /opt
RUN wget -q https://github.com/FStarLang/FStar/releases/download/v2024.09.05/fstar_2024.09.05_Linux_x86_64.tar.gz \
    && tar xzf fstar_2024.09.05_Linux_x86_64.tar.gz \
    && rm fstar_2024.09.05_Linux_x86_64.tar.gz \
    && ls -la

# Set F* environment
ENV FSTAR_HOME=/opt/fstar
ENV PATH="${FSTAR_HOME}/bin:${PATH}"

# Install Python dependencies
RUN pip3 install anthropic openai

# Create workspace
WORKDIR /workspace
COPY . /workspace/

# Verify F* installation
RUN fstar.exe --version

# Default command
CMD ["python3", "agent.py"]
