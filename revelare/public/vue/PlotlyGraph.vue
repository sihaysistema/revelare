<template>
  <button v-on:click="count++">Button1 — {{ count }}</button>
  <!-- Seems like a VUE component is an HTML page, trying a comment out-->
</template>
<!-- Seems like a VUE component is an HTML page, trying a comment out-->


<script>
// Works great!
console.log("VUE Component Button1 Loaded");
export default {
  props: ["count"],
  data: function() {
    return {
      count: 0
    };
  }
};

</script>