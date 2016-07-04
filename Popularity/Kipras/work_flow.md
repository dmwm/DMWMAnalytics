Summer student (2016)

### Week 2

4 Jul 2016

- Idea for the next day to find out witch parameters are actually used in model script.
- Dropping parameters and running roll script. Result is identical, which means that dropped parameters originally might not be used in model.
- Rules to drop parameter:
- - Exploring parameters that are highly correlated (value > 0.6)
- - Taking a first pair of parameters with highest correlation. 
- - Sum of abs correlations for each of these parameters. Choosing parameter that is more correlated with the others.
- - Removing such parameters and recalculating all the correlations.
- - Repeating until there is no parameters correlated more then 0.6.
- - Dropped parameters: rel1_8, rel1_5, nfiles, rel3_0, parent, rel1_3
- Plotting correlation between parameters (plot with parameters that are correlated more than 0.6 is added). 
Considering old data, 5 weeks (2016.05.26-2016.06.29)
- Updating roll plot with 3 weeks data (plot added to week_2 folder)

### Week 1

1 Jun 2016

- Running roll script on fixed data. Results in week_1 folder. 
- Exploring differencies between old and new data.

30 Jun 2016

- Review of the project plan:

> **Project plan:**  
> **PART No 1**
> - Do separate parts of roll2 process:
>   - Merge dataframes
>   - Transform dataframes 
>   - Split data to training and validation parts
>   - Make a model on training data
>   - Use that model on validation data
>   - Get statistics of TPR, FPR, CPU time and RAM  
> - This should be done for both old and new data (date after the bug fix).
> - Rolling process means: Let's say starting from 3 weeks training data we predict the next week. For the next week we add another week to training data and we predict 5-th week using 4 weeks data.
> -  To get TPR and FPR statistics we compare our prediction with actual labels which we get from (naccess, nusers, totcpu .. or other metrics)
> - RF, SGD and XGB classifiers should be used for modelling. 
> - We should also try to combine multiple classifiers together to get better predictions.
> 
> **PART No 2**  
> - At the beginning  run a simple modeling algorithm on SPARK
> - Later move all model process to SPARK to decrees computing time

29 Jun 2016

- Analyzing roll2.sh script. Found that current profile (source /data/srv/current/apps/DCAFPilot/etc/profile.d/init.sh) has to be sourced before running the script.
- Getting to know git


28 Jun 2016

- Plotting histograms of every parameter of two weeks: 2015 11 19-2015 11 25 and 2016 06 16-2016 06 22.
- Looking for differences in distributions. Visible differences in most rel_.. parameters.
- Reading about bash scripting. 
- Trying terminal editors.

27 Jun 2016  

- Setting up VM

