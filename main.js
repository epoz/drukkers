mapLink = '<a href="http://www.esri.com/">Esri</a>';
wholink =
  "i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community";
sats = L.tileLayer(
  "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution: "&copy; " + mapLink + ", " + wholink,
    maxZoom: 19,
  }
);
debroen = L.tileLayer(
  "https://images.huygens.knaw.nl/webmapper/maps/debroen/{z}/{x}/{y}.png",
  {
    maxZoom: 19,
    tileSize: 256,
  }
);

var baseMaps = {
  "De Broen": debroen,
  Satellite: sats,
};

var mymap = L.map("mapid", { layers: [debroen, sats], tap: false }).setView(
  [52.368223, 4.893425],
  14
);
L.control.layers(baseMaps).addTo(mymap);

document.getElementById("slider_begin").addEventListener("input", (event) => {
  var slider_end = document.getElementById("slider_end");
  var span_begin = document.getElementById("span_begin");
  var span_end = document.getElementById("span_end");
  if (event.target.value >= slider_end.value) {
    slider_end.value = event.target.value;
    span_end.innerHTML = "End " + event.target.value;
  }
  span_begin.innerHTML = "Begin " + event.target.value;
});

document.getElementById("slider_end").addEventListener("input", (event) => {
  var slider_begin = document.getElementById("slider_begin");
  var span_begin = document.getElementById("span_begin");
  var span_end = document.getElementById("span_end");
  if (event.target.value <= slider_begin.value) {
    slider_begin.value = event.target.value;
    span_begin.innerHTML = "Begin " + event.target.value;
  }
  span_end.innerHTML = "End " + event.target.value;
});

var sliders = document.getElementsByClassName("dateslider");
for (var i = 0; i < sliders.length; i++) {
  sliders[i].addEventListener("change", (event) => {
    updateMarkers();
  });
}

function formatAddr(obj) {
  var buf = [];
  obj.ADRESSEN[0]
    .split("\n")
    .map((addr_fragment) =>
      buf.push(`<p style="margin: 0">${addr_fragment}</p>`)
    );
  return buf.join("\n");
}

var markers = {};
Object.values(DATA).forEach((obj) => {
  obj.map((addr) => {
    if (addr.LATLON[0])
      markers[addr.ROW[0]] = L.marker(addr.LATLON[0])
        .addTo(mymap)
        .bindPopup(
          `<h1>${addr.NAAM[0]}</h1><p>${addr.BEGIN[0]} - ${
            addr.END[0]
          }</p> ${formatAddr(addr)}`
        );
  });
});

function updateMarkers() {
  var slider_begin = document.getElementById("slider_begin");
  var date_begin = parseInt(slider_begin.value);

  var slider_end = document.getElementById("slider_end");
  var date_end = parseInt(slider_end.value);

  Object.values(markers).map((mrkr) => {
    mrkr.remove();
  });

  Object.values(DATA).forEach((obj) => {
    obj.map((addr) => {
      try {
        if (
          addr.BEGIN[0] >= date_begin &&
          addr.END[0] <= date_end &&
          addr.LATLON[0]
        ) {
          markers[addr.ROW[0]].addTo(mymap);
        }
      } catch (error) {
        console.log(error, addr);
      }
    });
  });
}
updateMarkers();