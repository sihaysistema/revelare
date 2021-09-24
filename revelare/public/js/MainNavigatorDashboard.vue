<template>
  <div class="shs-container-fluid">
    <!-- Botones header -->
    <div class="project-nav">
      <div class="card-action card-tabs mr-auto">
        <ul class="nav nav-tabs style-2">
          <li class="nav-item">
            <select class="custom-select custom-select-lg mt-1">
              <option selected>{{ __("Errand Trip") }}</option>
              <option value="1">One</option>
              <option value="2">Two</option>
              <option value="3">Three</option>
            </select>
          </li>

          <li class="nav-item mr-4">
            <select class="custom-select custom-select-lg mt-1">
              <option selected>{{ __("Driver") }}</option>
              <option value="1">Lewis Hamilton</option>
              <option value="2">Pablito</option>
              <option value="3">Paco</option>
            </select>
          </li>

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

    <!-- Render dinamico de cards -->
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
    // this.getData();
    // console.log(this.stops);
  },
  methods: {
    getData() {
      //   this.stops = dummy_data;
      let _this = this;

      frappe.call({
        method: "shs_dashboard.api.sales_order_qty",
        async: true,
        callback: function (data) {
          _this.stops = data.message;

          console.log(data.message);
        },
      });
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