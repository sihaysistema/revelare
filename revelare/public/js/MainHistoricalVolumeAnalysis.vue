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
                @change="getItems" />
              <label class="form-check-label" for="isSalesItem">
                {{ __("Is Sales Item?") }}
              </label>
            </div>
          </li>

          <!-- Items -->
          <li class="nav-item" v-if="is_sales_item">
            <select class="custom-select mr-1" id="item" v-model="itemSelected">
              <option selected></option>
              <option v-for="itemOK in itemSelect" :key="itemOK.name" :value="itemOK.name">
                <span class="align-top">{{ itemOK.name }}</span>
                :
                <span class="text-muted align-bottom">{{ itemOK.item_name }}</span>
              </option>
            </select>
          </li>

          <!-- Selección de company-->
          <li class="nav-item">
            <select class="custom-select mr-1" id="compa" v-model="companySelected">
              <option selected>{{ companies[0] }}</option>
              <option v-for="companyOk in companies.slice(1, companies.length)" :key="companyOk" :value="companyOk">
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
                :value="fiscal_year">
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

    <div class="container mt-4">
      <!-- DIVISION -->
      <div v-for="item in configured_item" :key="item.name">
        <h3>{{ item.item_code }}:{{ item.item_name }}</h3>
        <div :id="`chart-${item.name}`"></div>
      </div>
      <div class="d-flex justify-content-center" v-if="show_buttom">
        <button type="button" class="btn btn-primary alihtcenter mt-3 mb-4" @click="get_configured_item()">
          {{ __("Get More Data Items") }}
        </button>
      </div>
    </div>

    <!-- <code class="mt-4">
      {{ datosBackend }}
    </code> -->
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
              11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
              39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
            ],
          },
          // DATASET #1: VALOR MAX
          {
            name: "Maximum",
            values: [
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
              44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
            ],
          },
          // DATASET #2: VALOR PROMEDIO
          {
            name: "Average",
            values: [
              6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
              35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
            ],
          },
          // DATASET #3: VALOR MIN
          {
            name: "Minimum",
            values: [
              1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
              31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
            ],
          },
        ], // Valores default para graficas,
      },
      datosBackend: {},
      is_sales_item: false,
      companies: [],
      fiscalYears: [],
      itemSelect: [],
      companySelected: "",
      yearSelected: "",
      itemSelected: "",
      configured_item: [],
      len_items: 0,
      items: [],
      start_item: 0,
      end_item: 4,
      show_buttom: true,
    };
  },
  mounted() {
    let _this = this;

    // Obtenemos los items configurados
    this.get_configured_item();
  },
  methods: {
    getData() {
      let _this = this;
      let is_item_s = this.is_sales_item ? 1 : 0;
      let item_selec = this.itemSelected;

      const filters = {
        company: this.companySelected,
        item_selected: item_selec,
        is_sales_item: is_item_s,
        year_selected: this.yearSelected,
        year: "2017",
      };

      //console.log(`${JSON.parse(filters)}`);

      frappe.call({
        args: {
          filters,
        },
        freeze: true,
        freeze_message: __("Obteniendo datos..."),
        method: "revelare.revelare.report.historical_weekly_item_amounts.historical_weekly_item_amounts.get_data",
        async: false,
        callback: function (data) {
          _this.datosBackend = data.message;
          _this.dd.labels = data.message[0].labels;
          _this.dd.datasets[0].values = data.message[0].values;
          _this.dd.datasets[1].values = data.message[0].value1;
          _this.dd.datasets[2].values = data.message[0].value2;
          _this.dd.datasets[3].values = data.message[0].value3;

          new frappe.Chart("#chart", {
            data: _this.dd,
            type: "line",
            height: 350,
            animate: 1,
            lineOptions: {
              hideDots: 1, // default: 0
            },
            // COLORES: 0: datos de año en curso, 1: max, 2: promedio, 3: min
            colors: ["#004C99", "#FF0000", "#FF0000", "#FF0000"],
          });
          //console.log(_this.dd.datasets);
          //console.log(data.message);
          _this.$forceUpdate();
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
    get_configured_item() {
      let _this = this;
      // R: Obtenemos el numero tal de items, y  la lista de los items a buscar
      this.get_len_items();
      // R: Si existen items para agregar al reporte iteramos
      if (this.len_items > 0) {
        // R: Agregue dos variables para ir recorriendo el array solo para esos items que hagan falta
        for (let i = this.start_item; i <= this.end_item; i++) {
          // R: Cuando el aumento de las variables llegue a ser mayor o igual que el tamaño de la lista de items, no ejecutamos nada
          // if (i >= this.len_items) {
          if (i >= 15) {
            this.show_buttom = false;
            console.log(this.show_buttom);
            break;
          }

          // R: Obtenemos el reporte por cada item que le pasemos por medio de la funció*n
          this.get_report(this.items[i].name);
          this.configured_item.push(this.items[i]);
        }
        console.log(this.configured_item);
        // R: Aumentamos las variables que recorren la lista de items
        this.start_item += 5;
        this.end_item = this.start_item + 4;
        this.$forceUpdate();
      }

      // Obtenemos los items configurados
      /*
      frappe.call({
        args: {
          qty: this.counter,
        },
        freeze: true,
        freeze_message: __("Obteniendo items configurados..."),
        method:
          "revelare.revelare.report.historical_weekly_item_amounts.queries.get_configured_item",
        async: false, // M: se pone en falso, ya que si se deja en true no corre serialmente con el flujo de ejecucion por eso no se obtiene la data correcta
        callback: function (data) {
          _this.configured_item = [];
          _this.configured_item = data.message;
          _this.$forceUpdate();
        },
      });*/

      //this.get_report();
    },
    get_report(item) {
      let _this = this;

      var data_ = {
        labels: [],
        datasets: [
          // DATASET #0: VALOR DE AÑO EN CURSO
          {
            name: "Current",
            values: [],
          },
          // DATASET #1: VALOR MAX
          {
            name: "Maximum",
            values: [],
          },
          // DATASET #2: VALOR PROMEDIO
          {
            name: "Average",
            values: [],
          },
          // DATASET #3: VALOR MIN
          {
            name: "Minimum",
            values: [],
          },
        ], // Valores default para graficas
        title: "",
      };

      let is_item_s = 0;

      var filters = {
        company: this.companySelected,
        item_selected: item,
        is_sales_item: is_item_s,
        year_selected: this.yearSelected,
        year: "2017",
      };

      frappe.call({
        args: {
          filters,
        },
        freeze: true,
        freeze_message: __("Obteniendo datos..."),
        method: "revelare.revelare.report.historical_weekly_item_amounts.historical_weekly_item_amounts.get_data",
        async: false,
        callback: function (data) {
          _this.$forceUpdate();
          data_.labels = data.message[0].labels;
          data_.datasets[0].values = data.message[0].values;
          data_.datasets[1].values = data.message[0].value1;
          data_.datasets[2].values = data.message[0].value2;
          data_.datasets[3].values = data.message[0].value3;
          setTimeout(() => {
            new frappe.Chart(`#chart-${item}`, {
              data: data_,
              title: `${data.message[0].UOM}`,
              type: "line",
              height: 350,
              animate: 1,
              lineOptions: {
                hideDots: 1, // default: 0
              },
              // COLORES: 0: datos de año en curso, 1: max, 2: promedio, 3: min
              colors: ["#004C99", "#FF0000", "#FF0000", "#FF0000"],
            });
          }, 0);
          _this.$forceUpdate();
        },
      });
    },
    get_len_items() {
      let _this = this;
      frappe.call({
        args: {
          //   filters,
        },
        freeze: true,
        async: false,
        freeze_message: __("Obteniendo datos..."),
        method: "revelare.revelare.report.historical_weekly_item_amounts.queries.get_qty_element",
        callback: function (data) {
          _this.len_items = data.message.qty;
          _this.items = data.message.items;
          //_this.items = _this.items.json()
          //console.log(_this.items)
        },
      });
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