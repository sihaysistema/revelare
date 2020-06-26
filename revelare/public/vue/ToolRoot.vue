<template>
  <div>
    {{ some_data }}
    <br />
    <ButtonCounter :count="10"></ButtonCounter>
  </div>
</template>

<script>
import ButtonCounter from "../vue/ButtonCounter.vue";
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
    ButtonCounter
  }
};
</script>