<p align="center">
  <img src="images/indcomp.svg" />
</p>

---
 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**indcomp** is a package for performing indirect treatment comparisons.

inccomp currently supports the Matching-Adjusted Indirect Comparison (MAIC) approach, implemented in line with [NICE's guidance](http://nicedsu.org.uk/technical-support-documents/population-adjusted-indirect-comparisons-maic-and-stc/).


## Install

<pre>
# PyPI
pip install indcomp
</pre>

### Dependencies
* NumPy
* SciPy
* pandas
* matplotlib

---

## Usage - MAIC

```python
from indcomp import MAIC
from indcomp.datasets import load_NICE_DSU18

# load simulated Individual Patient Data (IPD) for trial AB
# load simulated Aggregated Data (AgD) for trial AC
df_AB_IPD, df_AC_AgD = load_NICE_DSU18()
print(f"Number of AB patients: {len(df_AB_IPD)}")
print(df_AB_IPD.sample(5))
```
```console
> Number of AB patients: 500
>       ID  age  gender trt  y
> 113  114   73    Male   A  1
> 371  122   45  Female   B  1
> 77    78   48    Male   A  1
> 441  192   49    Male   B  0
> 120  121   68    Male   A  1
```
```python
# 300 AC patients
print(df_AC_AgD.round(2))
```
```console
>    age.mean  age.sd  N.male  prop.male  y.A.sum  y.A.bar  N.A  y.C.sum  y.C.bar  N.C
> 0     50.27    3.12      68       0.23      125     0.83  150       21     0.14  150
```
```python
# adjust df_AB_IPD['age'] to have same mean as df_AC_AgD['age.mean'] and
# adjust df_AB_IPD['age'] to have same std as df_AC_AgD['age.sd']
maic=MAIC(
    df_index=df_AB_IPD,
    df_target=df_AC_AgD,
    match={
        "age.mean": ("mean", "age"),
        "age.sd": ("std", "age", "age.mean")
    }
)
# compare unweighted populations, before performing matching adjustment
maic.compare_populations()
```
<p align="center">
  <img src="figures/NICE_DSU18_populations_unweighted.png" />
</p>

```python
# calculate and examine weights and Effective Sample Size
maic.calc_weights()
print(f"Effective Sample Size: {maic.ESS_:.2f}")  # original sample size: 500 patients
maic.plot_weights()
```
```console
> Effective Sample Size: 178.56
```
<p align="center">
  <img src="figures/NICE_DSU18_weights.png" />
</p>

```python
# compare weighted populations, after performing matching adjustment
maic.compare_populations(weighted=True)
```
<p align="center">
  <img src="figures/NICE_DSU18_populations_weighted.png" />
</p>