LogStats
========

Command line application that plots accesses to data from logs.

Usage 
-----
<pre>
usage: run [-h] [-s SAVE] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -s SAVE, --save SAVE  Save plots in specified folder. If this options is not
                        specified, results are saved in 'results_folder' set
                        in config.py.
  -p, --plot            Plots custom graphs using native window system.
                        Plotting is off by default.
</pre>


<code>./run.py -p </code>
will save the plots in default results folder set in config.py and plot the
graphs using the native window system. 

Requirements
------------
<pre><code>pip install -r requirements.txt</pre></code>

matplotlib install using pip might fail, issue has been discussed
here: https://github.com/pypa/pip/issues/720
If that's the case, you will need to install matplotlib separately.
I found the easiest way to do that on OS X 10.8 is to install it through the 
Enthought Python Distribution.
