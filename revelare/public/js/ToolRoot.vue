<template>
  <div>
    {{ some_data }}
    <br />
    <ButtonCounter :count="50"></ButtonCounter>
  </div>
</template>

<script>
import ButtonCounter from "./ButtonCounter.vue";

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