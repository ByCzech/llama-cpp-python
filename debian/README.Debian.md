# Debian package support

This repository extends the upstream `llama-cpp-python` project with **Debian `.deb` packaging** for Debian 13 (Trixie).

The packaging is designed around a modular backend architecture. The Python bindings and common runtime are separated from hardware-specific acceleration backends, allowing multiple backends to be installed independently and selected without rebuilding the Python package.

Currently packaged backends include:

- CPU / OpenBLAS, including multiple optimized CPU variants
- Vulkan
- NVIDIA CUDA 12.4
- NVIDIA CUDA 12.9
- NVIDIA CUDA 13.3
- AMD ROCm Core SDK 10.1 / HIP
- Intel oneAPI SYCL

Versioned CUDA and ROCm backends are designed to coexist where applicable, with `update-alternatives` used to select the active backend implementation. The packaging also includes transitional packages for compatibility with older package names.

Although the packaging is developed and tested on **Debian 13 (Trixie)**, it can in practice be adapted and built on most Linux distributions based on Debian packages, provided that the required build dependencies and vendor toolkits/frameworks are available. Depending on the selected backends, this may include NVIDIA CUDA, AMD ROCm or Intel oneAPI/SYCL.

### Vendor APT repositories

The current Debian packaging builds all configured backends in one
source-package build. All build dependencies listed in `debian/control`,
including the CUDA, ROCm and SYCL toolchains, are required.

At runtime, accelerator backend packages can be installed individually.

#### NVIDIA CUDA

The CUDA 12.9/13.x packages used by this packaging are obtained from NVIDIA's Debian repository. The repository currently used here is NVIDIA's Debian 12 x86_64 repository, which is also usable for these builds on Debian 13.

Install the repository key:

```bash
wget -qO- https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/3bf863cc.pub \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/nvidia-cuda-debian12.gpg >/dev/null
```

Add the repository:

```bash
echo "deb [signed-by=/usr/share/keyrings/nvidia-cuda-debian12.gpg] https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/ /" \
  | sudo tee /etc/apt/sources.list.d/nvidia-cuda.list
```

Then refresh APT metadata:

```bash
sudo apt update
```

#### AMD ROCm

AMD provides a Debian 13 multi-architecture ROCm repository.

Install the repository key:

```bash
wget -qO- https://repo.amd.com/rocm/packages-multi-arch/gpg/rocm.gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/amdrocm.gpg
```

Add the repository:

```bash
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/amdrocm.gpg] https://repo.amd.com/rocm/packages-multi-arch/debian13 stable main" \
  | sudo tee /etc/apt/sources.list.d/rocm.list
```

Then refresh APT metadata:

```bash
sudo apt update
```

#### Intel oneAPI / SYCL

Intel provides the oneAPI APT repository containing the DPC++/C++ compiler and the required SYCL libraries.

Install the repository key:

```bash
wget -qO- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/oneapi-archive-keyring.gpg >/dev/null
```

Add the repository:

```bash
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" \
  | sudo tee /etc/apt/sources.list.d/oneapi.list
```

Then refresh APT metadata:

```bash
sudo apt update
```

The Debian packaging files are maintained separately from the upstream Python package functionality and are intended to provide clean system integration, dependency handling and reproducible backend builds.

**Debian packaging author / maintainer:** `ByCzech <byczech-at-gmail.com>`

> The original `llama-cpp-python` project is developed and maintained by its upstream authors. The Debian packaging additions in this repository are maintained independently.
