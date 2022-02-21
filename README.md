<p align="center">
  <img width="400" src="./images/indcomp.png" />
</p>

---
 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 [![PyPI version](https://badge.fury.io/py/indcomp.svg)](https://badge.fury.io/py/indcomp)
 ![Coverage](./images/coverage.svg)
 [![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

**indcomp** is a package for performing indirect treatment comparisons (ITCs).

indcomp currently supports the Matching-Adjusted Indirect Comparison (MAIC) approach, implemented as per [NICE's guidance](https://research-information.bris.ac.uk/en/publications/nice-dsu-technical-support-document-18-methods-for-population-adj).

View the [indcomp documentation](https://aidancooper.github.io/indcomp/).

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

## Usage - Matching-Adjusted Indirect Comparison (MAIC)

For this example, we use simulated data as per [NICE's worked example](http://nicedsu.org.uk/wp-content/uploads/2017/05/TSD18-Appendix-D-Worked-example-of-MAIC-and-STC.pdf).

The objective is to weight individual patient-level data (IPD) for a hypothetical randomised control trial (RCT) comparing treatments _A_ and _B_, to match on specified characteristics described in aggregated data for a hypothetical RCT comparing treatments _A_ and _C_. In this example, we weight the _AB_ trial such that the age matches the mean and standard deviation of the _AC_ trial.

This example illustrates a common real-world scenario in which _B_ and _C_ are interventions for a disease, and _A_ is a placebo. Typically, MAIC is used to fairly evaluate IPD for a potential new treatment (_B_) against that of an existing treatment (_C_) for which only aggregate data is available (the published results for the _AC_ trial).

The _AB_ trial comprises 500 individual patient records.

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

The _AC_ trial is aggregate data for 300 patients.

```python
# 300 AC patients
print(df_AC_AgD.round(2))
```
```console
>    age.mean  age.sd  N.male  prop.male  y.A.sum  y.A.bar  N.A  y.C.sum  y.C.bar  N.C
> 0     50.27    3.12      68       0.23      125     0.83  150       21     0.14  150
```

We instantiate and configure a `MAIC` instance to weight the _AB_ data to yield the same mean and standard deviation age as the _AC_ trial. These characteristics are quite different for the starting, unweighted data.

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
  <img src="./figures/NICE_DSU18_populations_unweighted.png" />
</p>

After calculating the weights, we examine the effective sample size (ESS) and plot the distribution of weights. Our sample size decreases from the original 500 to an effective sample size of 178.56.

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
  <img src="./figures/NICE_DSU18_weights.png" />
</p>

After applying the weights, the mean and standard deviation age of the _AB_ trial now matches that of the _AC_ trial.

```python
# compare weighted populations, after performing matching adjustment
maic.compare_populations(weighted=True)
```
<p align="center">
  <img src="./figures/NICE_DSU18_populations_weighted.png" />
</p>
