###############################################
# BASE IMAGE
###############################################
FROM ubuntu:22.04

###############################################
# WORKING DIRECTORY
###############################################
# DO NOT MODIFY THIS SECTION
RUN mkdir /app
WORKDIR /app

###############################################
# SYSTEM DEPENDENCIES
###############################################
ENV DEBIAN_FRONTEND=noninteractive

# Install base packages and native C/C++ dependency headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    git python3 python3-pip python3-setuptools python-is-python3 \
    clang llvm build-essential curl wget tar ninja-build \
    zlib1g-dev libssl-dev libicu-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Manually install CMake 3.29 (dotnet requires >= 3.26, Ubuntu 22.04 only has 3.22)
RUN wget -O - https://github.com/Kitware/CMake/releases/download/v3.29.0/cmake-3.29.0-linux-x86_64.tar.gz | tar xzf - -C /usr/local --strip-components=1

# Install .NET SDKs required for compiling dotnet/runtime
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 9.0
ENV PATH="/root/.dotnet:${PATH}"

###############################################
# REPOSITORY SETUP
###############################################
RUN git clone https://github.com/dotnet/runtime.git .
# Pin to the specific parent commit of the PR
RUN git checkout 85149f3fd8fb5e24afafc5fedbf075a719464624

###############################################
# PROJECT DEPENDENCIES AND CONFIGURATION
###############################################
# Build the libraries subset to generate the required local targeting packs
RUN ./build.sh libs -c Release

###############################################
# ENTRYPOINT
###############################################
# DO NOT MODIFY THIS SECTION
ENTRYPOINT ["/bin/bash"]