---
title: "NICE DSU Technical Support Document 18 - Appendix D"
author: "Aidan"
date: "07/01/2022"
output:
  html_document:
    keep_md: true
---




```r
library(dplyr)
library(tidyr)
library(wakefield)
library(ggplot2)
library(sandwich)

set.seed(1374988)
```

## Background and resources

This report is a copy of the text and code shown in NICE's worked example of MAIC and STC. The purpose of this notebook is to generate data and reproduce NICE's analysis in R, to validate the results of this Python implementation. Due to differences in system and package versions, the data generated - and therefore the results - in this analysis do not exactly match the original document (despite using the same seed).

The text and code are lifted from the Appendix document below with almost no modification. All credit for this R implementation goes to the original authors.

 * [NICE DSU Technical Support Document 18](http://nicedsu.org.uk/wp-content/uploads/2018/08/Population-adjustment-TSD-FINAL-ref-rerun.pdf)
 * [Appendix D: Worked example of MAIC and STC](http://nicedsu.org.uk/wp-content/uploads/2017/05/TSD18-Appendix-D-Worked-example-of-MAIC-and-STC.pdf)

## Creating simulated datasets

First, we create some simulated data. We use the package `wakefield`, which provides an easy way to quickly create realistic simulated datasets with pre-set variable types. We will consider two variables, age and gender, with age being an effect modifier and gender a purely prognostic variable.

Here, we set the parameters of the simulation scenario, defining study characteristics (study sizes, age ranges, proportion of females) and the parameters of the outcome model.


```r
# Study characteristics
N_AB <- 500
N_AC <- 300
agerange_AB <- 45:75
agerange_AC <- 45:55
femalepc_AB <- 0.64
femalepc_AC <- 0.8

# Outcome model
b_0 <- 0.85
b_gender <- 0.12
b_age <- 0.05
b_age_trt <- -0.08
b_trt_B <- -2.1
b_trt_C <- -2.5
```

For our example, we will generate binary outcomes. The true logistic outcome model which we use to simulate the data will be:

$$logit(p_{it})=0.85+0.12\cdot\ male_{it}+0.05\cdot\ (age_{it}-40)+(\beta_{t}-0.08\cdot\ (age_{it}-40))\parallel(t\neq A)$$

where $\beta_{B}=-2.1$ and $\beta_{C}=-2.5$. The parameters of the model are interpreted as log odds ratios, and $p_{it}$ is the probability of an event for individual $i$ receiving treatment $t$.

### AB trial

The $AB$ trial ($N_{(AB)}=500$) will have ages from 45 to 75 and 64% females. The `wakefield` package provides a framework for generating simulated datasets, including many convenience functions; we make use of just a small number here, including age to uniformly generate ages within an age range, gender to generate a factor variable of genders with given probabilities, and id to create a unique ID for each individual.


```r
# generate data for the AB trial
AB.IPD <-
  rbind(
    
    # Generate A arm
    r_data_frame(n = N_AB/2, # Number of individuals in arm A
                 id, # Unique ID
                 age = age(x = agerange_AB), # Generate ages
                 gender = gender(prob = c(1 - femalepc_AB, femalepc_AB)), # Generate genders
                 trt = "A" # Assign treatment A
    ),
    
    # Generate B arm
    r_data_frame(n = N_AB/2, # Number of individuals in arm B
                 id, # Unique ID
                 age = age(x = agerange_AB), # Generate ages
                 gender = gender(prob = c(1 - femalepc_AB, femalepc_AB)), # Generate genders
                 trt = "B" # Assign treatment B
    )
  ) %>%
  
  # Generate outcomes using logistic model
  mutate(
    yprob = 1 / (1 + exp(-(
      b_0 + b_gender * (gender == "Male") + b_age * (age - 40) +
        if_else(trt == "B", b_trt_B + b_age_trt * (age - 40), 0)
    ))),
    y = rbinom(N_AB, 1, yprob)
  ) %>%
  select(-yprob) # Drop the yprob column

write.csv(AB.IPD, file="..\\data\\AB_IPD.csv", row.names=FALSE)
```

Tabulate the AB trial, to check that our ???randomisation??? has worked, and examine the generated outcomes.


```r
AB.IPD %>% group_by(trt) %>%
  summarise(n(), mean(age), sd(age), `n(male)`=sum(gender=="Male"),
            `%(male)`=mean(gender=="Male"), sum(y), mean(y))
```

```
## # A tibble: 2 x 8
##   trt   `n()` `mean(age)` `sd(age)` `n(male)` `%(male)` `sum(y)` `mean(y)`
##   <chr> <int>       <dbl>     <dbl>     <int>     <dbl>    <int>     <dbl>
## 1 A       250        60.5      9.01        99     0.396      221     0.884
## 2 B       250        59.9      9.06        90     0.36        41     0.164
```

### AC trial

The $AC$ trial ($N_{(AC)}=300$) will have ages from 45 to 55 and 80% females.


```r
# generate data for the AC trial
AC.IPD <-
  rbind(
    
    # Generate A arm
    r_data_frame(n = N_AC/2, # Number of individuals in arm A
                 id, # Unique ID
                 age = age(x = agerange_AC), # Generate ages
                 gender = gender(prob = c(1 - femalepc_AC, femalepc_AC)), # Generate genders
                 trt = "A" # Assign treatment A
    ),
    
    # Generate C arm
    r_data_frame(n = N_AC/2, # Number of individuals in arm C
                 id, # Unique ID
                 age = age(x = agerange_AC), # Generate ages
                 gender = gender(prob = c(1 - femalepc_AC, femalepc_AC)), # Generate genders
                 trt = "C" # Assign treatment C
    )
  ) %>%
  
  # Generate outcomes using logistic model
  mutate(
    yprob = 1 / (1 + exp(-(
      b_0 + b_gender * (gender == "Male") + b_age * (age - 40) +
        if_else(trt == "C", b_trt_C + b_age_trt * (age - 40), 0)
    ))),
    y = rbinom(N_AC, 1, yprob)
  ) %>%
  select(-yprob) # Drop the yprob column
```

Tabulate the AC trial, to check that our ???randomisation??? has worked, and examine the generated outcomes.


```r
AC.IPD %>% group_by(trt) %>%
  summarise(n(), mean(age), sd(age), `n(male)`=sum(gender=="Male"),
            `%(male)`=mean(gender=="Male"), sum(y), mean(y))
```

```
## # A tibble: 2 x 8
##   trt   `n()` `mean(age)` `sd(age)` `n(male)` `%(male)` `sum(y)` `mean(y)`
##   <chr> <int>       <dbl>     <dbl>     <int>     <dbl>    <int>     <dbl>
## 1 A       150        50.4      3.06        32     0.213      125     0.833
## 2 C       150        50.2      3.20        36     0.24        21     0.14
```

For analysis we will have access only to the aggregate data, as if from a published study. Here, we aggregate the IPD to obtain summaries, which will be used for the MAIC and STC analyses.


```r
# aggregate AC trial data
AC.AgD <-
  cbind(
    # Trial level stats: mean and sd of age, number and proportion of males
    summarise(AC.IPD, age.mean = mean(age), age.sd = sd(age),
              N.male = sum(gender=="Male"), prop.male = mean(gender=="Male")),
    # Summary outcomes for A arm
    filter(AC.IPD, trt == "A") %>%
      summarise(y.A.sum = sum(y), y.A.bar = mean(y), N.A = n()),
    # Summary outcomes for C arm
    filter(AC.IPD, trt == "C") %>%
      summarise(y.C.sum = sum(y), y.C.bar = mean(y), N.C = n())
  )

write.csv(AC.AgD, file="..\\data\\AC_AgD.csv", row.names=FALSE)
AC.AgD
```

```
##   age.mean   age.sd N.male prop.male y.A.sum   y.A.bar N.A y.C.sum y.C.bar N.C
## 1 50.27333 3.124821     68 0.2266667     125 0.8333333 150      21    0.14 150
```

## MAIC

We are now ready to proceed with our analyses. First, we will estimate the population-adjusted indirect comparison using MAIC. This involves estimating a logistic propensity score model, which includes all effect modifiers but no prognostic variables. This is equivalent to the following model on the log of the individual weights:

$$log(w_{it}=\alpha_{0}+\alpha_{1}^TX_{it}^{EM}$$

The weights are estimated using the method of moments to match the effect modifier distributions between the $AB$ and $AC$ trials. This is equivalent to minimising

$$\sum_{i,t}exp(\alpha_{1}^TX_{it}^{EM})$$

when $X_{(AC)}^{EM}=0$

In order to do this, we define the objective function to minimise (as above), and the gradient function (its derivative) which will be used by the minimisation algorithm.


```r
objfn <- function(a1, X){
  sum(exp(X %*% a1))
}

gradfn <- function(a1, X){
  colSums(sweep(X, 1, exp(X %*% a1), "*"))
}
```

To satisfy $\bar{X}_{AC}^{EM}=0$, we create centred versions of the effect modifiers by subtracting $\bar{X}_{AC}^{EM}$ from $X^{EM}$ in both trials. Here only age is an effect modifier, and we can balance this in both mean and standard deviation as we have observed `age.mean` and `age.sd` in the $AC$ trial. We therefore include centred versions of `age` and `age??2` for each individual in the $AB$ trial in the weighting model. Centring the mean is simple, but centring higher moments requires some attention: due to aggregation, we cannot simply centre `age??2` from the $AB$ trial with `age.sd` from the $AC$ trial. We use the variance formula $var(X)=\mathbb{E}(X^2)-\mathbb{E}(X)^2$, and centre `age??2` in the $AB$ trial with `age.mean??2 + age.sd??2` in the $AC$ trial. Here we make use of the `sweep` function to simultaneously centre the two row vectors `age` and `age??2` by subtracting `age.mean` and `age.mean??2 + age.sd??2` respectively:


```r
X.EM.0 <- sweep(with(AB.IPD, cbind(age, age^2)), 2,
                with(AC.AgD, c(age.mean, age.mean^2 + age.sd^2)), '-')
```

To estimate $\alpha_{1}$, we use the function `optim` to minimise the function `objfn`. The method we tell optim to use is BFGS (after Broyden, Fletcher, Goldfarb and Shanno), which makes use of the gradient function `gradfn` we specified to aid minimisation. We have to specify an initial value in the par argument (we choose `c(0,0)` here), and $X=X.EM.0$ is passed to `objfn` and `gradfn` as an additional argument.


```r
print(opt1 <- optim(par = c(0,0), fn = objfn, gr = gradfn, X = X.EM.0, method = "BFGS"))
```

```
## $par
## [1]  3.68798519 -0.03696784
## 
## $value
## [1] 196.4207
## 
## $counts
## function gradient 
##       68       14 
## 
## $convergence
## [1] 0
## 
## $message
## NULL
```

```r
a1 <- opt1$par
```

The output generated simply states that convergence has occurred successfully (`$convergence = 0`). The estimate $\hat{\alpha}_{1}$ is found in `$par`. (The other outputs are `$value`, the value of `objfn` at the minimum, `$counts`, the number of evaluations of `objfn` and `gradfn` before convergence, and `$message`, for any additional information from the minimisation algorithm.)

The estimated weights for each individual are then found by $\hat{w_{it}}=exp(X_{it}^{EM}\hat{\alpha_1})$. We do not need to estimate $\alpha_{0}$, as this constant cancels out.


```r
wt <- exp(X.EM.0 %*% a1)
```

It is easier to examine the distribution of the weights by scaling them, so that the rescaled weights are relative to the original unit weights of each individual; in other words, a rescaled weight > 1 means that an individual carries more weight in the reweighted population than in the $AB$ population, and a rescaled weight < 1 means that an individual carries less weight. The rescaled weight is calculated as

$$\tilde{w_{it}}=\frac{\hat{w_{it}}}{\sum_{i,t}\hat{w_{it}}}\cdot N_{(AB)}$$


```r
wt.rs <- (wt / sum(wt)) * N_AB  # rescaled weights

summary(wt.rs)
```

```
##        V1         
##  Min.   :0.00000  
##  1st Qu.:0.00002  
##  Median :0.03803  
##  Mean   :1.00000  
##  3rd Qu.:2.10475  
##  Max.   :3.67109
```


```r
qplot(wt.rs, geom="histogram",
      xlab = "Rescaled weight (multiple of original unit weight)",
      binwidth=0.25)
```

![](NICE_DSU_Technical_Support_Document-Appendix_D_files/figure-html/plot_weights-1.png)<!-- -->

The mean of the rescaled weights is not informative, as it is guaranteed to be 1:

$$\frac{1}{N_{(AB)}}\sum_{i,t}\tilde{w_{it}}=\frac{1}{N_{(AB)}}\sum_{i,t}\frac{\hat{w_{it}}}{\sum_{i,t}\hat{w_{it}}}\cdot N_{(AB)}=1$$

Here, the rescaled weights range from 0 to 3.44, and the median is heavily skewed towards zero (0.07). A histogram of the weights is also very helpful to present, and clearly shows that a large number of individuals have been given zero (or close to zero) weight. This is not surprising, as the age range in the $AB$ trial (45 to 75) is much wider than that in the $AC$ trial (45 to 55). There are therefore a large number of individuals from the $AB$ trial who have been excluded. More positively, there are no very large weights, as the distribution of effect modifiers in the $AC$ population is entirely contained within that of the $AB$ population (there are no ages in the $AC$ population outside of those observed in the $AB$ population).

The approximate effective sample size is calculated as

$$\frac{\sum_{i,t}(\hat{w_{it}})^2}{\sum_{i,t}\hat{w_{i,t}^2}}$$


```r
sum(wt)^2/sum(wt^2)
```

```
## [1] 178.5609
```

This is quite a reduction from the original 500, but is still reasonably large. (The actual ESS is likely to be larger than this, as the weights are not fixed and known ??? see section 2.2.1.)

Note that age is balanced (in terms of mean and SD) with the $AC$ population after weighting.


```r
AB.IPD %>%
  mutate(wt) %>%
  summarise(age.mean = weighted.mean(age, wt),
            age.sd = sqrt(sum(wt / sum(wt) * (age - age.mean)^2))
)
```

```
## # A tibble: 1 x 2
##   age.mean age.sd
##      <dbl>  <dbl>
## 1     50.3   3.12
```


```r
AC.AgD[, c("age.mean", "age.sd")]
```

```
##   age.mean   age.sd
## 1 50.27333 3.124821
```

The estimated relative effect $\hat{d}_{AB(AC)}$ of $B$ vs. $A$ in the $AC$ population is found by taking weighted means of the outcomes in the $AB$ trial. However, in practice it is easier to generate these estimates using a simple linear model: this is exactly equivalent to taking the weighted means, but allows us to use the `sandwich` package to calculate standard errors correctly using a sandwich estimator. (Note that it is possible to generate estimates of absolute outcomes on each treatment using the weighted means or the linear model, but these will be biased unless all prognostic variables and effect modifiers in imbalance between the populations are accounted for. Unbiased prediction of absolute outcomes relies on the much stronger assumption of conditional constancy of absolute effects.)


```r
# Binomial GLM
fit1 <-
AB.IPD %>% mutate(y0 = 1 - y, wt = wt) %>%
glm(cbind(y,y0) ~ trt, data = ., family = binomial, weights = wt)
# Sandwich estimator of variance matrix
V.sw <- vcovHC(fit1)
# The log OR of B vs. A is just the trtB parameter estimate,
# since effect modifiers were centred
print(d.AB.MAIC <- coef(fit1)["trtB"])
```

```
##      trtB 
## -3.385924
```


```r
print(var.d.AB.MAIC <- V.sw["trtB","trtB"])
```

```
## [1] 0.170214
```

Finally, we construct the indirect comparison estimate $\hat{d}_{BC(AC)}$ on the log OR scale, using the fact that $d_{BC(AC)}=d_{AC(AC)}-d_{AB(AC)}$.


```r
# Estimated log OR of C vs. A from the AC trial
d.AC <- with(AC.AgD, log(y.C.sum * (N.A - y.A.sum) / (y.A.sum * (N.C - y.C.sum))))
var.d.AC <- with(AC.AgD, 1/y.A.sum + 1/(N.A - y.A.sum) + 1/y.C.sum + 1/(N.C - y.C.sum))

# Indirect comparison
print(d.BC.MAIC <- d.AC - d.AB.MAIC)
```

```
##        trtB 
## -0.03880351
```


```r
print(var.d.BC.MAIC <- var.d.AC + var.d.AB.MAIC)
```

```
## [1] 0.273585
```

So the MAIC estimate of the log odds ratio of treatment $C$ vs. $B$ is ???0.039, with standard error $\sqrt{0.274}=0.523$. We examine this result in more detail later on in the summary section.
