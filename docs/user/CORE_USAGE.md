# 核心用法说明

本文档用于说明 `neuroutils` 的特色中层能力。  
当前先给出第一个核心功能：**3D 神经元图像的 2.5D 旋转投影标注流程**。

## 功能 1：3D TIFF -> 2.5D 旋转标注 -> 3D Mask 恢复

### 目标

对一个 3D `tif` 神经元图像：
- 自动生成多角度旋转 MIP 图（供人工标注）
- 保存恢复配置文件
- 读取标注多边形并恢复为 3D mask

---

### 环节 A：导出 2.5D 旋转投影

函数：
- `neuroutils.segmentation.export_rotational_mips_for_2p5d_annotation`

输入：
- `image_file`: 3D tif 路径（`z,y,x`）
- `output_dir`: 输出文件夹
- 可选参数：
  - `rotate_times`（默认 `12`）
  - `axes_rot`（默认 `(1,2)`，即绕 `y-x` 平面旋转）
  - `mip_axis`（默认 `1`）
  - `order`（默认 `1`）
  - `flip_tif`（默认 `False`）

输出：
- `output_dir/*.tif`：旋转后的 MIP 图（已转 `uint8`）
- `output_dir/rotation_mip_config.json`：恢复配置（关键）
- 返回值 `dict`：包含来源图像、形状、角度、条目清单

示例：

```python
from neuroutils.segmentation import export_rotational_mips_for_2p5d_annotation

cfg = export_rotational_mips_for_2p5d_annotation(
    image_file=r"E:\neuroutils\examples\soma_label\image_xxx.tif",
    output_dir=r"E:\neuroutils\examples\soma_label\image_xxx_2p5d",
    rotate_times=12,
    mip_axis=1,
)
print(cfg["rotate_times"], len(cfg["entries"]))
```

---

### 环节 B：人工标注（外部执行）

标注者需要在 `output_dir` 中：
- 按 `rotation_mip_config.json` 的 `entries[*].label_file` 文件名
- 为每张 MIP 生成对应的 polygon 标注 JSON（LabelMe 格式）

最关键字段：
- `imageHeight`
- `imageWidth`
- `shapes[].points`（多边形点）

---

### 环节 C：从标注文件夹恢复 3D mask

函数：
- `neuroutils.segmentation.restore_3d_mask_from_2p5d_annotation_folder`

输入：
- `annotation_dir`: 包含 `rotation_mip_config.json` 和标注 JSON 的文件夹
- 可选：
  - `output_mask_file`: 输出 3D mask tif 路径
  - `strict`: 若 `True`，缺任何 JSON 直接报错；默认 `False`

输出：
- 返回 `np.ndarray`（`z,y,x`，二值 mask）
- 若给定 `output_mask_file`，同时保存为 `0/255` 的 tif

示例：

```python
from neuroutils.segmentation import restore_3d_mask_from_2p5d_annotation_folder

mask = restore_3d_mask_from_2p5d_annotation_folder(
    annotation_dir=r"E:\neuroutils\examples\soma_label\image_xxx_2p5d",
    output_mask_file=r"E:\neuroutils\examples\soma_label\image_xxx_2p5d_mask.tif",
    strict=False,
)
print(mask.shape, mask.dtype)
```

---

### 最小完整流程

```python
from neuroutils.segmentation import (
    export_rotational_mips_for_2p5d_annotation,
    restore_3d_mask_from_2p5d_annotation_folder,
)

ann_dir = r"E:\neuroutils\examples\soma_label\case_001_2p5d"

# 1) 导出旋转 MIP
export_rotational_mips_for_2p5d_annotation(
    image_file=r"E:\neuroutils\examples\soma_label\case_001.tif",
    output_dir=ann_dir,
    rotate_times=12,
)

# 2) 人工在 ann_dir 内完成 JSON 标注

# 3) 恢复 3D mask
restore_3d_mask_from_2p5d_annotation_folder(
    annotation_dir=ann_dir,
    output_mask_file=r"E:\neuroutils\examples\soma_label\case_001_mask3d.tif",
)
```

---

### 注意事项

- 输入图像必须是 3D（`z,y,x`）。
- 恢复严格依赖 `rotation_mip_config.json`，不要改动 `entries` 顺序和文件名约定。
- 若需要“缺标注即报错”，把 `strict=True`。
- 本流程依赖 `scipy.ndimage.rotate`（未安装 `scipy` 会报错）。

