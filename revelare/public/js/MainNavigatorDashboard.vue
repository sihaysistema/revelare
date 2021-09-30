<template>
  <div class="shs-container-fluid">
    <!-- Botones header -->
    <div class="project-nav">
      <div class="card-action card-tabs mr-auto">
        <ul class="nav nav-tabs style-2">
          <!-- Renderiza los nombres de Errand Trips Activos-->
          <li class="nav-item">
            <select
              class="custom-select mt-2"
              @change="selectedErrandTrip($event.target.value)"
              v-model="errandTripSel"
            >
              <option selected></option>
              <option
                v-for="errandTrip in errandTrips"
                :key="errandTrip.name"
                :value="errandTrip.name"
              >
                {{ errandTrip.name }}
              </option>
            </select>
          </li>

          <!-- Renderiza el nombre de X conductor -->
          <li class="nav-item mr-1">
            <a
              class="nav-link disabled"
              data-toggle="tab"
              aria-expanded="false"
              disabled
              >{{ driver }}</a
            >
          </li>

          <!-- Botón para mostrar todas las paradas -->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link active"
              data-toggle="tab"
              aria-expanded="false"
              @class="allTrips()"
            >
              {{ __("Todos de viajes") }}
              <span class="badge badge-pill shadow-dark badge-dark">
                {{ this.stops.length }}</span
              >
            </a>
          </li>

          <!-- NOTA: Los botones se mantienen desactivados -->
          <!-- Botón para filtros todas las paradas activas -->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link disabled"
              data-toggle="tab"
              aria-expanded="false"
              disabled
            >
              {{ __("Activos") }}
              <span class="badge badge-pill badge-success shadow-success">{{
                numberOfActives
              }}</span>
            </a>
          </li>

          <!-- Botón para filtros todas las paradas pendientes cerca de llegar a la fecha estimada-->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link disabled"
              data-toggle="tab"
              aria-expanded="true"
              disabled
            >
              {{ __("Pendientes") }}
              <span class="badge badge-pill badge-warning shadow-warning">{{
                numberOfPending
              }}</span>
            </a>
          </li>

          <!-- Botón para filtros todas las paradas atrasados -->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link disabled"
              data-toggle="tab"
              aria-expanded="true"
              disabled
            >
              {{ __("Atrasados") }}
              <span class="badge badge-pill badge-danger shadow-danger">{{
                numberOfOverdues
              }}</span>
            </a>
          </li>

          <!-- Botón para filtros todas las paradas completadas -->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link disabled"
              data-toggle="tab"
              aria-expanded="true"
              disabled
              >{{ __("Completados") }}
              <span class="badge badge-pill badge-secondary shadow-secondary">{{
                numberOfCompleted
              }}</span></a
            >
          </li>
        </ul>
      </div>
    </div>

    <!-- Render dinamico de cards -->
    <div class="row">
      <DataCard
        v-for="stop in stops"
        :key="stop.idx"
        :tripData="stop"
        @dataTripCompleted="tripCompleted($event)"
      />
    </div>
  </div>
</template>

<script>
import DataCard from "./components/DataCard.vue";

export default {
  name: "MainNavigatorDashboard",
  components: {
    DataCard,
  },
  data() {
    return {
      errandTripSel: "", // Guarda cada errand trip seleccionado
      errandTrips: [], // Guarda datos para opciones de select
      stops: [], // Guarda datos para generar las paradas de cada ErrandTrip
      nowDateTime: frappe.datetime.now_datetime(),
      driver: "",
    };
  },
  mounted() {
    // Obtiene datos
    this.getErrandTrips();
    // console.log("se monto");
  },
  updated() {
    // console.log("se atualizo");
    // reactivamos las propiedades computadas para regenerar el conteo
  },
  methods: {
    // Obtiene los errand trips activos
    getErrandTrips() {
      let _this = this;

      frappe.call({
        method: "revelare.api.get_errand_trips",
        async: true,
        callback: function (data) {
          _this.errandTrips = data.message;

          //   console.log(data.message);
        },
      });
    },
    // Obtiene los errand trip stops de X errand trip
    selectedErrandTrip(event) {
      // Obtiene el nombre del conductor que se asigno al errand trip
      this.driver =
        this.errandTrips.filter((errandT) => errandT.name === event)[0]
          .driver_name || "";

      //   console.log(this.driver);

      let _this = this;

      frappe.call({
        method: "revelare.api.get_errand_trip_stops",
        args: {
          name: event,
        },
        callback: function (data) {
          _this.stops = data.message;
        },
      });
    },
    // NOTA: por ahora no es necesario autoupdate, el conductor es el que
    // actualiza los estados segun vaya completando viajes
    autoUpdateData() {
      // Aqui se agregara un timer
    },
    updateData() {
      // Aqui se actualizara la data manualmente
    },
    // Emisor de evento: detecta los cambios de componente hijo cuando se completa un viaje
    tripCompleted(option) {
      //   console.log("Completo: ", option);
      this.selectedErrandTrip(option);
      this.$forceUpdate();
    },
    // Se ejecuta cuando se presiona el boton allTrips y recarga todos los datos del backend
    allTrips() {
      this.selectedErrandTrip(this.errandTripSel);
      this.$forceUpdate();
    },
  },
  // Propiedades computadas para generar clases css, datos dinamicas
  computed: {
    numberOfActives() {
      return this.stops.filter((trip) => trip.status === "Active").length;
    },
    numberOfOverdues() {
      return this.stops.filter((trip) => trip.status === "Overdue").length;
    },
    numberOfPending() {
      return this.stops.filter((trip) => trip.status === "Pending").length;
    },
    numberOfCompleted() {
      return this.stops.filter((trip) => trip.status === "Completed").length;
    },
  },
};
</script>

<style scoped>
.custom-select {
  width: auto !important;
  border: none !important;
  font-size: 12pt !important;
}
.custom-select option {
  font-size: 12pt !important;
}

.project-nav {
  display: inline-block;
  vertical-align: middle;
}
</style>