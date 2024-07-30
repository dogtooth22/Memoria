# Original Project

This is the original project that was developed before the Flask and Vue projects. It's developed in Python along numpy and matplotlib as the primary libraries, both very common in data science projects.

## Compilation

A makefile was created to compile this project's files, having the same parameters as the Vue project.

### Parameters

* i: number of iterations.
* alpha: constant that sets the importance on pheromones in the algorithm.
* beta: constant that sets the importance on distances in the algorithm.
* q: number of pheromones released by each ant.
* decay: the rate at which pheromones decay over time.
* instance: an instance's parameters (number of buses, starting points, meeting points and shelters).
* v: an instance's version.

### Example

```sh
make i=1000 alpha=1 beta=1 q=5 decay=0.9 instance=8-40-20-20 v=7
```