<template>
  <div class="shs-container-fluid">
    <!-- Botones header -->
    <div class="project-nav">
      <div class="card-action card-tabs mr-auto">
        <ul class="nav nav-tabs style-2">
          <!-- Renderiza los Errand Trips -->
          <li class="nav-item">
            <select
              class="custom-select custom-select-lg mt-1"
              @change="selectedErrandTrip($event.target.value)"
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
          <!-- Renderiza los conductores -->
          <li class="nav-item mr-4">
            <select class="custom-select custom-select-lg mt-1">
              <option selected></option>
              <option value="1">Lewis Hamilton</option>
              <option value="2">Pablito</option>
              <option value="3">Paco</option>
            </select>
          </li>

          <!-- Botón para filtros todas las paradas -->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link active"
              data-toggle="tab"
              aria-expanded="false"
            >
              {{ __("Todos los viajes") }}
              <span class="badge badge-pill shadow-dark badge-dark">
                {{ this.stops.length }}</span
              >
            </a>
          </li>

          <!-- Botón para filtros todas las paradas activas -->
          <li class="nav-item">
            <a
              type="button"
              class="nav-link"
              data-toggle="tab"
              aria-expanded="false"
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
              class="nav-link"
              data-toggle="tab"
              aria-expanded="true"
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
              class="nav-link"
              data-toggle="tab"
              aria-expanded="true"
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
              class="nav-link"
              data-toggle="tab"
              aria-expanded="true"
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
import dummy_data from "./dummy_data.js";

export default {
  name: "MainNavigatorDashboard",
  components: {
    DataCard,
  },
  data() {
    return {
      errandTrips: [],
      stops: [],
      nowDateTime: frappe.datetime.now_datetime(),
      tripsToDo: [], // contendra todos los viajes no completado
      tripsCompleted: [], // contendra los viajes completados
    };
  },
  mounted() {
    // this.getData();
    this.getErrandTrips();
    // console.log(this.stops);
  },
  methods: {
    // Obtiene los errand trips activos
    getErrandTrips() {
      //   this.stops = dummy_data;
      let _this = this;

      frappe.call({
        method: "revelare.api.get_errand_trips",
        async: true,
        callback: function (data) {
          _this.errandTrips = data.message;

          console.log(data.message);
        },
      });
    },
    // Obtiene los errand trip stops de X errand trip
    selectedErrandTrip(event) {
      let _this = this;

      frappe.call({
        method: "revelare.api.get_errand_trip_stops",
        args: {
          name: event,
        },
        async: true,
        callback: function (data) {
          _this.stops = data.message;
        },
      });
    },
    autoUpdateData() {
      // Aqui se agregara un timer
    },
    updateData() {
      // Aqui se actualizara la data manualmente
    },
    // Emisor de evento
    tripCompleted(option) {
      console.log("Completo: ", option);
      this.selectedErrandTrip(option);
      this.$forceUpdate();
    },
  },
  computed: {
    numberOfActives() {
      let actives = this.stops.filter(
        (trip) => trip.status === "Active"
      ).length;
      return actives;
    },
    numberOfOverdues() {
      let overdue = this.stops.filter(
        (trip) => trip.status === "Overdue"
      ).length;
      return overdue;
    },
    numberOfPending() {
      let pending = this.stops.filter(
        (trip) => trip.status === "Pending"
      ).length;
      return pending;
    },
    numberOfCompleted() {
      let completed = this.stops.filter(
        (trip) => trip.status === "Completed"
      ).length;
      return completed;
    },
  },
};
</script>

<style scoped>
.custom-select {
  width: auto !important;
  border: none !important;
}

.project-nav {
  display: inline-block;
  vertical-align: middle;
}
</style>