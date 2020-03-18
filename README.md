# Process-Simulations
Simulation models of different processes created with help of SimPy

## List of Models
- [Library](#Library%20Simulation%20Model) <sup>[file](library.py)</sup>

## Library Simulation Model

[Python file](library.py)

The library simulation model is a year long simulation of a student library. The library has 2 counters for checking in and out books. Students come looking for a particular book and borrow it. Sometimes, students tend to be late in returning the books. There are limited books in the library and limited copies of each book. If a student can't find a particular book, they will return back later for the same or a different book. Very rarely, students will lose the books they borrowed. Occasionaly, new books are added to the library.

All parameters are described in the [python file](library.py) docstring. You can change any parameter very easily when running the simulation. Logging capability is provided (disabled by default). The final result is a graph of various attributes being compared over the time period. You can use the model to predict other parameters as well.

## Libraries used
[SimPy](https://simpy.readthedocs.io/) is a process-based discrete-event simulation framework based on standard Python. It is made available under the [MIT License](https://simpy.readthedocs.io/en/latest/about/license.html) by Team SimPy.

This repository uses SimPy to help simulate models and handle concurrent processes. You can learn more about SimPy with [this tutorial](https://simpy.readthedocs.io/en/latest/simpy_intro/index.html).

## License
This project and all included source code is made available under [MIT License](LICENSE) unless stated otherwise. A copy of the license is included below:-

MIT License

Copyright (c) 2020 Yashovardhan Dhanania 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.