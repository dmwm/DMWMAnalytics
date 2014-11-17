DMWMAnalytics
=============

Data-mining/process-mining analytics for the entire DM/WM stack

This is a place to gather code for analytics projects that go beyond simple
monitoring of components. In-depth or historic analyses of things like data
popularity, PhEDEx global transfers, T2<->T2 traffic, block latency etc.

We need to decide how to organise things under this repository. I suggest that
where the code clearly belongs to one of our projects we create a subdirectory
for that project and put the code in there. Also, create a subdirectory that
tells you what the code does. This gives us two levels of hierarchy to avoid
polluting the top-level namespace.

Specific suggestions:
* PhEDEx/Global-Transfer-Stats - for the plot of total volume of data ever transferred by PhEDEx
* Popularity/prototype - for the prediction-prototype we've discussed with IT division
