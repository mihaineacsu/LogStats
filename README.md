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

Requirements
------------
<pre><code>pip install -r requirements.txt</pre></code>

<pre>matplotlib</pre> install using pip might fail, issue has been discussed
here: https://github.com/pypa/pip/issues/720
If that's the case, you will need to install <pre>matplotlib</pre> separately.
I found the easiest way to do that on OS X 10.8 is to install it through the 
<pre>Enthought Python Distribution</pre>.

Log files
---------
One .tgz log archives for each machine should be placed in the 'log_folder' set
in config.py. The archives should be named accordingly to the 3 machines:
"prod-api1.tgz", "prod-api2.tgz", "ubvu-api1.tgz".
A second option would be placing log files in folders named after 3 machines.
