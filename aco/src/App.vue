<template>
  <div>
    <h1>Bus Evacuation Problem Route Visualization</h1>
    <div class="row flex-wrap">
      <div class="column">
        <p>Alpha</p>
        <input type="number" v-model="alpha" min="0" step="0.1"/>
      </div>
      <div class="column">
        <p>Beta</p>
        <input type="number" v-model="beta" min="0" step="0.1"/>
      </div>
      <div class="column">
        <p>q</p>
        <input type="number" v-model="q" min="0"/>
      </div>
      <div class="column">
        <p>Decay</p>
        <input type="number" v-model="decay" min="0" max="1" step="0.1"/>
      </div>
      <div class="column">
        <p>N of iterations</p>
        <input type="number" v-model="n_iterations" min="1" step="1"/>
      </div>
      <div class="column">
        <p>Algorithm</p>
        <select v-model="algorithm">
          <option value="ant_density">Ant Density</option>
          <option value="ant_quantity">Ant Quantity</option>
          <option value="ant_cycle">Ant Cycle</option>
        </select>
      </div>
    </div>
    <input type="file" ref="fileInput" accept=".txt" @change="onFilePicked"/>
    <template v-if="file != null && loading == false">
      <p>Execution Time: {{ executionTime }}s</p>
      <div class="row menu-buttons">
        <button @click="minusBus">&lt;</button>
        <button @click="plusBus">&gt;</button>
        <button @click="playAnimation" v-if="animationPlaying == false"><i class="fa fa-play"></i></button>
        <button @click="stopAnimation" v-else><i class="fa fa-pause"></i></button>
        <button @click="hidePaths" v-if="pathsHidden == false">Hide Paths</button>
        <button @click="showPaths" v-else>Show Paths</button>
      </div>
  
      <p>Bus {{ currentBus + 1 }}, distance {{ pathsDistances[currentBus] }}</p>

    </template>
    
    <div class="column" v-if="file != null && loading == true">
      <div class="loader"></div>
    </div>
    
    <template v-if="file == null && loading == false">
      <p>Upload a file</p>
    </template>
    <!--<HelloWorld></HelloWorld>-->

    <div class="column">
      <svg ref="svg" overflow="visible">
        <defs>
          <filter id="rounded-corners" x="-5%" width="110%" y="0%" height="100%">
            <feFlood flood-color="#FFAA55"/>
            <feGaussianBlur stdDeviation="2"/>
            <feComponentTransfer>
              <feFuncA type="table"tableValues="0 0 0 1"/>
            </feComponentTransfer>
            
            <feComponentTransfer>
              <feFuncA type="table"tableValues="0 1 1 1 1 1 1 1"/>
              </feComponentTransfer>
              <feComposite operator="over" in="SourceGraphic"/>
          </filter>
          
          <filter id="rounded-corners-2" primitiveUnits="objectBoundingBox">
            <feImage preserveAspectRatio="none" width="110%" height="110%" x="-5%" y="0%"  xlink:href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' x='0px' y='0px' viewBox='0 0 400 40' height='40' width='400'%3E%3Crect fill='green' x='0' y='0' rx='20' ry='10' width='400' height='40'/%3E%3C/svg%3E"/>
            <feComposite operator="over" in="SourceGraphic"/>
          </filter>

          <!-- Define arrow markers for graph links -->
          <!-- refX controls the distance between the node and the arrow -->
          <marker id="arrowhead" viewBox="-0 -5 10 10" refX="20" refY="0" orient="auto-start-reverse" markerWidth="7" markerHeight="7" xoverflow="visible">
            <path d="M 0,-5 L 10 ,0 L 0,5 Z" stroke="#000"></path>
          </marker>
        </defs>
        <g></g>
      </svg>
      <div class="column" style="width: 100%;" v-if="file != null && loading == false">
        <table class="main-table">
          <tr class="firstTableRow">
            <th><!--Bus--></th>
            <th v-for="path in maxPath">Trip {{ path }}</th>
            <th></th>
            <th>Total Distance</th>
          </tr>
          <tr v-for="(item, index) in finalRoutes.length">
            <td class="firstTableColumn">Bus {{ index + 1 }}</td>
            <td v-for="route in finalRoutes[index]">
              {{ route[0] + 1 }} -> {{ route[1] + 1 }}
            </td>
            <td v-for="i in maxPath - finalRoutes[index].length"></td>
            <td></td>
            <td>{{ pathsDistances[index] }}</td>
          </tr>
        </table>
        <table class="main-table">
          <tr class="firstTableRow">
            <th>Shelters</th>
            <th v-for="index in finalShelters.length">{{ index }}</th>
          </tr>
          <tr>
            <td class="firstTableColumn">Space Available</td>
            <td v-for="shelter in finalShelters">{{ shelter }}</td>
          </tr>
        </table>
        <img v-bind:src="sourceImage" alt="">
        <p style="width: 50%;">Ant Colony Optimization progress over time. All solutions are improved in order to have a shorter evacuation time. To improve solutions, you might try with different parameters, such as the number of iterations.</p>
      </div>
    </div>

    
  </div>
</template>

<script setup>
  //import HelloWorld from './components/HelloWorld.vue';
  import { onMounted, ref } from 'vue';
  import axios from 'axios';
  import * as d3 from 'd3';

  // Default parameters
  var alpha = 1, beta = 1, q = 4, decay = 0.9, n_iterations = 50, algorithm = "ant_density";

  const svg = ref(null);
  const nodes = [], links = [];
  var link = null;
  var nodeVerticalDistances = 200, nodeHorizontalDistances = 500;
  var firstDistances, secondDistances, finalRoutes, pathsDistances, finalShelters = [], executionTime = ref(0);
  var maxPath = 0;
  var addedPaths = [], excludedPaths = [];
  const currentBus = ref(0);
  const animationPlaying = ref(false);
  const file = ref(null);
  var loading = ref(false);
  var pathsHidden = ref(false);
  var sourceImage = ref('');

  const plusBus = () => {
    if (currentBus.value < finalRoutes.length - 1) {
      currentBus.value += 1;
      changeBus();
    }
  };

  const minusBus = () => {
    if (currentBus.value > 0) {
      currentBus.value -= 1;
      changeBus();
    }
  };

  const changeBus = () => {
    clearPath();
    for (var k = 0; k < finalRoutes[currentBus.value].length; k++) {
      if (k == 0) {
        for (var j = finalRoutes[currentBus.value][k][0]*secondDistances.length; j < secondDistances.length*(parseInt(finalRoutes[currentBus.value][0]) + 1); j++) {
          if (link["_groups"][0][j]["__data__"]["source"]["index"] != undefined) {
            var source = link["_groups"][0][j]["__data__"]["source"]["index"];
            var target = link["_groups"][0][j]["__data__"]["target"]["index"];
          } else {
            var source = link["_groups"][0][j]["__data__"]["source"];
            var target = link["_groups"][0][j]["__data__"]["target"];
          }
          if (finalRoutes[currentBus.value][k][0] == source && finalRoutes[currentBus.value][k][1] == (target - firstDistances.length)) {
            addedPaths.push(j);
            d3.select(link["_groups"][0][j]).attr("marker-end", "url(#arrowhead)")
            .attr('stroke', 'red').transition().duration('1000');
            break;
          } else {
            excludedPaths.push(j);
          }
        }
      } else {
        for (var j = secondDistances.length; j < link["_groups"][0].length; j++) {
          if (link["_groups"][0][j]["__data__"]["source"]["index"] != undefined) {
            var source = link["_groups"][0][j]["__data__"]["source"]["index"];
            var target = link["_groups"][0][j]["__data__"]["target"]["index"];
          } else {
            var source = link["_groups"][0][j]["__data__"]["source"];
            var target = link["_groups"][0][j]["__data__"]["target"];
          }
          if (finalRoutes[currentBus.value][k][0] == parseInt(source - firstDistances.length) && finalRoutes[currentBus.value][k][1] == parseInt(target - (firstDistances.length + secondDistances.length))) {
            d3.select(link["_groups"][0][j]).attr("marker-end", "url(#arrowhead)")
            .attr('stroke', 'red').transition().duration('1000');
            addedPaths.push(j);
            if ((k + 1) != finalRoutes[currentBus.value].length) {
              for (var m = secondDistances.length; m < link["_groups"][0].length; m++) {
                if (link["_groups"][0][j]["__data__"]["source"]["index"] != undefined) {
                  var source = link["_groups"][0][m]["__data__"]["source"]["index"];
                  var target = link["_groups"][0][m]["__data__"]["target"]["index"];
                } else {
                  var source = link["_groups"][0][m]["__data__"]["source"];
                  var target = link["_groups"][0][m]["__data__"]["target"];
                }
                if (finalRoutes[currentBus.value][k][1] == parseInt(target - (firstDistances.length + secondDistances.length)) && finalRoutes[currentBus.value][k + 1][0] == parseInt(source - firstDistances.length)){
                  d3.select(link["_groups"][0][m]).attr("marker-start", "url(#arrowhead)")
                  .attr('stroke', 'red').transition().duration('1000');
                  addedPaths.push(m);
                  break;
                } else {
                  excludedPaths.push(m);
                }
              }
            } else {
              //addedPaths.push(j); // Did an extra push
            }
            break;
          }
        }
      }
    }
    if (animationPlaying.value == true) {
      playAnimation();
    }
  };

  const clearPath = () => {
    d3.selectAll("line").attr("marker-end", "").attr("marker-start", "").attr('stroke', '#999').transition().duration('1000');
    addedPaths = [];
  }

  const clearNodes = () => {
    d3.selectAll("circle").remove();
  }

  const clearLinks = () => {
    d3.selectAll("line").remove();
  }

  const playAnimation = () => {
    stopAnimation();
    animationPlaying.value = true;
    var pathAnimation = "";
    for (var i = 0; i < addedPaths.length; i++) {
      var path = d3.select(link["_groups"][0][addedPaths[i]]);
      if (i == 0 || i % 2 == 1) {
        pathAnimation += "M " + path.attr("x1") + " " + (parseInt(path.attr("y1")) - 50).toString() + " L " + path.attr("x2") + " " + (parseInt(path.attr("y2")) - 50).toString() + " ";
      } if (i > 0 && i % 2 == 0) {
        pathAnimation += "M " + path.attr("x2") + " " + (parseInt(path.attr("y2")) - 50).toString() + " L " + path.attr("x1") + " " + (parseInt(path.attr("y1")) - 50).toString() + " ";
      }
    }

    const svgElement = d3.select(svg.value);
    const image = svgElement.append("image")
      .attr("href", "https://static-00.iconduck.com/assets.00/bus-emoji-2048x1005-1c9m00t4.png")
      .attr("width", 100)
      .attr("height", 100);

    image.append("animateMotion")
      .attr("path", pathAnimation)
      .attr("begin", "0s")
      .attr("dur", addedPaths.length + "s")
      .attr("repeatCount", "indefinite");
  }

  const stopAnimation = () => {
    animationPlaying.value = false;
    const svgElement = d3.select(svg.value);
    svgElement.selectAll("image").remove();
  }

  const hidePaths = () => {
    //console.log(addedPaths, excludedPaths);
    pathsHidden.value = !pathsHidden.value;
    for (var i = 0; i < link["_groups"][0].length; i++) {
      if (!addedPaths.includes(i)) {
        d3.select(link["_groups"][0][i]).attr('stroke', 'transparent').style('pointer-events', 'none');
      }
    }
  }

  const showPaths = () => {
    pathsHidden.value = !pathsHidden.value;
    for (var i = 0; i < link["_groups"][0].length; i++) {
      if (!addedPaths.includes(i)) {
        d3.select(link["_groups"][0][i]).attr('stroke', '#999').style('pointer-events', 'auto');
      }
    }
  }

  const onFilePicked = (event) => {
    loading.value = true;
    currentBus.value = 0;
    maxPath = 0;
    clearPath(); clearNodes(); clearLinks(); stopAnimation();
    file.value = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
    };
    reader.readAsText(file.value);

    var formData = new FormData();
    formData.append('file', file.value);
    formData.append('alpha', alpha);
    formData.append('beta', beta);
    formData.append('q', q);
    formData.append('decay', decay);
    formData.append('n_iterations', n_iterations);
    formData.append('algorithm', algorithm);

    axios.post('http://127.0.0.1:5000',
      formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        loading.value = false;
        firstDistances = response.data[0];
        secondDistances = response.data[1];

        finalRoutes = response.data[2];
        pathsDistances = response.data[3]
        finalShelters = response.data[4];
        executionTime = response.data[5];

        sourceImage = 'data:image/png;base64,' + response.data[6];

        for (var i = 0; i < finalRoutes.length; i++) {
          if (maxPath < finalRoutes[i].length) {
            maxPath = finalRoutes[i].length;
          }
        }

        const middleFirstPoint = (firstDistances.length - 1) / 2;
        const middleSecondPoint = (secondDistances.length + 1) / 2;
        const middleThirdPoint = (secondDistances[0].length - 1) / 2;

        for (var i = 0; i < firstDistances.length; i++) {
          nodes[i] = { id: i, name: 'Partida ' + (i + 1) };
          nodes[i].fx = 100;
          nodes[i].fy = nodeVerticalDistances*middleSecondPoint + nodeVerticalDistances*(i - middleFirstPoint);
          for (var j = 0; j < firstDistances[i].length; j++) {
            links[j + i*firstDistances[i].length] = { source: i, target: j + firstDistances.length, length: firstDistances[i][j] };
          }
        }

        for (var i = 0; i < secondDistances.length; i++) {
          nodes[i + firstDistances.length] = { id: i + firstDistances.length, name: 'Punto Encuentro ' + (i + 1) };
          nodes[i + firstDistances.length].fx = 100 + nodeHorizontalDistances;
          nodes[i + firstDistances.length].fy = nodeVerticalDistances*(i + 1);
        }

        for (var i = 0; i < secondDistances[0].length; i++) {
          nodes[i + firstDistances.length + secondDistances.length] = { id: i + firstDistances.length + secondDistances.length, name: 'Refugio ' + (i + 1) };
          nodes[i + firstDistances.length + secondDistances.length].fx = 100 + nodeHorizontalDistances*2;
          nodes[i + firstDistances.length + secondDistances.length].fy = nodeVerticalDistances*middleSecondPoint + nodeVerticalDistances*(i - middleThirdPoint);
          for (var j = 0; j < secondDistances.length; j++) {
            links[secondDistances.length*firstDistances.length + j + i*secondDistances.length] = { source: j + firstDistances.length, target: i + firstDistances.length + secondDistances.length, length: secondDistances[j][i]};
          }
        }

        var width = 200 + nodeHorizontalDistances*2, height = nodeVerticalDistances*(secondDistances.length + 1);
      
        const svgElement = d3.select(svg.value)
                            .attr('width', width)
                            .attr('height', height);
      
        // Draw graph links
        var divLink = d3.select("svg").append("text")
          .attr("class", "tooltip")
          .attr("font", "10px sans-serif")
          .attr("fill", "black")
          .attr("filter", "url(#rounded-corners)")

        link = svgElement.select('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('stroke-width', 2)
                .attr('stroke', '#999')
                .on('mouseover', function(d, i) {
                  const link = d3.select(this);
                  const x = (parseInt(link.attr('x1')) + parseInt(link.attr('x2'))) / 2;
                  const y = (parseInt(link.attr('y1')) + parseInt(link.attr('y2'))) / 2;
                  link.transition()
                  .duration("200")
                  .attr('stroke-width', 4);

                  divLink.transition()
                    .duration('50')
                    .style("opacity", 1);

                  let num = i['length']
                  divLink.html(num)
                    .attr("x", (parseFloat(x) + 15))
                    .attr("y", (parseFloat(y) + 15))
                }
                ).on('mouseout', function(d, i) {
                  d3.select(this).transition()
                  .duration("200")
                  .attr('stroke-width', 2);
                  divLink.transition()
                    .duration('50')
                    .style("opacity", 0);
                })
      
        var divNode = d3.select("svg").append("text")
          .attr("class", "tooltip")
          .attr("font", "10px sans-serif")
          .attr("fill", "red")
          .attr("filter", "url(#rounded-corners-2)")

        /*var busNumber = d3.select("svg").append("text")
          .attr("class", "tooltip")
          .attr("font", "10px sans-serif")
          .attr("fill", "black")
          .attr("filter", "url(#rounded-corners)")*/
      
        // Draw graph nodes
        const nodeRadius = 15;
        const node = svgElement.select('g')
                      .attr('class', 'nodes')
                      .selectAll('circle')
                      .data(nodes)
                      .enter().append('circle')
                      .attr('r', nodeRadius)
                      .attr('fill', '#69b3a2')
                      .attr('stroke-width', 3)
                      .on('mouseover', function(d, i) {
                        const node = d3.select(this);
                        const x = node.attr('cx');
                        const y = node.attr('cy');
                        node.transition()
                        .duration("200")
                        .attr('r', nodeRadius + 3);

                        divNode.transition()
                          .duration('50')
                          .style("opacity", 1);

                        let num = i['name']
                        divNode.html(num)
                          .attr("x", (parseFloat(x) + 15))
                          .attr("y", (parseFloat(y) + 15))
                      })
                      .on('mouseout', function(d, i) {
                        d3.select(this).transition()
                        .duration("200")
                        .attr('r', nodeRadius);

                        divNode.transition()
                          .duration('50')
                          .style("opacity", 0);
                      })
                      .on('click', function(d, i) {
                        if (i["index"] < firstDistances.length) {
                          //console.log("Partida:", i["index"]);
                        } else if (i["index"] >= firstDistances.length && i["index"] < firstDistances.length + secondDistances.length) {
                          //console.log("Hola");
                        } else {
                          //console.log("Espacio Disponible:", finalShelters[i["index"] - firstDistances.length - secondDistances.length]);
                        }
                      });
        changeBus();
        // Set up force simulation
        const simulation = d3.forceSimulation(nodes)
                            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                            .force('charge', d3.forceManyBody().strength(-400))
                            .force('center', d3.forceCenter(width / 2, height / 2));
      
        // Update positions each tick
        simulation.on('tick', () => {
          link.attr('x1', d => d.source.x)
              .attr('y1', d => d.source.y)
              .attr('x2', d => d.target.x)
              .attr('y2', d => d.target.y);
      
          node.attr('cx', d => d.x)
              .attr('cy', d => d.y);
        });
      }).catch(error => {
        loading.value = false;
        console.error(error);
    });
  };

  onMounted(() => {
  });
</script>
