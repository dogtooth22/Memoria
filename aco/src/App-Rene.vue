<template>
  <div id="app">
    <input type="file" ref="fileInput" accept=".txt" @change="onFilePicked"/>
    <div style="flex-direction: row;">
      <button @click="minusBus"><</button>
      <button @click="plusBus">></button>
      <button @click="playAnimation" v-if="!animationPlaying">&#9658;</button>
      <button @click="stopAnimation" v-else>&#xe034;</button>
    </div>

    <svg ref="svg">
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
      </defs>
    </svg>
    <!--<HelloWorld></HelloWorld>-->
  </div>
</template>

<script setup>
  //import HelloWorld from './components/HelloWorld.vue';
  import { onMounted, ref } from 'vue';
  import axios from 'axios';
  import * as d3 from 'd3';

  const svg = ref(null);
  const nodes = [], links = [];
  var link = null;
  var nodeVerticalDistances = 200, nodeHorizontalDistances = 600;
  var currentBus = 0;
  var firstDistances, secondDistances, finalRoutes = [];
  var addedPaths = [];
  var animationPlaying = false;

  const plusBus = () => {
    if (currentBus < finalRoutes.length - 1) {
      currentBus += 1;
      changeBus();
    }
  };

  const minusBus = () => {
    if (currentBus > 0) {
      currentBus -= 1;
      changeBus();
    }
  };

  const changeBus = () => {
    clearPath();
    //console.log(finalRoutes[currentBus]);
    for (var k = 0; k < finalRoutes[currentBus].length; k++) {
      if (k == 0) {
        for (var j = finalRoutes[currentBus][k][0]*secondDistances.length; j < secondDistances.length*(parseInt(finalRoutes[currentBus][0]) + 1); j++) {
          if (link["_groups"][0][j]["__data__"]["source"]["index"] != undefined) {
            var source = link["_groups"][0][j]["__data__"]["source"]["index"];
            var target = link["_groups"][0][j]["__data__"]["target"]["index"];
          } else {
            var source = link["_groups"][0][j]["__data__"]["source"];
            var target = link["_groups"][0][j]["__data__"]["target"];
          }
          if (finalRoutes[currentBus][k][0] == source && finalRoutes[currentBus][k][1] == (target - firstDistances.length)) {
            addedPaths.push(j);
            d3.select(link["_groups"][0][j]).attr("marker-end", "url(#arrowhead)")
            .attr('stroke', 'red').transition().duration('1000');
            break;
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
          if (finalRoutes[currentBus][k][0] == parseInt(source - firstDistances.length) && finalRoutes[currentBus][k][1] == parseInt(target - (firstDistances.length + secondDistances.length))) {
            d3.select(link["_groups"][0][j]).attr("marker-end", "url(#arrowhead)")
            .attr('stroke', 'red').transition().duration('1000');
            addedPaths.push(j);
            if ((k + 1) != finalRoutes[currentBus].length) {
              for (var m = secondDistances.length; m < link["_groups"][0].length; m++) {
                if (link["_groups"][0][j]["__data__"]["source"]["index"] != undefined) {
                  var source = link["_groups"][0][m]["__data__"]["source"]["index"];
                  var target = link["_groups"][0][m]["__data__"]["target"]["index"];
                } else {
                  var source = link["_groups"][0][m]["__data__"]["source"];
                  var target = link["_groups"][0][m]["__data__"]["target"];
                }
                if (finalRoutes[currentBus][k][1] == parseInt(target - (firstDistances.length + secondDistances.length)) && finalRoutes[currentBus][k + 1][0] == parseInt(source - firstDistances.length)){
                  d3.select(link["_groups"][0][m]).attr("marker-start", "url(#arrowhead)")
                  .attr('stroke', 'red').transition().duration('1000');
                  addedPaths.push(m);
                  break;
                }
              }
            } break;
          }
        }
      }
    }
    if (animationPlaying) {
      playAnimation();
    }
  };

  const clearPath = () => {
    d3.selectAll("line").attr("marker-end", "").attr("marker-start", "").attr('stroke', '#999').transition().duration('1000');
    addedPaths = [];
  }

  const playAnimation = () => {
    stopAnimation();
    animationPlaying = true;
    var pathAnimation = "";
    for (var i = 0; i < addedPaths.length; i++) {
      if (i == 0 || i % 2 == 1) {
        pathAnimation += "M " + d3.select(link["_groups"][0][addedPaths[i]]).attr("x1") + " " + d3.select(link["_groups"][0][addedPaths[i]]).attr("y1") + " L " + d3.select(link["_groups"][0][addedPaths[i]]).attr("x2") + " " + d3.select(link["_groups"][0][addedPaths[i]]).attr("y2") + " ";
      } if (i > 0 && i % 2 == 0) {
        pathAnimation += "M " + d3.select(link["_groups"][0][addedPaths[i]]).attr("x2") + " " + d3.select(link["_groups"][0][addedPaths[i]]).attr("y2") + " L " + d3.select(link["_groups"][0][addedPaths[i]]).attr("x1") + " " + d3.select(link["_groups"][0][addedPaths[i]]).attr("y1") + " ";
      }
    }
    const svgElement = d3.select(svg.value);
    const image = svgElement.append("image")
      .attr("href", "https://images.emojiterra.com/google/android-12l/512px/1f68c.png")
      .attr("width", 100)
      .attr("height", 100);

    image.append("animateMotion")
      .attr("path", pathAnimation)
      .attr("begin", "0s")
      .attr("dur", addedPaths.length + "s")
      .attr("repeatCount", "indefinite");
  }

  const stopAnimation = () => {
    const svgElement = d3.select(svg.value);
    svgElement.selectAll("image").remove();
  }

  const onFilePicked = (event) => {
    clearPath();
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
    };
    reader.readAsText(file);

    var formData = new FormData();
    var finalShelters = [];
    var finalTime = 0;
    formData.append('file', file);
    axios.post('http://127.0.0.1:5000', 
      formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        firstDistances = response.data[0];
        secondDistances = response.data[1];

        finalRoutes = response.data[2];
        finalShelters = response.data[3];
        finalTime = response.data[4];

        var middleFirstPoint = (firstDistances.length - 1) / 2;
        var middleSecondPoint = (secondDistances.length + 1) / 2;
        var middleThirdPoint = (secondDistances[0].length - 1) / 2;;

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
          nodes[i + firstDistances.length + secondDistances.length] = { id: i + firstDistances.length + secondDistances.length, name: 'Destino ' + (i + 1) };
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
      
        // Define arrow markers for graph links
        svgElement.select('defs').append('marker')
                  .attr('id', 'arrowhead')
                  .attr('viewBox', '-0 -5 10 10')
                  .attr('refX', 20) // Controls the distance between the node and the arrow
                  .attr('refY', 0)
                  .attr('orient', 'auto-start-reverse')
                  .attr('markerWidth', 7)
                  .attr('markerHeight', 7)
                  .attr('xoverflow', 'visible')
                  .append('svg:path')
                  .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
                  .attr('stroke', '#999');
      
        // Draw graph links
        var divLink = d3.select("svg").append("text")
          .attr("class", "tooltip")
          .attr("font", "10px sans-serif")
          .attr("fill", "black")
          .attr("filter", "url(#rounded-corners)")

        link = svgElement.append('g')
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

        var busNumber = d3.select("svg").append("text")
          .attr("class", "tooltip")
          .attr("font", "10px sans-serif")
          .attr("fill", "black")
          .attr("filter", "url(#rounded-corners)")
      
        // Draw graph nodes

        const nodeRadius = 15;
        const node = svgElement.append('g')
                              .attr('class', 'nodes')
                              .selectAll('circle')
                              .data(nodes)
                              .enter().append('circle')
                              .attr('r', nodeRadius)
                              .attr('fill', '#69b3a2')
                              .attr('stroke', '#000')
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
                                /*busNumber.html("Bus")
                                  .transition()
                                  .duration('50')
                                  .style("opacity", 1);*/
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
      }).catch(error => console.error(error));
  };

  onMounted(() => {
  });
</script>

<style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    text-align: center;
    color: #2c3e50;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-top: 50px;
    margin-bottom: 50px;
  }

  svg {
    display: block;
    margin: auto;
    border: 1px solid #ccc;
  }
</style>