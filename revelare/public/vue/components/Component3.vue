<template>
  <div class="parent3">
  <h4>Adding a Grid to the page</h4>
  <div class="grid-container">
  <div class="grid-item">1</div>
  <div class="grid-item">2</div>
  <div class="grid-item">3</div>  
  <div class="grid-item">4</div>
  <div class="grid-item">5</div>
  <div class="grid-item">6</div>  
  <div class="grid-item">7</div>
  <div class="grid-item">8</div>
  <div class="grid-item">9</div>  
</div>
  </div>
</template>

<script>
export default {
  props: ["count"],
  data: function() {
    return {
      count: 0
    };
  }
  /*
  data: function() frappe.call({
            method: "milconnect.api_ach.ach_payment_entry_generator",
            args: {
                docname: frm.doc.name,
            },
            callback: function (r) {
                // console.log(r.message);
                if (r.message[0]) {
                    // window.open("/api/method/milconnect.api_ach.download_habilita_ach");
                    var file_url = r.message[1];
                    if (file_url) {
                        file_url = file_url.replace(/#/g, "%23");
                    }
                    window.open(file_url);
                }
            },
        }); */
};
</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: auto auto auto;
  background-color: #2196F3;
  padding: 10px;
}
.grid-item {
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.8);
  padding: 20px;
  font-size: 30px;
  text-align: center;
}
</style>