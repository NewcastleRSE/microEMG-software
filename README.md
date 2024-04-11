# microEMG-software
Software for recording and analysing microEMG recordings, developed for "Multi-channel jitter recordings in the diagnosis of myasthenia gravis and congenital myasthenic syndromes" project.

## About

In clinical practice, electromyography (EMG) is performed using a single-channel electrode to capture motor unit and muscle fibre potentials. These recordings are subsequently analysed to detect abnormalities in motor unit function. Clinicians must currently obtain multiple single-channel recordings which is time-consuming and requires expertise. Additionally, a single-channel recording does not provide information about muscle fibre locations or motor unit sizes.

To address these limitations, the microEMG team have developed:

1. A multichannel EMG (microEMG) electrode. Each electrode contains 32 or 64 channels, allowing clinicians to obtain a single, multivariate recording per muscle.
2. An analytical pipeline that identifies motor units and localises muscle fibres. 


The microEMG team’s primary goal is for their microEMG electrode technology and analysis pipeline to be obtained by an external company that will commercialise these techniques.
 
To meet this goal, the microEMG team requires RSE team assistance in the following: 

1.	Development of a real-time recording GUI for EMG recordings with multiple channels. 
2.	Development analysis scripts and GUI to allow clinicians to perform microEMG recording analyses within a reasonable runtime. 
3.	The microEMG team will conduct a small pilot study to collect microEMG data from patients with neuromuscular disorders. The current analytical pipeline needs to be extended to describe more features of the patients’ motor units, and the data from all patients will need to be analysed using the updated software.

See project documentation for a detailed description.

### Project Team

Dr Roger Whittaker, Newcastle University  ([roger.whittaker@newcastle.ac.uk](mailto:roger.whittaker@newcastle.ac.uk))  
Dr Stuart Maitland, Newcastle University  ([stu.maitland@newcastle.ac.uk](mailto:stu.maitland@newcastle.ac.uk))  

Dr Gabrielle Schroeder, Newcastle University ([gabrielle.schroeder@newcastle.ac.uk](mailto:gabrielle.schroeder@newcastle.ac.uk))  
Dr Richard Howey, Newcastle University ([richard.howey@newcastle.ac.uk](mailto:richard.howey@newcastle.ac.uk))

### RSE Contact
Gabrielle Schroeder
RSE Team  
Newcastle University  
([gabrielle.schroeder@newcastle.ac.uk](mailto:gabrielle.schroeder@newcastle.ac.uk))  

## Built With

This section is intended to list the frameworks and tools you're using to develop this software. Please link to the home page or documentation in each case.

[Framework 1](https://something.com)  
[Framework 2](https://something.com)  
[Framework 3](https://something.com)  

## Getting Started

### Prerequisites

Any tools or versions of languages needed to run code. For example, specific Python or Node versions. Minimum hardware requirements also go here.

### Installation

How to build or install the application.

### Running Locally

How to run the application on your local system.

### Running Tests

How to run tests on your local system.

## Deployment

### Local

Deploying to a production-style setup but on the local system. Examples of this would include `venv`, `anaconda`, `Docker` or `minikube`. 

### Production

Deploying to the production system. Examples of this would include cloud, HPC or virtual machine. 

## Usage

Any links to the production environment, video demos and screenshots.

## Roadmap

- [x] Initial Research  
- [ ] Minimum viable product <-- You are Here  
- [ ] Alpha Release  
- [ ] Feature-Complete Release  

## Contributing

### Main Branch
Protected and can only be pushed to via pull requests. It should be considered stable and a representation of production code.

### Dev Branch
Should be considered fragile; code should compile and run, but features may be prone to errors.

### Feature Branches
A branch per feature that is being worked on.

https://nvie.com/posts/a-successful-git-branching-model/

## License

## Citation

Please cite the associated papers for this work if you use this code:

```
@article{xxx2023paper,
  title={Title},
  author={Author},
  journal={arXiv},
  year={2023}
}
```


## Acknowledgements
This work was funded by a grant from the UK Research Councils, EPSRC grant ref. EP/L012345/1, “Example project title, please update”.
