# Preprocessing of an Open-Source Dataset for Synthetic CT Generation from Brain MRI

**Bachelor's Thesis in Computer and Biomedical Engineering**  
Università degli Studi "Magna Græcia" di Catanzaro — Academic Year 2024/2025  
**Author:** Giusy Francesca Scarpelli  
**Supervisor:** Prof. Paolo Zaffino  

---

## Overview

This repository accompanies my Bachelor's thesis and documents the preprocessing pipeline, experimental results, and outcome visualizations from a study on **synthetic CT (sCT) generation from brain MRI** using deep learning.

The goal of the project was to investigate how the quality of segmentation mask preprocessing influences the performance of a deep learning model trained to generate synthetic CT images from T1-weighted MRI scans, in the context of MRI-only radiotherapy planning.

📄 **Full thesis available on Zenodo: https://doi.org/10.5281/zenodo.18941244 **

---

## Background

In modern radiotherapy, CT and MRI are used in a complementary fashion: CT provides electron density maps for dose calculation, while MRI offers superior soft-tissue contrast for target delineation. Acquiring both modalities introduces workflow complexity, additional radiation exposure, and registration uncertainties.

Synthetic CT (sCT) images — generated from MRI using deep learning algorithms — represent a promising solution to enable MRI-only radiotherapy workflows, reducing the reliance on conventional CT acquisitions.

---

## Dataset

This work used a subset of the **SynthRAD2023** open-source dataset:

- **Source:** [SynthRAD2023 Grand Challenge](https://doi.org/10.1002/mp.16529) (Thummerer et al., 2023)
- **License:** Creative Commons CC-BY-NC 4.0
- **Task:** Task 1 — MRI to CT conversion, brain district
- **Subset used:** 33 patients from Centre A (training set), T1-weighted MRI without contrast

Images were pre-registered (MRI on CT), resampled to 1×1×1 mm³ isotropic resolution, and stored in NIfTI format (.nii.gz).

---

## Methods

### 1. Segmentation Mask Preprocessing (3D Slicer)

The original body contour masks provided with the dataset presented inaccuracies in several patients. Since evaluation metrics (MAE and bias) are computed exclusively within the mask, precise contour definition is critical.

Masks were refined for all 33 patients using the **Foreground Masking (BRAINS)** module in [3D Slicer](https://www.slicer.org/), by iteratively adjusting four parameters:

| Parameter | Description |
|---|---|
| Otsu Percentile Threshold | Controls sensitivity of automatic thresholding |
| Threshold Correction Factor | Multiplicative factor to adjust Otsu threshold (range: 0.8–1.2) |
| Closing Size | Morphological closing element size (mm) |
| ROIAuto Dilate Size | Final dilation of the mask to preserve outer contours |

Total preprocessing time: ~10 hours across all 33 patients.

### 2. Deep Learning Model

The sCT generation model is based on the **multiplanar U-Net architecture** described in:

> Spadea et al. (2019). *Deep Convolution Neural Network (DCNN) Multiplane Approach to Synthetic CT Generation from MR Images — Application in Brain Proton Therapy.* International Journal of Radiation Oncology Biology Physics, 105(3), 495–503. https://doi.org/10.1016/j.ijrobp.2019.06.2535

The training and inference scripts were provided by the research group and are not included in this repository.

**Key training details:**
- Framework: PyTorch + NumPy + SimpleITK
- GPU training (~26–28 hours per cycle)
- 17 training iterations (leave-2-out cross-validation)
- 20 checkpoints saved per cycle → 20 sCT generated per patient (660 total)

### 3. Evaluation Metrics

Performance was evaluated using voxel-wise metrics computed inside the body mask:

- **MAE (Mean Absolute Error)** — average absolute deviation in Hounsfield Units (HU)
- **Bias** — signed mean error (positive = underestimation, negative = overestimation)

---

## Results

### Quantitative Results

Across all 660 generated sCT images:

| Metric | Value |
|---|---|
| Mean MAE | 96.05 ± 11.67 HU |
| MAE range | 69.78 – 132.06 HU |
| Mean Bias | 2.51 ± 17.60 HU |
| Bias range | -49.95 – +44.23 HU |

Best performing patient: **1BA222** (MAE = 69.78 HU)  
Most challenging patient: **1BA131** (MAE = 132.06 HU)

### Visual Results

Sample comparisons between reference CT and generated sCT across axial, coronal, and sagittal planes are available in the [`results/figures/`](results/figures/) folder.

---

## Repository Structure

```
├── README.md
├── results/
│   ├── figures/              # MAE and bias distribution plots
│   └── sample_sCT/           # Visual CT vs sCT comparisons (selected patients)
├── preprocessing/
│   └── parameters_table.csv  # 3D Slicer parameters used per patient
└── analysis/
    └── metrics_plots.py      # Python script for MAE/bias visualization
```

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| [3D Slicer](https://www.slicer.org/) | Segmentation mask refinement |
| [PyTorch](https://pytorch.org/) | Deep learning framework |
| [SimpleITK](https://simpleitk.org/) | Medical image I/O and processing |
| [NumPy](https://numpy.org/) | Numerical computation |
| Python (matplotlib) | Results visualization |

---

## Citation

If you use or reference this work, please cite the thesis:

> Scarpelli, G.F. (2025). *Preprocessing di un dataset open source per la generazione di TC sintetiche* [Bachelor's thesis, Università degli Studi "Magna Græcia" di Catanzaro]. Zenodo. *[DOI to be added]*

---

## Acknowledgements

This work was supervised by **Prof. Paolo Zaffino** and supported by **Ing. Lorena Romeo**, whose guidance was essential throughout the project. The deep learning framework was developed by Spadea et al. and graciously made available for this study.

---

## License

The content of this repository (figures, analysis scripts, documentation) is released under the [MIT License](LICENSE).  
The thesis PDF is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
The SynthRAD2023 dataset is subject to its own [CC-BY-NC 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/).
