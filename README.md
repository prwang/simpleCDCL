# simpleCDCL
graded project for 'Logic and program verification' 

## spec
*   cdcl: 预判只搞一边，另外一边是在那个whiletrue里面发现出事了，
       由deduce直接推出来的
       
实现要点：
* ```formula.py```: cnf formula toolkit
    for dfs procedures: maintaining a stack for changes 
    induced by assigning values
  
* ```search.py```:   
