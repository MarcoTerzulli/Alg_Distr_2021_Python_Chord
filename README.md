# Python Chord - Distributed Algorithms 2021
**Python Chord** project's repository - **Marco Terzulli**'s exam project of the **2021 Distributed Algorithms** Course for the **Master Degree in Computer Science** at [**University of Modena and Reggio Emilia**](https://www.unimore.it/).

## Table of Contents
<ol>
	<li>
		<a href="#get-started">Get Started</a>
		<ul>
			<li><a href="#prerequisites">Prerequisites</a></li>
		</ul>
	</li>
	<li>
        <a href="#how-the-application-works">How the Application Works</a>
		<ul>
			<li>
                <a href="#additional-settings">Additional Settings</a>
                <ul>
                    <li><a href="#notes-about-the-debugging-menu">Notes About the Debugging Menu</a></li>
                </ul>
            </li>
		</ul>
    </li>
	<li><a href="#application-purpose-and-limitations">Application Purposes and Limitations</a></li>
	<li><a href="#software--used-for-developmento">Software Used for Development</a></li>
	<li><a href="#known-issues">Known Issues</a></li>
</ol>
 
 
## Get Started

The following instructions will allow you to have a working copy of the project on your local machine.

### Prerequisites

Software to install for the project to work, and how to install it.

```
* A Linux, Windows or MacOS machine
* Python 3.7+
```

No additional requirements and installation steps needed!

<p align="right">(<a href="#top">back to top</a>)</p>


## How the Application Works

To execute the Chord Application, run the ```main.py``` script.

A simple command line interface is going to appear, allowing the interaction with the main functions of the application:
* Node Creation
* Node Termination and Delete
* File Insert
* File Lookup
* File Delete
* Print of the Chord Network
* Print of the Status of a Given Node (Predecessor Node, Successor List, and Finger Table)

### Additional Settings

You can specify additional settings to tune the Application behaviour inside the ```settings.py``` file.

Currently supported settings:
* ```Debug Mode```: enables the print of the debug messages for the main operations. **Warning**: the nodes are going to print A LOT of debug messages due to their frequent periodic operations, making the use of the application difficult. This command should be combined with a higher node perdioc operation timeout.
* ```Debug Menu Enabled```: enabled the hidden debugging menu. This menu shows advanced options for understanding how the network is working
* ```Max Node Initalization Retries```: specifies the max number of initialization retries for a node. It's here to prevent a loop in case a the most of the TCP ports are full
* ```Node Periodic Operations Timeout```: specifies the nodes periodic operations timeout A higher timeout is suggested if you're going to create a lot of nodes for reducing the TCP traffic

#### Notes About the Debugging Menu

This menu is meant only for debugging purposes and for checking and understanding how the Chord network works.

**Warning**: the use of the debugging commands could make the application stop working properly. Use these commands at your own risk!

<p align="right">(<a href="#top">back to top</a>)</p>


## Application Purposes and Limitations

The Application was realized only for a didactic use, and it's not intended to be used as a library nor as a complete 
Chord implementation and use case.

The Application uses Threads for managing the concurrent execution of the different Nodes that compose the Chord network.
A multi-processing implementation would have been better and more correct; however, given the purpose of the Application,
I chose a simpler and straight forward approach.

<p align="right">(<a href="#top">back to top</a>)</p>



## Software Used for Development
* [JetBrains Pycharm](https://www.jetbrains.com/pycharm/) - IDE used for development and testing

<p align="right">(<a href="#top">back to top</a>)</p>


## Known Issues
* The termination of a node should free its TCP port. However, this doesn't always happen immediately. This doesn't compromise in any way the application functionalities since other ports are going to be chosen for the new nodes (until all the systems ports are taken, of course).

<p align="right">(<a href="#top">back to top</a>)</p>
