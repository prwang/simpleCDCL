# simpleCDCL
graded project for 'Logic and program verification' 

This code is essentially a loyal implementation of ```GRASP```(Joa˜o P. Marques-Silva et al) algorithm 
in python, without the *unique implication points* optimization.


## Key points in implementation

* several dicts(inside ```var_info, var_value```) are maintained for fast lookup for unit clauses 
* use of python generator(source: ```step.inflate_clause()```) when calculating *causes_of* (see the paper in page #5, formula (3))
* iterative(not recursive)(source: ```step() push() pop()```) approach of main DFS procedure
  * note: instead of exact undoing the side-effects(removing the entire clause when satisfied or removing the literal
   when unsatisfied, ```before_unmount() after_mounted()```) of assignments during ```pop()``` process, one must follow the reverse mapping ```rev```
    from variables to clauses in order to cover the newly-learned clause. see [1f4aaf1](/../../commit/1f4aaf1f1e7b416a58fa00e30a74058836147207)
* the ever-true clause where a variable exists in both positive and negative form just hurts the program, and must be got rid of, see also [#1](/../../issues/1)

## Benchmarks

open tests: python3.61/archlinux/HyperV/Core i7 6820HQ@2.8GHZ (time in seconds)

<table>
<tbody>
<tr>
<td align="left">BMC</td>
<td align="left">fl100</td>
<td align="left">fl30</td>
<td align="left">sw100</td>
<td align="left">uf100</td>
</tr>
<tr>
<td align="left" style='background-color:red !important'>&gt;30s</td>
<td align="left">1.41</td>
<td align="left">0.04</td>
<td align="left">0.29</td>
<td align="left">0.72</td>
</tr>
<tr>
<td align="left">bf26</td>
<td align="left">h6</td>
<td align="left">h7</td>
<td align="left">pret</td>
<td align="left">uf100</td>
</tr>
<tr>
<td align="left">1.47</td>
<td align="left">0.72</td>
<td align="left">8.73</td>
<td align="left">3.77</td>
<td align="left">1.75</td>
</tr></tbody></table>
