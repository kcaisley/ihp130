# IHP130 HDL21 PDK

HDL21 device compilation and FRIDA layout metadata for the IHP SG13G2 130 nm
BiCMOS technology. The repository contains no foundry model files or other PDK
source data.

This code was extracted from the public FRIDA repository while preserving its
subtree history. Its HDL21 integration originated from the Hdl21 IHP package
and retains that package's BSD 3-Clause license and attribution.

FRIDA mounts this repository at `pdk/ihp130`, where it is imported as
`pdk.ihp130`. Run its tests from an initialized FRIDA checkout:

```text
uv run pytest pdk/ihp130/tests
uv run pytest pdk/ihp130/tests -m site_pdk
```
