# simpleCDCL
graded project for 'Logic and program verification' 

## spec
实现要点：
   先搞dpll，再搞cdcl
   dpll: 搜索函数加两个优化（传播和纯变量）
```class formu```: represent a standard cnf boolean formula
  * [ ] choose_var() : choose a undecided variable
  * [ ] simplify() : BCP && pure
  
```resolve.py```: toolkit for resolving & PURE_simplification 
  * [ ] aux_data_structure
  * [ ] resolve()
