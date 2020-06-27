<template>
  <div>
    {{ some_data }}
    <br />
    <PlotlyGraph :count="1"></PlotlyGraph>
    <br>
  </div>
</template>


<script>
import ButtonCounter from "../vue/ButtonCounter.vue";
import PlotlyGraph from "../vue/PlotlyGraph.vue";

// Works great!
console.log("VUE Component ToolRoot Loaded");
export default {
  name: "ToolRoot",
  data: function() {
    return {
      some_data:
        "This cool button was loaded using Vue components on Revelare App"
    };
  },
  components: {
    ButtonCounter,
    PlotlyGraph
  }
};
</script>