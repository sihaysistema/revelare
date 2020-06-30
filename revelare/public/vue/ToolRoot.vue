<template>
  <div class="graph-canvas">
    <h3>{{ some_data }}</h3>
    <component1 :count="1"></component1>
    <Component2 :count="10"></Component2>
    <Component3></Component3>
    <Component5></Component5>
  </div>
</template>


<script>
// Local registration in a module system:
// Source: https://vuejs.org/v2/guide/components-registration.html#Local-Registration-in-a-Module-System
import Component1 from "../vue/components/Component1.vue";
import Component2 from "../vue/components/Component2.vue";
import Component3 from "../vue/components/Component3.vue";
import Component5 from "../vue/components/Component5.vue";

// Works great!
console.log("VUE Component ToolRoot Loaded");
export default {
  name: "ToolRoot",
  data: function() {
    return {
      some_data:
        "These buttons were loaded as 2 different Single File Vue components on Revelare App"
    };
  },
  components: {
    Component1,
    Component2,
    Component3,
    Component5
  }
};
</script>