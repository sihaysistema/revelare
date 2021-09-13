<template>
  <div class="shs-container-fluid">
    <div class="project-nav">
      <div class="card-action card-tabs mr-auto">
        <ul class="nav nav-tabs style-2">
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
    <pre>{{ nowDateTime }} </pre>
    <div class="row">
      <DataCard v-for="stop in stops" :key="stop.idx" :tripData="stop" />
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
      stops: [],
      nowDateTime: frappe.datetime.now_datetime(),
      tripsToDo: [], // contendra todos los viajes no completado
      tripsCompleted: [], // contendra los viajes completados
    };
  },
  mounted() {
    this.getData();
    console.log(this.stops);
  },
  methods: {
    getData() {
      this.stops = dummy_data;
    },
    autoUpdateData() {
      // Aqui se agregara un timer
    },
    updateData() {
      // Aqui se actualizara la data manualmente
    },
  },
  computed: {
    numberOfActives() {
      return this.stops.filter((trip) => trip.status === "active").length;
    },
    numberOfOverdues() {
      return this.stops.filter((trip) => trip.status === "overdue").length;
    },
    numberOfPending() {
      return this.stops.filter((trip) => trip.status === "pending").length;
    },
    numberOfCompleted() {
      return this.stops.filter((trip) => trip.status === "completed").length;
    },
  },
};
</script>

<style>
</style>