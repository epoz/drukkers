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

mapz = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png?{foo}", {
  foo: "bar",
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
});

debroen = L.tileLayer(
  "https://images.huygens.knaw.nl/webmapper/maps/debroen/{z}/{x}/{y}.png",
  {
    maxZoom: 19,
    tileSize: 256,
  }
);

var baseMaps = {
  "De Broen": debroen,
  Sats: sats,
  Map: mapz,
};

var mymap = L.map("mapid", {
  layers: [debroen, sats, mapz],
  tap: false,
}).setView([52.368223, 4.893425], 14);
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

function copyToClipboard(data) {
  const el = document.createElement("textarea");
  el.value = data;
  el.setAttribute("readonly", "");
  el.style.position = "absolute";
  el.style.left = "-9999px";
  document.body.appendChild(el);
  const selected =
    document.getSelection().rangeCount > 0
      ? document.getSelection().getRangeAt(0)
      : false;
  el.select();
  document.execCommand("copy");
  document.body.removeChild(el);
  if (selected) {
    document.getSelection().removeAllRanges();
    document.getSelection().addRange(selected);
  }
}

var printer_names = document.getElementById("printer_names");
var input_filter = document.getElementById("input_filter");
input_filter.addEventListener("change", (event) => {
  printer_names.innerHTML = "";
  Object.values(DATA).forEach((obj) => {
    let naam = obj[0].NAAM[0];
    let ppn = obj[0].RECORD[0];
    if (
      !event.target.value ||
      naam.match(new RegExp(event.target.value, "i"))
    ) {
      printer_names.insertAdjacentHTML(
        "beforeend",
        `<p onclick='copyToClipboard("${ppn} ${naam}")' data-ppn='${ppn}' style='margin: 0; cursor: pointer'>${naam}</p>`
      );
    }
  });

  updateMarkers();
});

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
      markers[addr.ROW[0]] = L.marker(addr.LATLON[0]).bindPopup(
        `<h1>${addr.NAAM[0]}</h1><p>${addr.BEGIN[0]} - ${
          addr.END[0]
        }</p> ${formatAddr(addr)}`
      );
  });
});

var markersGroup = L.markerClusterGroup();
mymap.addLayer(markersGroup);
function updateMarkers() {
  var slider_begin = document.getElementById("slider_begin");
  var date_begin = parseInt(slider_begin.value);

  var slider_end = document.getElementById("slider_end");
  var date_end = parseInt(slider_end.value);

  markersGroup.clearLayers();

  Object.values(DATA).forEach((obj) => {
    obj.map((addr) => {
      try {
        let matched_name;
        if (
          input_filter.value &&
          addr.NAAM[0].match(new RegExp(input_filter.value, "i"))
        ) {
          matched_name = true;
        } else {
          matched_name = false;
        }
        if (!input_filter.value) {
          matched_name = true;
        }
        if (
          addr.BEGIN[0] >= date_begin &&
          addr.END[0] <= date_end &&
          addr.LATLON[0] &&
          matched_name
        ) {
          markersGroup.addLayer(markers[addr.ROW[0]]);
        }
      } catch (error) {
        console.log(error, addr);
      }
    });
  });
}
updateMarkers();
