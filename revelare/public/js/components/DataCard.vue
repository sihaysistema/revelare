<template>
  <div class="col-xl-6 mt-4 mb-4">
    <div :class="cardStyle">
      <!-- HEADER -->
      <div class="card-header mt-2">
        <div class="d-flex align-items-start">
          <div class="mr-auto">
            <a class="text-primary mb-1" @click="errandTrip()">
              {{ __("VIAJE") }} #{{ tripData.idx + 1 }}
            </a>
            <h5 class="title font-w600 mb-2">
              <a class="text-black"></a>
              {{ tripData.document }}
            </h5>
            <h5 class="title font-w600 mb-2">
              <a class="text-black"></a>
              {{ tripData.document_type }}
            </h5>
            <span class="font-weight-bolder">
              {{ __("Para") }}: {{ tripData.customer }}</span
            >
          </div>
          <h3 :class="badgeStyle">
            {{ __(statusCard) }}
          </h3>
        </div>
      </div>

      <!-- BODY -->
      <div class="card-body">
        <div class="row mb-3">
          <!-- Icono Izquierdo: Hora solicitada-->
          <div class="col-sm-6 mb-sm-0 mb-3 d-flex">
            <div class="dt-icon mr-3 bgl-danger">
              <svg
                width="19"
                height="24"
                viewBox="0 0 19 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M18.6601 8.6858C18.5437 8.44064 18.2965 8.28427 18.025 8.28427H10.9728L15.2413 1.06083C15.3697 0.843469 15.3718 0.573844 15.2466 0.354609C15.1214 0.135375 14.8884 -9.37014e-05 14.6359 4.86277e-08L8.61084 0.000656299C8.3608 0.000750049 8.12957 0.1335 8.00362 0.349453L0.0958048 13.905C-0.0310859 14.1224 -0.0319764 14.3911 0.0934142 14.6094C0.218805 14.8277 0.451352 14.9624 0.703117 14.9624H7.71037L5.66943 23.1263C5.58955 23.4457 5.74213 23.7779 6.03651 23.9255C6.13691 23.9757 6.24459 24 6.35123 24C6.55729 24 6.75923 23.9094 6.89638 23.7413L18.5699 9.43186C18.7415 9.22148 18.7766 8.93105 18.6601 8.6858V8.6858Z"
                  fill="#FF4C41"
                />
              </svg>
            </div>
            <div>
              <span class="font-weight-bolder"
                >{{ __("Hora solicitada") }}:</span
              >
              <p class="mb-0 pt-1 font-w500 text-black">
                {{ tripData.requested_time }}
              </p>
            </div>
          </div>

          <!-- Icono derecho: Hora completado -->
          <div class="col-sm-6 d-flex">
            <div class="dt-icon mr-3 bgl-info">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M19 5H18V3C18 2.73478 17.8946 2.48043 17.7071 2.29289C17.5196 2.10536 17.2652 2 17 2C16.7348 2 16.4804 2.10536 16.2929 2.29289C16.1054 2.48043 16 2.73478 16 3V5H8V3C8 2.73478 7.89464 2.48043 7.70711 2.29289C7.51957 2.10536 7.26522 2 7 2C6.73478 2 6.48043 2.10536 6.29289 2.29289C6.10536 2.48043 6 2.73478 6 3V5H5C4.20435 5 3.44129 5.31607 2.87868 5.87868C2.31607 6.44129 2 7.20435 2 8V9H22V8C22 7.20435 21.6839 6.44129 21.1213 5.87868C20.5587 5.31607 19.7957 5 19 5Z"
                  fill="#92caff"
                />
                <path
                  d="M2 19C2 19.7956 2.31607 20.5587 2.87868 21.1213C3.44129 21.6839 4.20435 22 5 22H19C19.7957 22 20.5587 21.6839 21.1213 21.1213C21.6839 20.5587 22 19.7956 22 19V11H2V19Z"
                  fill="#51A6F5"
                />
              </svg>
            </div>
            <div>
              <span class="font-weight-bolder"
                >{{ __("Hora completado") }}:
              </span>
              <p class="mb-0 pt-1 font-w500 text-black">
                {{ tripData.actual_arrival }}
              </p>
            </div>
          </div>
        </div>

        <!-- DESCRIPCIONES PARA EL VIAJE -->
        <p class="mb-2">
          <span class="font-weight-bolder">{{ __("Detalles") }} :</span> <br />
          {{ tripData.details }}
        </p>

        <div class="mr-auto">
          <p class="mb-2 text-black font-weight-bolder">
            {{ __("Detalles de cliente") }}
          </p>

          <p class="mb-2 text-black">
            <i class="fa fa-user" aria-hidden="true"></i> {{ __("Contacto") }}:
            <br />
            {{ tripData.contact_details }}
          </p>

          <p class="mb-2 text-black">
            <i class="fa fa-map-marker" aria-hidden="true"></i>
            {{ __("Dirección") }}: <br />{{ tripData.address_details }}
          </p>

          <!-- Ingreso comentarios por conductor -->
          <div class="md-form form-group">
            <label for="example8" class="font-weight-bolder"
              >{{ __("Driver comment") }}:
            </label>
            <input
              type="text"
              class="form-control"
              id="example8"
              placeholder="Ingrese su comentario"
              v-model="tripData.driver_comment"
              @change="updateComment()"
            />
          </div>
        </div>
      </div>

      <!-- FOOTER -->
      <div
        class="card-footer d-sm-flex justify-content-center align-items-center"
      >
        <!-- <div class="card-footer-link mb-4 mb-sm-0">
          {{ __("Tiempo retraso ") }}: 00:23:54
          <p class="card-text text-dark d-inline"></p>
        </div> -->

        <!-- Boton abrir en google maps -->
        <div class="text-center mr-2">
          <button
            type="button"
            title="Abrir en google maps"
            class="btn"
            @click="openInGoogleMaps"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 48 48"
              width="30px"
              height="30px"
            >
              <path
                fill="#1c9957"
                d="M42,39V9c0-1.657-1.343-3-3-3H9C7.343,6,6,7.343,6,9v30c0,1.657,1.343,3,3,3h30C40.657,42,42,40.657,42,39z"
              />
              <path
                fill="#3e7bf1"
                d="M9,42h30c1.657,0-15-16-15-16S7.343,42,9,42z"
              />
              <path
                fill="#cbccc9"
                d="M42,39V9c0-1.657-16,15-16,15S42,40.657,42,39z"
              />
              <path
                fill="#efefef"
                d="M39,42c1.657,0,3-1.343,3-3v-0.245L26.245,23L23,26.245L38.755,42H39z"
              />
              <path
                fill="#ffd73d"
                d="M42,9c0-1.657-1.343-3-3-3h-0.245L6,38.755V39c0,1.657,1.343,3,3,3h0.245L42,9.245V9z"
              />
              <path
                fill="#d73f35"
                d="M36,2c-5.523,0-10,4.477-10,10c0,6.813,7.666,9.295,9.333,19.851C35.44,32.531,35.448,33,36,33s0.56-0.469,0.667-1.149C38.334,21.295,46,18.813,46,12C46,6.477,41.523,2,36,2z"
              />
              <path
                fill="#752622"
                d="M36 8.5A3.5 3.5 0 1 0 36 15.5A3.5 3.5 0 1 0 36 8.5Z"
              />
              <path
                fill="#fff"
                d="M14.493,12.531v2.101h2.994c-0.392,1.274-1.455,2.185-2.994,2.185c-1.833,0-3.318-1.485-3.318-3.318s1.486-3.318,3.318-3.318c0.824,0,1.576,0.302,2.156,0.799l1.548-1.547C17.22,8.543,15.92,8,14.493,8c-3.038,0-5.501,2.463-5.501,5.5s2.463,5.5,5.501,5.5c4.81,0,5.637-4.317,5.184-6.461L14.493,12.531z"
              />
            </svg>
          </button>
        </div>

        <!-- Boton completar -->
        <div class="text-center" v-if="!tripData.actual_arrival">
          <button
            type="button"
            class="btn shs-btn-success btn-lg"
            @click="complete()"
          >
            {{ __("Complete") }}
          </button>
        </div>
        <!-- Boton deshacer -->
        <div
          class="text-center"
          v-if="tripData.actual_arrival && tripData.status === 'Completed'"
        >
          <button
            type="button"
            class="btn shs-btn-success btn-lg"
            @click="undo()"
          >
            {{ __("Undo") }}
          </button>
        </div>

        <!-- Boton abrir en waze -->
        <div class="text-center ml-2">
          <button
            type="button"
            title="Abrir en waze"
            class="btn"
            @click="openInWaze"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 48 48"
              width="30px"
              height="30px"
            >
              <path
                fill="#37474f"
                d="M27,38C9.1,38,5.2,33.2,3.6,31.1c-0.4-0.4-0.6-1-0.6-1.6C3,28.1,4.1,27,5.5,27C6.4,27,9,27,9,22.1 v-0.6C9,12.4,17.1,5,27,5s18,7.4,18,16.5S36.9,38,27,38z"
              />
              <path
                fill="#eceff1"
                d="M27,36c8.8,0,16-6.5,16-14.5S35.8,7,27,7s-16,6.5-16,14.5v0.6c0,6.2-3.8,6.9-5.5,6.9 C5.2,29,5,29.2,5,29.5c0,0.1,0,0.2,0.1,0.3C6.6,31.7,10,36,27,36z"
              />
              <path
                fill="#37474f"
                d="M32 16A2 2 0 1 0 32 20 2 2 0 1 0 32 16zM22 16A2 2 0 1 0 22 20 2 2 0 1 0 22 16zM27 29c-4.8 0-6.7-3.5-7-5.3-.1-.5.3-1.1.8-1.2.5-.1 1.1.3 1.2.8 0 .1.7 3.7 5 3.7 4.3 0 5-3.5 5-3.7.1-.5.6-.9 1.2-.8.5.1.9.6.8 1.1C33.7 25.5 31.8 29 27 29zM16.5 34A4.5 4.5 0 1 0 16.5 43 4.5 4.5 0 1 0 16.5 34z"
              />
              <path
                fill="#607d8b"
                d="M16.5 37A1.5 1.5 0 1 0 16.5 40A1.5 1.5 0 1 0 16.5 37Z"
              />
              <path
                fill="#37474f"
                d="M32.5 34A4.5 4.5 0 1 0 32.5 43A4.5 4.5 0 1 0 32.5 34Z"
              />
              <path
                fill="#607d8b"
                d="M32.5 37A1.5 1.5 0 1 0 32.5 40A1.5 1.5 0 1 0 32.5 37Z"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DataCard",
  props: ["tripData"],
  data() {
    return {
      completedOn: "",
      statusCard: "",
      driverComment: "",
    };
  },
  methods: {
    openInWaze() {
      // Para abrir en movil
      let url = `https://waze.com/ul?q=${this.tripData.lat},${this.tripData.lng}&navigate=yes&zoom=17`;
      if (this.detectMob()) {
        window.open(url).focus();
      } else {
        url = `https://www.waze.com/ul?ll=${this.tripData.lat}%2C${this.tripData.lng}&navigate=yes&zoom=17`;
        window.open(url, "_blank").focus();
      }
    },
    openInGoogleMaps() {
      //   let url = `maps://www.google.com/maps/dir/?api=1&travelmode=driving&layer=traffic&destination=${this.tripData.latitude},${this.tripData.longitude}`;
      let url = `https://www.google.com/maps/dir/?api=1&travelmode=driving&layer=traffic&destination=${this.tripData.lat},${this.tripData.lng}`;
      if (this.detectMob()) {
        window.open(url).focus();
      } else {
        url = `https://www.google.com/maps/dir/?api=1&travelmode=driving&layer=traffic&destination=${this.tripData.lat},${this.tripData.lng}`;
        window.open(url, "_blank").focus();
      }
    },
    // Si es navegador PC abre en pagina web, si es un telefono abre en app instalada
    detectMob() {
      const toMatch = [
        /Android/i,
        /webOS/i,
        /iPhone/i,
        /iPad/i,
        /iPod/i,
        /BlackBerry/i,
        /Windows Phone/i,
      ];

      return toMatch.some((toMatchItem) => {
        return navigator.userAgent.match(toMatchItem);
      });
    },
    // Función para marcar viajes como completados
    complete() {
      let _this = this;

      frappe.confirm(
        __("Would you like to mark as completed?"),
        () => {
          frappe.call({
            method: "revelare.api.complete_trip",
            args: {
              parent: this.tripData.parent,
              name: this.tripData.name,
            },
            async: true,
            callback: function (data) {
              //   console.log(data.message);
              if (data.message) {
                frappe.show_alert(
                  {
                    indicator: "green",
                    message: __(data.message),
                  },
                  5
                );
                frappe.utils.play_sound("submit");

                // Emite evento al componente padre para recargar los datos
                _this.$emit("dataTripCompleted", _this.tripData.parent);
                _this.$forceUpdate();
              } else {
                frappe.utils.play_sound("error");
                frappe.msgprint(data.message);
                // Emite evento al componente padre para recargar los datos
                _this.$emit("dataTripCompleted", _this.tripData.parent);
                _this.$forceUpdate();
              }
            },
          });
        },
        () => {
          // action to perform if No is selected
        }
      );
      //   this.$emit("dataTripCompleted", this.tripData.parent);
      this.$forceUpdate();
    },
    // Vuelve activar X viaje
    undo() {
      let _this = this;

      frappe.confirm(
        __("You are sure to activate the trip again?"),
        () => {
          frappe.call({
            method: "revelare.api.undo_status_trip",
            args: {
              parent: this.tripData.parent,
              name: this.tripData.name,
            },
            async: true,
            callback: function (data) {
              if (data.message) {
                // Si hay respuesta
                frappe.show_alert(
                  {
                    indicator: "green",
                    message: __(data.message),
                  },
                  5
                );
                // frappe.utils.play_sound("submit");
                frappe.utils.play_sound("click");
                // Emite evento al componente padre para recargar los datos
                _this.$emit("dataTripCompleted", _this.tripData.parent);
                _this.$forceUpdate();
              } else {
                frappe.utils.play_sound("error");
                frappe.msgprint(data.message);
                // Emite evento al componente padre para recargar los datos
                _this.$emit("dataTripCompleted", _this.tripData.parent);
                _this.$forceUpdate();
              }
            },
          });
        },
        () => {
          // action to perform if No is selected
        }
      );
      //   this.$emit("dataTripCompleted", this.tripData.parent);
      this.$forceUpdate();
    },
    // Retorna la diferencia en minutos entre dos fechastiempo
    diff_minutes(dt2, dt1) {
      // NOTA: Es necesario que las fechas sean de tipo Date
      let diff = (dt2 - dt1) / 1000;
      diff /= 60;
      let minutes = Math.abs(Math.round(diff));
      //   console.log(minutes);
      return minutes;
    },
    // Actualizador de comentarios
    updateComment() {
      let _this = this;

      // Actualiza el comentario en la tabla hija de Errand Trip
      frappe.call({
        method: "revelare.api.update_driver_comment",
        args: {
          parent: this.tripData.parent,
          name: this.tripData.name,
          comment: this.tripData.driver_comment,
        },
        async: true,
        callback: function (data) {
          if (data.message) {
            frappe.show_alert(
              {
                indicator: "green",
                message: __(data.message),
              },
              3
            );
            // frappe.utils.play_sound("email");
            frappe.utils.play_sound("click");

            _this.$forceUpdate();
          } else {
            frappe.utils.play_sound("error");
            frappe.msgprint(data.message);

            _this.$forceUpdate();
          }
        },
      });
    },
    // Redirecciona al Errand Trip Origen
    errandTrip() {
      //   Forma 1: abre en la misma página
      //   frappe.set_route("Form", "Errand Trip", this.tripData.parent);

      // Forma 2: abre en una nueva página
      window.open(`/app/errand-trip/${this.tripData.parent}`);
    },
  },
  // En caché
  computed: {
    cardStyle: function () {
      // Si es Pendiente: Si hay 30 minutos o menos a la fecha requeridad y esta activo,
      // la tarjeta toma el color amarillo
      if (
        this.tripData.status === "Active" &&
        this.diff_minutes(
          new Date(this.tripData.requested_time),
          new Date(frappe.datetime.now_datetime())
        ) <= 30
      ) {
        // console.log("pendiente");
        this.statusCard = "Pending";
        this.tripData.status = "Pending";
        return "card shs-bg-warning";
      }

      // Activo: Si la fecha y tiempo es menor a la fecha hora requeridad y esta activo,
      // la tarjeta toma el color verde
      if (
        this.tripData.status === "Active" &&
        frappe.datetime.now_datetime() <= this.tripData.requested_time
      ) {
        // console.log("activo");
        this.statusCard = "Active";
        this.tripData.status = "Active";
        return "card shs-bg-active";
      }

      // Atraso: Si la fecha y tiempo es mayor a la fecha hora requeridad y esta activo,
      // la tarjeta toma el color rojo
      if (
        this.tripData.status === "Active" &&
        frappe.datetime.now_datetime() > this.tripData.requested_time
      ) {
        // console.log("atrasado");
        this.statusCard = "Overdue";
        this.tripData.status = "Overdue";
        return "card shs-bg-danger";
      }

      // Completado: Si el status es Completed y ya hay una fecha en actual_arrival,
      // la tarjeta toma el color gris
      if (
        this.tripData.status === "Completed" &&
        this.tripData.actual_arrival
      ) {
        // console.log("completado");
        this.statusCard = "Completed";
        this.tripData.status = "Completed";
        return "card shs-bg-completed";
      }

      // Si no se cumple ninguna condicion se pone en color rojo, para darle atencion
      this.statusCard = "Overdue";
      this.tripData.status = "Overdue";
      return "card shs-bg-danger";
    },
    badgeStyle: function () {
      if (this.statusCard === "Active") {
        return "badge badge-success d-sm-inline-block d-none";
      } else if (this.statusCard === "Overdue") {
        return "badge badge-danger d-sm-inline-block d-none";
      } else if (this.statusCard === "Pending") {
        return "badge badge-warning d-sm-inline-block d-none";
      } else if (this.statusCard === "Completed") {
        return "badge shs-badge-dark d-sm-inline-block d-none";
      } else {
        return "badge shs-badge-dark d-sm-inline-block d-none";
      }
    },
  },
};
</script>

<style scoped>
input[type="text"] {
  background: transparent;
  border: none;
}
</style>