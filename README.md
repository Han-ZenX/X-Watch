# X-Watch

X-Watch 是一款开源智能手表项目，主控芯片为 **STM32L4R9AII6U**，图形界面基于 **TouchGFX** 开发。本仓库统一管理硬件设计、嵌入式固件、配套软件、文档与测试。

> 项目处于早期开发阶段（硬件 Rev1.0），接口与目录结构可能随迭代调整。

## 核心方案

| 项目 | 选型 |
|------|------|
| 主控 MCU | STM32L4R9AII6U（Arm Cortex-M4F，120 MHz，2 MB Flash，640 KB SRAM，UFBGA169） |
| 图形框架 | TouchGFX（配合 TouchGFX Designer 设计界面） |
| 图形加速 | Chrom-ART（DMA2D）、GFXMMU，显示接口可选 LTDC / MIPI DSI |
| 硬件 EDA | KiCad |
| 固件构建 | CMake + GCC ARM（arm-none-eabi） |
| 大文件管理 | Git LFS |

### 为什么选 STM32L4R9

- **超低功耗**：STM32L4+ 系列，适合电池供电的穿戴设备。
- **图形能力完整**：片上集成 LTDC、MIPI DSI Host、Chrom-ART 加速器和 GFXMMU（适合圆形屏帧缓冲），无需外置图形芯片。
- **TouchGFX 官方支持**：ST 提供 STM32L4R9I-DISCO 参考设计（圆形 AMOLED 屏），可作为软硬件起点，手册见 [docs/references/Rev1.0](docs/references/Rev1.0)。

## 目录结构

```
X-Watch/
├── firmware/      # 嵌入式固件（app / hal / drivers / services 四层架构）
├── hardware/      # 硬件设计（原理图、PCB、BOM、Gerber、3D、引脚表）
├── software/      # 配套软件（desktop / mobile / cloud）
├── tools/         # 构建脚本与辅助工具
├── docs/          # 项目文档
├── tests/         # 单元测试 / 集成测试 / 硬件在环测试
└── ci/            # CI/CD 流水线配置
```

完整的架构说明见 [docs/architecture/architecture.md](docs/architecture/architecture.md)。

## 快速开始

### 1. 获取代码

```bash
git lfs install
git clone git@github.com:Han-ZenX/X-Watch.git
```

### 2. 开发环境

- [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html)：外设与时钟配置
- [TouchGFX Designer](https://www.st.com/en/development-tools/touchgfxdesigner.html)：UI 设计与代码生成
- GCC ARM 工具链（arm-none-eabi-gcc）、CMake ≥ 3.20、Ninja
- [KiCad](https://www.kicad.org/)：打开 `hardware/schematic/v1.0/XWatch_Rev1.0/` 下的工程
- 调试器：ST-LINK

### 3. 编译固件

```bash
cd firmware
cmake -B build -G Ninja -DBOARD=default
cmake --build build
```

或使用构建脚本：

```bash
python tools/scripts/build.py --board=default
```

## 硬件

- 原理图 / PCB：`hardware/schematic/v1.0/XWatch_Rev1.0/`（KiCad 工程）
- 引脚分配：[hardware/pinout/pinout.md](hardware/pinout/pinout.md)
- 每次硬件改版需同步更新引脚表与 `firmware/boards/` 下对应的板级配置。

## 开发计划

- [ ] 硬件 Rev1.0 原理图与 PCB 完成
- [ ] STM32L4R9 板级支持（时钟、电源、调试串口）
- [ ] 显示屏驱动与 TouchGFX 移植
- [ ] 触摸驱动接入
- [ ] 基础表盘与界面
- [ ] 低功耗管理

## 变更记录

见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
