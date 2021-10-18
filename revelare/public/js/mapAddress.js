frappe.ui.form.on('Address', {
  onload_post_render: function (frm) {
    let latitude = frm.doc.shs_latitude || 14.552619924048559;
    let longitude = frm.doc.shs_longitude || -90.45376770582736;
    let zoom = 10;

    // Crea una nueva instancia de mapa, con una ubicacion default
    var map = L.map('map').setView([latitude, longitude], zoom);

    // El proveedor de mapas es openstreetmap, si se require mas precision hay que pagar por API KEY
    // como Google Maps
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Se agregan los controles de busqueda y zoom al mapa
    var searchControl = L.esri.Geocoding.geosearch().addTo(map)

    // Los resultados se agregan como capa al mapa (frente)
    var results = L.layerGroup().addTo(map);


    // Cuando se carga por primera vez se renderiza el pin con las coords que existan
    // Complementado de http://bl.ocks.org/ramiroaznar/f399ffd29d1b4d48632604aebfc7b8cc
    var myMarker = L.marker([latitude, longitude], { title: "Punto", alt: "Punto", draggable: true })
      .addTo(map)
      .on('dragend', function () {
        var coord = String(myMarker.getLatLng()).split(',');
        var lat = coord[0].split('(')[1].replace(/\s+/g, '');  // Se elimina cualquier espacio en blanco
        // console.log(lat);
        var lng = coord[1].split(')')[0].replace(/\s+/g, '');
        // console.log(lng);
        myMarker.bindPopup("Punto Movido a: " + lat[1] + ", " + lng[0] + ".");

        // Se actualizan los valores de lat, lng
        frm.set_value({
          shs_latitude: lat,
          shs_longitude: lng
        })
        frm.refresh_field('shs_latitude');
        frm.refresh_field('shs_longitude');

        // Regenera permalink
        let permalink = `https://www.waze.com/livemap?zoom=14&lat=${frm.doc.shs_latitude}&lon=${frm.doc.shs_longitude}&pin=1`;
        frm.set_value({ waze_permalink: permalink })
        frm.refresh_field('waze_permalink');
      });


    // Cuando se realiza una busqueda de dirección, en el icono de lupa
    searchControl.on('results', function (data) {
      // console.log("Buscando...")
      results.clearLayers();  // Se limpia la capa para renderizar los nuevos resultados

      for (var i = data.results.length - 1; i >= 0; i--) {
        results.addLayer(L.marker(data.results[i].latlng, { title: "Punto", alt: "Punto", draggable: true }).addTo(map)
          .on('dragend', function () {
            map.removeLayer(myMarker) // LImpia el mapa para renderizar el nuevo pin

            var coord = String(myMarker.getLatLng()).split(',');
            var lat = coord[0].split('(')[1].replace(/\s+/g, '');
            // console.log(lat);
            var lng = coord[1].split(')')[0].replace(/\s+/g, '');
            // console.log(lng);

            frm.set_value({
              shs_latitude: lat,
              shs_longitude: lng
            })

            frm.refresh_field('shs_latitude');
            frm.refresh_field('shs_longitude');

            myMarker.bindPopup("Punto Movido a: " + lat[1] + ", " + lng[0] + ".");

            // Regeneracion permalink
            let permalink = `https://www.waze.com/livemap?zoom=14&lat=${frm.doc.shs_latitude}&lon=${frm.doc.shs_longitude}&pin=1`;
            frm.set_value({ waze_permalink: permalink })
            frm.refresh_field('waze_permalink');
          }))

        // console.log("Resultado", data.results[i].latlng)
        frm.set_value({
          shs_latitude: data.results[i].latlng.lat,
          shs_longitude: data.results[i].latlng.lng
        })
      }

      frm.refresh_field('shs_latitude');
      frm.refresh_field('shs_longitude');

      // Regeneracion permalink
      let permalink = `https://www.waze.com/livemap?zoom=14&lat=${frm.doc.shs_latitude}&lon=${frm.doc.shs_longitude}&pin=1`;
      frm.set_value({ waze_permalink: permalink })
      frm.refresh_field('waze_permalink');
    });
  },
});
