# 🛠️ STM32CubeMX & VS Code Hybrid Setup Guide
## Workflow for NUCLEO-H533RE in Antigravity / VS Code

This guide walks you through the exact setup steps once your **STM32CubeMX** and **STM32CubeCLT** installers finish downloading.

---

### Step 1: Install STM32CubeCLT & STM32CubeMX

1. **Run the STM32CubeCLT Installer:**
   * Keep default install path: `C:\ST\STM32CubeCLT_x.x.x`
   * This installs the **GNU Arm Embedded Toolchain**, **GDB Server**, and **STM32CubeProgrammer**.
2. **Run the STM32CubeMX Installer:**
   * Keep default install path: `C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeMX`
   * This installs the visual pinout and clock-tree configurator.

---

### Step 2: Configure Project in STM32CubeMX (Targeting CMake)

1. Launch **STM32CubeMX**.
2. Click **Access to Board Selector**:
   * Search for: `NUCLEO-H533RE`
   * Select it and click **Start Project**.
   * When asked *"Initialize all peripherals with their default Mode?"*, click **Yes**.
3. **Configure Smart-ASHA Pins & Buses:**
   * **`PB9`** -> Set to `I2C1_SDA` (Primary 50 kHz bus to TCA9548A multiplexer).
   * **`PB8`** -> Set to `I2C1_SCL`.
   * **`PB11`** -> Set to `I2C2_SDA` (Secondary 400 kHz bus to MAX30105).
   * **`PB10`** -> Set to `I2C2_SCL`.
   * **`PA0`** -> Set to `ADC1_IN1` (AD8232 Lead-I ECG).
   * **`PA1`** -> Set to `ADC1_IN2` (MQ-135 Gas sensor).
   * **`PA2`** / **`PA3`** -> Set to `USART2_TX` / `USART2_RX` (Quectel EC200U 4G modem).
   * **`PC4`** / **`PC5`** -> Set to `USART3_TX` / `USART3_RX` (External BLE bridge).
   * **`PA5`** -> Set to `GPIO_Output` (Green triage LED).
4. **Configure Clock Tree:**
   * Navigate to the **Clock Configuration** tab.
   * Set SYSCLK (System Clock) to **250 MHz** (CubeMX will auto-resolve PLL multipliers).
5. **Project Manager Settings (CRITICAL STEP):**
   * Go to **Project Manager** tab on the top bar.
   * Project Name: `Smart_ASHA_H5`
   * Project Location: `C:\Users\Acer\OneDrive\Desktop\DESKTOP VANSH\Smart Asha\STM\cubemx`
   * **Toolchain / IDE:** Select **CMake** from the dropdown menu! *(Do not select MDK-ARM or IAR).*
   * Check the box: *"Generate peripheral initialization as a pair of '.c/.h' files per peripheral"*.
6. Click **GENERATE CODE** in the top-right corner.

---

### Step 3: Open & Build in Antigravity / VS Code

1. In Antigravity / VS Code, open the folder:  
   `STM/cubemx/Smart_ASHA_H5`
2. The **STM32 VS Code Extension** and **CMake Tools** will automatically pop up with:
   > *"Configuring project using CMake and STM32CubeCLT..."*
3. You will see the **STM32 icon** on the left Activity Bar:
   * **Build:** Click the **Build** button in the bottom status bar (or press `F7`).
   * **Flash & Debug:** Connect your NUCLEO-H533RE board via USB-C, and press **`F5`**!
   * It will automatically flash the microcontroller using ST-LINK/V3E and break at `main()`.

