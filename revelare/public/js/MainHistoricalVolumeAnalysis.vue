<template>
  <div>
    <div class="project-nav">
      <div class="card-action card-tabs mr-auto">
        <ul class="nav nav-tabs align-items-center">
          <!-- Check -->
          <li class="nav-item">
            <div class="form-check mr-2">
              <input
                class="form-check-input"
                type="checkbox"
                value=""
                id="isSalesItem"
                v-model="is_sales_item"
                @change="getItems"
              />
              <label class="form-check-label" for="isSalesItem">
                {{ __("Is Sales Item?") }}
              </label>
            </div>
          </li>

          <!-- Items -->
          <li class="nav-item" v-if="is_sales_item">
            <select class="custom-select mr-1" id="item" v-model="itemSelected">
              <option selected></option>
              <option
                v-for="itemOK in itemSelect"
                :key="itemOK.name"
                :value="itemOK.name"
              >
                <span class="align-top">{{ itemOK.name }}</span>
                :
                <span class="text-muted align-bottom">{{
                  itemOK.item_name
                }}</span>
              </option>
            </select>
          </li>

          <!-- Selección de company-->
          <li class="nav-item">
            <select
              class="custom-select mr-1"
              id="compa"
              v-model="companySelected"
            >
              <option selected>{{ companies[0] }}</option>
              <option
                v-for="companyOk in companies.slice(1, companies.length)"
                :key="companyOk"
                :value="companyOk"
              >
                {{ companyOk }}
              </option>
            </select>
          </li>

          <!-- Selección de año -->
          <li class="nav-item">
            <select class="custom-select mr-1" id="year" v-model="yearSelected">
              <option selected>{{ fiscalYears[0] }}</option>
              <option
                v-for="fiscal_year in fiscalYears.slice(1, fiscalYears.length)"
                :key="fiscal_year"
                :value="fiscal_year"
              >
                {{ fiscal_year }}
              </option>
            </select>
          </li>

          <li class="nav-item">
            <button type="button" class="btn btn-primary" @click="getData()">
              {{ __("Get Data") }}
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- DIVISION -->

    <h3>Semanal</h3>
    <div id="chart"></div>

    <code class="mt-4">
      {{ datosBackend }}
    </code>
  </div>
</template>

<script>
export default {
  name: "MainHistoricalVolumeAnalysis",
  data() {
    return {
      dd: {
        labels: [
          __("1"),
          __("2"),
          __("3"),
          __("4"),
          __("5"),
          __("6"),
          __("7"),
          __("8"),
          __("9"),
          __("10"),
          __("11"),
          __("12"),
          __("13"),
          __("14"),
          __("15"),
          __("16"),
          __("17"),
          __("18"),
          __("19"),
          __("20"),
          __("21"),
          __("22"),
          __("23"),
          __("24"),
          __("25"),
          __("26"),
          __("27"),
          __("28"),
          __("29"),
          __("30"),
          __("31"),
          __("32"),
          __("33"),
          __("34"),
          __("35"),
          __("36"),
          __("37"),
          __("38"),
          __("39"),
          __("40"),
          __("41"),
          __("42"),
          __("43"),
          __("44"),
          __("45"),
          __("46"),
          __("47"),
          __("48"),
          __("49"),
          __("50"),
          __("51"),
          __("52"),
          __("53"),
        ],
        datasets: [
          // DATASET #0: VALOR DE AÑO EN CURSO
          {
            name: "Current",
            values: [
              11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
              27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
              43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
              59, 60, 61, 62, 63,
            ],
          },
          // DATASET #1: VALOR MAX
          {
            name: "Maximum",
            values: [
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
              32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
              48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
              64, 65, 66, 67, 68,
            ],
          },
          // DATASET #2: VALOR PROMEDIO
          {
            name: "Average",
            values: [
              6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
              23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
              39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54,
              55, 56, 57, 58,
            ],
          },
          // DATASET #3: VALOR MIN
          {
            name: "Minimum",
            values: [
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
              20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
              36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
              52, 53,
            ],
          },
        ], // Valores default para graficas
      },
      datosBackend: {},
      is_sales_item: false,
      companies: [],
      fiscalYears: [],
      itemSelect: [],
      companySelected: "",
      yearSelected: "",
      itemSelected: "",
    };
  },
  mounted() {
    // _this.$forceUpdate();

    let _this = this;

    frappe.call({
      freeze: true,
      freeze_message: __("Obteniendo datos..."),
      method: "revelare.api.get_data_to_select",
      async: true,
      callback: function (data) {
        _this.companies = data.message[0];
        _this.companySelected = data.message[0][0];

        _this.fiscalYears = data.message[1];
        _this.yearSelected = data.message[1][0];

        console.log(data.message);
      },
    });

    new frappe.Chart("#chart", {
      data: this.dd,
      type: "line",
      height: 350,
      animate: 1,
      lineOptions: {
        hideDots: 1, // default: 0
      },
      // COLORES: 0: datos de año en curso, 1: max, 2: promedio, 3: min
      colors: ["#004C99", "#FF0000", "#FF0000", "#FF0000"],
    });
  },
  methods: {
    getData() {
      let _this = this;
      const filters = {
        company: this.companySelected,
        item: this.itemSelected,
        year: this.yearSelected,
      };

      console.log(filters);

      frappe.call({
        args: {
          filters,
        },
        freeze: true,
        freeze_message: __("Obteniendo datos..."),
        method:
          "revelare.revelare.report.historical_weekly_item_amounts.historical_weekly_item_amounts.get_data_",
        async: true,
        callback: function (data) {
          _this.datosBackend = data.message;

          console.log(data.message);
        },
      });
    },
    getItems(e) {
      // Si se marca el checkbox
      if (e.target.checked) {
        console.log("Obteniendo items...");
        let _this = this;

        frappe.call({
          freeze: true,
          freeze_message: __("Obteniendo items..."),
          method: "revelare.api.get_items",
          async: true,
          callback: function (data) {
            _this.itemSelect = data.message;

            console.log(data.message);
          },
        });
      } else {
        this.itemSelected = "";
      }
    },
  },
};
</script>

<style scoped>
.custom-select {
  width: auto !important;
  border: none !important;
  font-size: 11pt !important;
}
.custom-select option {
  font-size: 11pt !important;
}

.project-nav {
  display: inline-block;
  vertical-align: middle;
}
</style>